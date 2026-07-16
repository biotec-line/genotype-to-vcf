import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import {
  analyzeText,
  parseGenotypeText,
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
