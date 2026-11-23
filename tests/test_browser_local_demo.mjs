import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import {
  DEMO_TRANSLATIONS,
  SUPPORTED_LOCALES,
  analyzeText,
  parseGenotypeText,
  resolveDemoLocale,
  slicePreviewText,
  splitCsvLine,
  summarizeRecords,
} from "../docs/browser-local-demo/demo.mjs";

test("splitCsvLine keeps quoted commas intact", () => {
  assert.deepEqual(splitCsvLine('"rs123","chr1","123","A,G"'), [
    "rs123",
    "chr1",
    "123",
    "A,G",
  ]);
});

test("parseGenotypeText normalizes chromosome aliases and genotype casing", () => {
  const text = [
    "# comment",
    '"rs123","chr1","123","ag"',
    "rs456\tM\t73\ttt",
  ].join("\n");

  const parsed = parseGenotypeText(text);

  assert.equal(parsed.records.length, 2);
  assert.deepEqual(parsed.records[0], {
    rsid: "rs123",
    chromosome: "1",
    position: 123,
    genotype: "AG",
  });
  assert.deepEqual(parsed.records[1], {
    rsid: "rs456",
    chromosome: "MT",
    position: 73,
    genotype: "TT",
  });
  assert.equal(parsed.stats.skippedComment, 1);
});

test("analyzeText warns about unsupported layouts but still keeps valid preview rows", () => {
  const text = [
    "rsid,chromosome,position,genotype",
    "rs111,1,111,AA",
    "rs222,1,222,AG,EXTRA",
    "marker,chromosome,position,genotype",
    "rs333,2,not-a-number,TT",
  ].join("\n");

  const result = analyzeText(text);

  assert.equal(result.records.length, 1);
  assert.equal(result.stats.skippedUnsupportedLayout, 1);
  assert.equal(result.stats.skippedHeader, 2);
  assert.equal(result.stats.skippedInvalidPosition, 1);
  assert.match(result.summary.warnings[0], /nicht genau vier Spalten/u);
});

test("summarizeRecords produces a stable chromosome snapshot", () => {
  const records = [
    { rsid: "rs1", chromosome: "1", position: 1, genotype: "AA" },
    { rsid: "rs2", chromosome: "1", position: 2, genotype: "AG" },
    { rsid: "rs3", chromosome: "X", position: 3, genotype: "TT" },
  ];

  const summary = summarizeRecords(records, {
    skippedBlank: 0,
    skippedComment: 0,
    skippedHeader: 0,
    skippedUnsupportedLayout: 0,
    skippedInvalidPosition: 0,
  });

  assert.equal(summary.cards[0].value, "3");
  assert.equal(summary.cards[3].value, "1:2, X:1");
});

