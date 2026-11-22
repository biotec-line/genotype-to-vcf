# Genotype-to-VCF Pro — Product Skill

**Product:** Genotype-to-VCF Pro (`genotype-to-vcf`)
**Version:** 1.0.3
**Interface:** PySide6 desktop GUI + headless CLI (`Make23toVCF3.py`)
**License:** MIT

## Purpose & Boundaries

Converts 4-column Direct-to-Consumer (DTC) DNA genotype raw data files (`rsid`, `chromosome`, `position`, `genotype` in TSV or CSV, e.g. 23andMe, Genes for Good, Mapmygenome, MyHeritage, FamilyTreeDNA, tellmeGen) into **VCF 4.2** files.

**Does NOT do:**
- Clinical interpretation, risk scoring, trait reporting, or medical advice (not a medical device).
- Illumina IDAT/GTC array conversion or 5-column AncestryDNA exports.
- Cloud upload of raw genotypes or VCF outputs.

**Network / Privacy Boundary:**
- Automatic build detection (`--build Auto`) queries NCBI dbSNP for up to the first 200 input rsIDs (without sending allele calls or raw files).
- Without a local FASTA + `.fai` index, uncached rsIDs are queried against NCBI dbSNP for reference base lookup.
- For fully offline conversion, pass an explicit `--build GRCh37` or `--build GRCh38` and provide a local FASTA reference (plus `.fai` index) in the working/FASTA folder.

## Prerequisites & Installation

- Python **3.10+** (`PySide6>=6.5.0`, `pyfaidx>=0.7.0`, `requests>=2.28.0`)

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

## CLI Usage (Deterministic Assistant Calls)

Entrypoint: `python Make23toVCF3.py [options]`

| Flag | Values / Default | Description |
|---|---|---|
| `--input` | `<path>` | Input genotype file (`.txt`/`.csv`/`.tsv`). Required unless `--gui` or no arguments are passed. |
| `--output` | `<path>` | Output VCF 4.2 file path (written atomically via temp file + `os.replace`; must not alias input, cache, or FASTA). |
| `--build` | `Auto` (default), `GRCh37`, `GRCh38`, `hg19`, `hg38` | Genome build (case-insensitive). |
| `--sex` | `Auto` (default), `female`, `male` | Biological sex for X/Y/PAR ploidy rules (case-insensitive). |
| `--detect-build` | flag | Detect genome build only and print `GRCh37` or `GRCh38` to stdout without writing a VCF. |
| `--gui` | flag | Launch desktop GUI explicitly. |

### Examples

```bash
# Detect genome build only
python Make23toVCF3.py --input sample.tsv --detect-build

# Convert headless to VCF 4.2
python Make23toVCF3.py --input sample.tsv --build GRCh37 --sex female --output out.vcf

# Launch desktop GUI
python Make23toVCF3.py --gui
```

## Exit Codes, Output & Verification

- `0`: Conversion or `--detect-build` succeeded (`VCF geschrieben.` or detected build on stdout; CLI intentionally omits file paths and variant counts from stdout).
- `1`: Runtime/validation failure or aborted conversion (error message printed to stderr; existing target VCF is preserved untouched).
- `2`: Invalid CLI arguments (e.g. missing `--input` in headless mode).

Verification commands:
```bash
python -m pytest -q
python tests/source_platform_smoke.py
node --test tests/test_browser_local_demo.mjs
```

## Related Documentation

- [llms.txt](llms.txt) — Machine-readable repository entrypoint and file map
- [README.md](README.md) / [README_de.md](README_de.md) — User documentation (EN / DE)
- [VCF_OUTPUT_SAFETY.md](VCF_OUTPUT_SAFETY.md) — Atomic VCF write and path-safety guarantees
- [SECURITY.md](SECURITY.md) — Responsible disclosure and privacy notes
