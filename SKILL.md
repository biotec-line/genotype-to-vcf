# Genotype-to-VCF Pro — Product Skill

**Product:** Genotype-to-VCF Pro (`genotype-to-vcf`)
**Version:** 1.0.3
**Interface:** PySide6 desktop GUI + headless CLI (`Make23toVCF3.py` / `genotype-to-vcf`) + static browser-local preflight (`docs/browser-local-demo/`)
**License:** MIT

## Purpose & Boundaries

Converts 4-column Direct-to-Consumer (DTC) DNA genotype raw data files (`rsid`, `chromosome`, `position`, `genotype` in TSV or CSV/semicolon-CSV, e.g. 23andMe, Genes for Good, Mapmygenome, MyHeritage, FamilyTreeDNA, tellmeGen) into **VCF 4.2** files.

**Does NOT do:**
- Clinical interpretation, risk scoring, trait reporting, or medical advice (not a medical device).
- Illumina IDAT/GTC array conversion or 5-column AncestryDNA exports (detected and flagged in `--preflight`).
- Cloud upload of raw genotypes or VCF outputs.

**Network / Privacy Boundary:**
- `--preflight [--json]` and `docs/browser-local-demo/` are **100% zero-network** and never read or create `cache.json`, query NCBI, or emit file paths / personal rsIDs.
- Automatic build detection (`--build Auto`) queries NCBI dbSNP for up to the first 200 input rsIDs (without sending allele calls or raw files).
- Without a local FASTA + `.fai` index, uncached rsIDs are queried against NCBI dbSNP for reference base lookup.
- For fully offline conversion, pass an explicit `--build GRCh37` or `--build GRCh38` and provide a local FASTA reference (`--fasta <path>` or in the working folder).

## Prerequisites & Installation

- Python **3.10+** (`pyfaidx>=0.7.0`, `requests>=2.33.1`, `psutil>=5.9.0`; `PySide6>=6.5.0` required for desktop GUI, optional for headless Linux/macOS CLI execution)

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
# Optional editable install for the `genotype-to-vcf` console command:
python -m pip install -e . --no-deps
```

## CLI Usage (Deterministic Assistant Calls)

Entrypoint: `python Make23toVCF3.py [options]` (or `genotype-to-vcf [options]` when installed)

| Flag | Values / Default | Description |
|---|---|---|
| `--input` | `<path>` | Input genotype file (`.txt`/`.csv`/`.tsv`). Required unless `--version`, `--gui`, or no arguments are passed. |
| `--output` | `<path>` | Output VCF 4.2 file path (written atomically via temp file + `os.replace`; must not alias input, cache, or FASTA). |
| `--build` | `Auto` (default), `GRCh37`, `GRCh38`, `hg19`, `hg38` | Genome build (case-insensitive). |
| `--sex` | `Auto` (default), `female`, `male` | Biological sex for X/Y/PAR ploidy rules (case-insensitive). |
| `--fasta` | `<path>` | Optional explicit reference FASTA path (`.fa`/`.fasta`) outside the application folder (auto-builds `.fai` if absent; protected from `--output` overwrite). |
| `--cache` | `<path>` | Optional custom `cache.json` path for read-only / workstation environments (protected from `--output` overwrite). |
| `--preflight` | flag | Run local, zero-network 4-column structural preflight without touching `cache.json`, FASTA, or NCBI APIs. |
| `--json` | flag | Emit structured JSON summary for `--preflight` (omits file paths and personal rsIDs/genotypes). |
| `--detect-build` | flag | Detect genome build only and print `GRCh37` or `GRCh38` to stdout without writing a VCF. |
| `--version` | flag | Print `Genotype-to-VCF Pro 1.0.3` and exit with code `0`. |
| `--gui` | flag | Launch desktop GUI explicitly. |

### Examples

```bash
# Check version
python Make23toVCF3.py --version

# Run local zero-network structural preflight (JSON for assistant readback)
python Make23toVCF3.py --input sample.tsv --preflight --json

# Detect genome build only
python Make23toVCF3.py --input sample.tsv --detect-build

# Convert headless offline on Linux/macOS/Windows with explicit FASTA & cache paths
python Make23toVCF3.py --input sample.tsv --build GRCh38 --sex female --fasta /data/ref/GRCh38.fa --cache ~/.cache/genotype-to-vcf/cache.json --output out.vcf

# Launch desktop GUI
python Make23toVCF3.py --gui
```

## Exit Codes, Output & Verification

- `0`: Conversion, `--detect-build`, `--version`, or compatible `--preflight` succeeded (`VCF geschrieben.`, detected build, version string, or privacy-safe preflight summary on stdout; CLI omits file paths and personal variant calls from stdout).
- `1`: Incompatible `--preflight` (`0` valid 4-column rows), missing GUI runtime when `--gui` is requested on display-free hosts, runtime/validation failure, or aborted conversion (error message printed to stderr; existing target VCF is preserved untouched).
- `2`: Invalid CLI arguments (e.g. missing `--input` in headless mode).

Verification commands:
```bash
python -m pytest -q
python tests/source_platform_smoke.py
python manage_translations.py --check
node --test tests/test_browser_local_demo.mjs
```

## Related Documentation

- [llms.txt](llms.txt) — Machine-readable repository entrypoint and file map
- [README.md](README.md) / [README_de.md](README_de.md) — User documentation (EN / DE)
- [VCF_OUTPUT_SAFETY.md](VCF_OUTPUT_SAFETY.md) — Atomic VCF write and path-safety guarantees
- [SECURITY.md](SECURITY.md) — Responsible disclosure and privacy notes