test("browser preview renders dynamic genotype values without innerHTML templates", () => {
  const source = readFileSync(new URL("../docs/browser-local-demo/demo.mjs", import.meta.url), "utf8");

  assert.doesNotMatch(source, /innerHTML\s*=\s*`/u);
  assert.doesNotMatch(source, /innerHTML\s*=\s*['"]<tr/u);
  assert.match(source, /textContent\s*=\s*value/u);
});

test("parseGenotypeText supports semicolon CSV, numeric DTC chromosomes, extended headers, BOM, and 5-column detection", () => {
  const text = [
    "\uFEFF# synthetic semicolon + DTC numeric chromosomes",
    "rs_id;chromosome;position;genotype",
    '"rs10";"23";"60005";"ag"',
    "rs11;24;15000;--",
    "rs12;25;100000;cc",
    "rs13;26;73;tt",
    "rs_ancestry,1,555,A,G",
  ].join("\n");

  const parsed = parseGenotypeText(text);

  assert.equal(parsed.records.length, 4);
  assert.deepEqual(
    parsed.records.map((r) => [r.rsid, r.chromosome, r.genotype]),
    [
      ["rs10", "X", "AG"],
      ["rs11", "Y", "--"],
      ["rs12", "X", "CC"],
      ["rs13", "MT", "TT"],
    ],
  );
  assert.equal(parsed.stats.skippedHeader, 1);
  assert.equal(parsed.stats.noCallRecords, 1);
  assert.equal(parsed.stats.skippedFiveColumnLayout, 1);
  assert.equal(parsed.stats.skippedUnsupportedLayout, 1);
});

test("slicePreviewText cuts multi-megabyte inputs cleanly at a newline boundary", async () => {
  const chunk = "rs1\t1\t100\tAA\nrs2\t1\t200\tAG\nrs3\t1\t300\tTT\n";
  const sliced = slicePreviewText(chunk, 28);

  assert.equal(sliced.truncated, true);
  assert.equal(sliced.text, "rs1\t1\t100\tAA\nrs2\t1\t200\tAG\n");
  const analyzed = analyzeText(sliced.text, "en", { truncated: sliced.truncated });
  assert.equal(analyzed.records.length, 2);
  assert.equal(analyzed.stats.skippedUnsupportedLayout, 0);
  assert.ok(analyzed.summary.warnings.some((w) => /sampled|first/iu.test(w)));

  // Simulate Blob.slice(0, maxBytes).text() where UTF-8 multibyte chars make rawChunk.length < maxBytes
  const fullContent =
    "# Kommentar mit Umlaut äöü\nrs10\t1\t100\tAA\nrs11\t1\t0\tCC\nrs12\t2\t400\tGG\n";
  const blob = new Blob([fullContent]);
  const maxBytes = 58; // Cuts inside the final row ("rs12\t2") while decoded JS string length < 58
  assert.ok(blob.size > maxBytes);
  const rawChunk = await blob.slice(0, maxBytes).text();
  assert.ok(rawChunk.length < maxBytes);

  const blobSliced = slicePreviewText(rawChunk, maxBytes, { forceTruncate: true });
  assert.equal(blobSliced.truncated, true);
  const blobAnalyzed = analyzeText(blobSliced.text, "de", { truncated: blobSliced.truncated });
  assert.equal(blobAnalyzed.records.length, 1);
  assert.equal(blobAnalyzed.stats.skippedUnsupportedLayout, 0);
  assert.equal(blobAnalyzed.stats.skippedInvalidPosition, 1); // position 0 rejected
});

test("six-language demo catalog has full key parity and localized summaries", () => {
  assert.deepEqual(SUPPORTED_LOCALES, ["de", "en", "es", "zh", "ja", "ru"]);
  const baseKeys = Object.keys(DEMO_TRANSLATIONS.de).sort();
  assert.ok(baseKeys.length >= 25);

  for (const locale of SUPPORTED_LOCALES) {
    assert.deepEqual(
      Object.keys(DEMO_TRANSLATIONS[locale]).sort(),
      baseKeys,
      `Key mismatch in locale ${locale}`,
    );
    for (const key of baseKeys) {
      assert.ok(
        typeof DEMO_TRANSLATIONS[locale][key] === "string" &&
          DEMO_TRANSLATIONS[locale][key].trim().length > 0,
        `Empty translation for ${locale}.${key}`,
      );
    }

    const res = analyzeText("rs1\t1\t100\tAG\nrs2,1,200,A,G\n", locale);
    assert.equal(res.summary.cards.length, 4);
    assert.ok(res.summary.warnings.length >= 2);
  }

  assert.equal(resolveDemoLocale("zh-CN"), "zh");
  assert.equal(resolveDemoLocale("es-MX"), "es");
  assert.equal(resolveDemoLocale("pt-BR", "en"), "en");
});

test("browser demo enforces zero-egress CSP, language selector A11y, and zero network APIs", () => {
  const html = readFileSync(new URL("../docs/browser-local-demo/index.html", import.meta.url), "utf8");
  const js = readFileSync(new URL("../docs/browser-local-demo/demo.mjs", import.meta.url), "utf8");

  assert.match(html, /http-equiv="Content-Security-Policy"/u);
  assert.match(html, /connect-src 'none'/u);
  assert.match(html, /for="lang-select"/u);
  assert.match(html, /id="lang-select"/u);

  assert.doesNotMatch(js, /\bfetch\s*\(/u);
  assert.doesNotMatch(js, /\bXMLHttpRequest\b/u);
  assert.doesNotMatch(js, /\bWebSocket\b/u);
  assert.doesNotMatch(js, /\bsendBeacon\b/u);
});
