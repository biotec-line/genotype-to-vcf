const SAMPLE_TEXT = `# Synthetic local-only sample
rs12564807\t1\t734462\tAA
rs3131972\t1\t752721\tAG
"rs56116432","chrM","73","tt"
`;

export function splitCsvLine(line) {
  const fields = [];
  let current = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }
    if (char === "," && !inQuotes) {
      fields.push(current);
      current = "";
      continue;
    }
    current += char;
  }
  fields.push(current);
  return fields;
}

function normalizeChromosome(rawChromosome) {
  const upper = rawChromosome.trim().toUpperCase();
  const withoutPrefix = upper.startsWith("CHR") ? upper.slice(3) : upper;
  return withoutPrefix === "M" ? "MT" : withoutPrefix;
}

function parseLine(line) {
  const fields = line.includes("\t") ? line.split("\t") : splitCsvLine(line);
  return fields.map((field) => field.trim().replace(/^"(.*)"$/u, "$1"));
}

export function parseGenotypeText(text) {
  const result = {
    records: [],
    stats: {
      skippedBlank: 0,
      skippedComment: 0,
      skippedHeader: 0,
      skippedUnsupportedLayout: 0,
      skippedInvalidPosition: 0,
    },
  };

  const lines = text.split(/\r?\n/u);
  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      result.stats.skippedBlank += 1;
      continue;
    }
    if (line.startsWith("#")) {
      result.stats.skippedComment += 1;
      continue;
    }

    const parts = parseLine(line);
    if (parts.length !== 4) {
      result.stats.skippedUnsupportedLayout += 1;
      continue;
    }

    const [rsid, chrom, pos, genotype] = parts;
    if (["rsid", "snp", "marker", "name"].includes(rsid.toLowerCase())) {
      result.stats.skippedHeader += 1;
      continue;
    }

    if (!/^\d+$/u.test(pos)) {
      result.stats.skippedInvalidPosition += 1;
      continue;
    }

    result.records.push({
      rsid,
      chromosome: normalizeChromosome(chrom),
      position: Number.parseInt(pos, 10),
      genotype: genotype.trim().toUpperCase(),
    });
  }

  return result;
}

export function summarizeRecords(records, stats) {
  const chromosomeCounts = new Map();
  for (const record of records) {
    chromosomeCounts.set(
      record.chromosome,
      (chromosomeCounts.get(record.chromosome) ?? 0) + 1,
    );
  }

  const chromosomes = [...chromosomeCounts.entries()]
    .sort((left, right) => left[0].localeCompare(right[0], undefined, { numeric: true }))
    .slice(0, 6)
    .map(([chromosome, count]) => `${chromosome}:${count}`)
    .join(", ");

  const warnings = [];
  if (stats.skippedUnsupportedLayout > 0) {
    warnings.push(
      "Mindestens eine Zeile hatte nicht genau vier Spalten. Das deutet auf ein nicht unterstütztes Exportformat wie AncestryDNA oder auf kaputte CSV/TSV-Zeilen hin.",
    );
  }
  if (records.length === 0) {
    warnings.push("Es wurde kein kompatibler Datensatz erkannt.");
  }
  warnings.push(
    "Die Demo bleibt read-only. Für echte VCF-Erzeugung, Build-Erkennung und FASTA/dbSNP-Pfade weiter Desktop-App oder CLI nutzen.",
  );

  return {
    cards: [
      { label: "Erkannte Varianten", value: String(records.length) },
      { label: "Übersprungene Header", value: String(stats.skippedHeader) },
      { label: "Nicht unterstützte Zeilen", value: String(stats.skippedUnsupportedLayout) },
      { label: "Chromosomen-Snapshot", value: chromosomes || "—" },
    ],
    warnings,
  };
}

export function analyzeText(text) {
  const parsed = parseGenotypeText(text);
  return {
    ...parsed,
    summary: summarizeRecords(parsed.records, parsed.stats),
  };
}

function renderSummary(container, cards) {
  container.innerHTML = "";
  for (const card of cards) {
    const node = document.createElement("article");
    node.className = "summary-card";
    const value = document.createElement("strong");
    value.textContent = card.value;
    const label = document.createElement("span");
    label.textContent = card.label;
    node.append(value, label);
    container.appendChild(node);
  }
}

function renderWarnings(container, warnings) {
  container.innerHTML = "";
  for (const warning of warnings) {
    const node = document.createElement("div");
    node.className = "warning";
    node.textContent = warning;
    container.appendChild(node);
  }
}

function renderPreview(body, records) {
  body.innerHTML = "";
  if (records.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.className = "empty";
    cell.textContent = "Keine kompatiblen Vier-Spalten-Zeilen gefunden.";
    row.appendChild(cell);
    body.appendChild(row);
    return;
  }
  for (const record of records.slice(0, 12)) {
    const row = document.createElement("tr");
    for (const value of [record.rsid, record.chromosome, String(record.position), record.genotype]) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    }
    body.appendChild(row);
  }
}

function renderStatus(statusBanner, result) {
  const hasWarnings = result.stats.skippedUnsupportedLayout > 0 || result.records.length === 0;
  statusBanner.className = `status ${hasWarnings ? "warn" : "ok"}`;
  statusBanner.textContent = hasWarnings
    ? "Lokaler Check abgeschlossen: Datei ist nur teilweise oder nicht im erwarteten Vier-Spalten-Format."
    : "Lokaler Check abgeschlossen: kompatible Vier-Spalten-Zeilen erkannt, ohne Upload oder Netzverkehr.";
}

function attachDom() {
  const fileInput = document.getElementById("file-input");
  const sampleButton = document.getElementById("sample-button");
  const clearButton = document.getElementById("clear-button");
  const analyzeButton = document.getElementById("analyze-button");
  const rawInput = document.getElementById("raw-input");
  const statusBanner = document.getElementById("status-banner");
  const summary = document.getElementById("summary");
  const warnings = document.getElementById("warnings");
  const previewBody = document.getElementById("preview-body");

  const runAnalysis = () => {
    const result = analyzeText(rawInput.value);
    renderStatus(statusBanner, result);
    renderSummary(summary, result.summary.cards);
    renderWarnings(warnings, result.summary.warnings);
    renderPreview(previewBody, result.records);
  };

  analyzeButton.addEventListener("click", runAnalysis);
  sampleButton.addEventListener("click", () => {
    rawInput.value = SAMPLE_TEXT;
    runAnalysis();
  });
  clearButton.addEventListener("click", () => {
    rawInput.value = "";
    statusBanner.className = "status info";
    statusBanner.textContent = "Noch nichts geprüft.";
    summary.innerHTML = "";
    warnings.innerHTML = "";
    previewBody.innerHTML = "";
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.className = "empty";
    cell.textContent = "Noch keine Vorschau vorhanden.";
    row.appendChild(cell);
    previewBody.appendChild(row);
  });
  fileInput.addEventListener("change", async (event) => {
    const [file] = event.target.files ?? [];
    if (!file) {
      return;
    }
    rawInput.value = await file.text();
    runAnalysis();
  });
}

if (typeof document !== "undefined") {
  attachDom();
}
