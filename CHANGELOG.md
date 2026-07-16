# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Build / Release
- EXE neu gebaut 2026-06-01 (PyInstaller, 23toVCF_Pro.spec); 9/9 Tests grün, Smoke OK. EXE war 2026-05-01; Anlass: Make23toVCF3.py 2026-05-30.
- `build_exe.bat` nutzt nun standardmäßig `C:\_Local_DEV\codex_build\23tovcf_pro` als lokalen Build-Root außerhalb des OneDrive-Projektbaums und führt PyInstaller mit `--clean` aus.

### Added

- Added a static local browser demo in `docs/browser-local-demo/` for privacy-safe format preflight without uploads, server calls, or in-browser VCF generation.
- Added `tests/test_browser_local_demo.mjs` to cover CSV parsing, chromosome normalization, unsupported-layout warnings, and the summary snapshot used by the browser demo.
- Added README positioning tables and search phrases for 23andMe raw-data-to-VCF, DTC-DNA genotype conversion, MyHeritage/FamilyTreeDNA-compatible exports, and disambiguation against Illumina IDAT/GTC tools, cloud upload portals, and clinical interpretation services.
- Updated `llms.txt` with 2026-06-12 discovery notes, headless CLI framing, broader search phrases, and explicit boundaries for non-clinical local VCF conversion.
- Added `scripts/make_sha256sums.py` to generate SHA256SUMS for `dist/` artifacts before GitHub releases; `tests/test_make_sha256sums.py` covers the four core functions.
- Added Release Checklist section to README with Windows EXE + SHA256SUMS workflow and macOS/Linux source instructions.
- Added a README start-here table, top-level GUI screenshot placement, and explicit search context for 23andMe-style DTC genotype to VCF conversion.
- Added `llms.txt` with canonical repository, discovery phrases, file map, and non-medical-device boundaries for LLM and search-index readers.
- Added a real headless CLI entrypoint to `Make23toVCF3.py` with `--input`, `--output`, `--build`, `--sex`, `--detect-build`, and `--gui`.
- Added `tests/test_cli_headless.py` to cover VCF generation and build detection without launching the GUI.
- Added `tests/source_platform_smoke.py` as a reproducible macOS/Linux source smoke for headless VCF generation and `--detect-build`.

### Changed

- Narrowed `.gitignore` so `docs/browser-local-demo/` stays versioned while the rest of `docs/` remains internal-only.
- Documented the new browser-local format demo in the README and task list as a non-upload, read-only preview path rather than a public webapp product line.
- Reordered the public README so the English project overview is the default GitHub landing section and the German documentation remains available below it.
- Moved GUI and CLI runs onto the shared `run_conversion_pipeline()` path so the conversion logic is no longer split across separate execution flows.
- Documented the new CLI/headless workflow in the English and German README sections plus the platform plan and task list.
- Extended GitHub Actions with a dedicated `platform-smoke` job on Ubuntu and macOS and recorded the 2026-06-03 source-smoke results in the README/task docs.

### Fixed

- Hardened the browser-local preview against HTML injection from pasted or selected genotype text by rendering dynamic values with DOM text nodes instead of `innerHTML` templates.
- Made CLI build/sex parsing more forgiving: `--build` now accepts case-insensitive `GRCh37` / `GRCh38` plus `hg19` / `hg38` aliases, and `--sex` accepts case-insensitive `Auto` / `female` / `male`. Regression coverage was added in `tests/test_cli_headless.py`.
- Reduced CLI success output so headless conversions no longer print local
  output paths, variant counts, genome build, or sex metadata by default.
- Fixed `parse_genotype_file` encoding fallback (Bug B): files encoded in latin-1/cp1252 (some FTDNA exports) previously raised `UnicodeDecodeError`; now retries with `latin-1` after a failed `utf-8-sig` attempt. Regression test: `test_parse_genotype_file_latin1_fallback`.
- Fixed `create_vcf` i-type SNP ordering (Bug C): internal 23andMe IDs (`i...`) were silently dropped when no FASTA was present because `get_ref()` was called before the `i→rs` cache mapping, so it always returned `"N"` and triggered a `continue`. The mapping block now runs before `get_ref()`. Regression test: `test_create_vcf_i_type_snp_resolved_from_cache`.
- Fixed `create_vcf` hemizygous het-call inconsistency (Bug A): heterozygous genotypes on haploid sites (e.g. chrY outside PAR for males) produced inconsistent VCF records with `ALT="G"` but `GT="0"`. These are probe artifacts; they are now skipped. Regression tests: `test_create_vcf_hemizygous_het_call_skipped` + `test_create_vcf_hemizygous_homozygous_alt_written`.
- Fixed `manage_translations.py` so a damaged `locales/translations.json` no longer aborts the scan; the file is rebuilt from detected GUI strings instead. Regression coverage is in `tests/test_bug_regressions.py`.
- Fixed `signal_callback` None-Crash in `create_vcf`: wraps the callback in `make_signal` at function start so `signal_callback.emit()` never raises `AttributeError` when `stop_event` is set and `signal_callback=None` is passed; regression test added in `tests/test_create_vcf.py`.
- Fixed `_is_german` false positives: now checks for real UTF-8 umlauts (`äöüÄÖÜß`) instead of ASCII substitutes (`ae/oe/ue/...`), preventing false hits on English text with common trigrams; regression test added in `tests/test_translator.py`.
- Fixed the shared GUI/CLI conversion pipeline so explicit `--output` paths create missing parent folders before writing the VCF instead of failing with `Errno 2`.
- Fixed FASTA chromosome alias resolution so mitochondrial `MT` / `M` lookups can resolve against `chrM` / `chrMT` references.
- Fixed CSV genotype parsing for fully quoted provider exports and uppercase `CHR` chromosome prefixes.
- Normalized the German build-detection warning so the UI consistently uses real UTF-8 umlauts.

### Removed

- Removed `PORTIERUNGSPLAN.md`; its content is now covered by `AUFGABEN.txt` and the platform section in `README.md`.

### Repository Hygiene

- Rechecked repository privacy and Git hygiene on 2026-07-16 for the browser-local demo: no real genotype data, VCF outputs, FASTA references, caches, credentials, or build artifacts are tracked; `LOCK*.txt` remains ignored.
- Rechecked repository privacy and Git hygiene on 2026-07-02 after the CLI alias update; local genome exports, FASTA references, `cache.json`, EXE/release artifacts, internal docs, and `LOCK*.txt` remain ignored and untracked.
- Checked repository privacy and Git hygiene on 2026-06-24: local genome exports, FASTA references, `cache.json`, EXE/release artifacts, internal docs, and `LOCK*.txt` remain ignored and untracked.
- Added an explicit local-data hygiene note for ignored FASTA references, dbSNP caches, VCF outputs, and provider raw-data exports.
- Added `.gitattributes` for stable text line endings and binary handling of screenshots, icons, executables, VCF files, and FASTA references.
- Extended `.gitignore` to cover generic `.fai` FASTA index files.
- Refreshed README privacy notes to make the ignored local genome-data and build-artifact boundary explicit.

## [1.0.2] - 2026-05-01

### Build and Repository Hygiene

- Added a guarded `build_exe.bat` PyInstaller wrapper for reproducible Windows builds
- Extended `.gitignore` to keep local release folders and raw genotype exports out of Git
- Updated README build instructions to match the tracked PyInstaller spec
- Added optional pytest regression coverage for FASTA path and dialog handling
- Added a GitHub Actions CI matrix for the new regression tests
- Added `requirements-dev.txt` for local test setup and expanded test cache ignores
- Hardened `START.bat` with UTF-8 output and a Python availability check
- Bilingualized contributor and security guidance for the current GitHub repository
- Confirmed local genome data, reference FASTA files, caches, and build outputs remain untracked
- Aligned the application version constant and README with the 1.0.2 release metadata
- Fixed the reference download prompt path so worker callables and signal-like callbacks both work

## [1.0.1] - 2026-04-30

### Repository Hygiene

- Restored the current `Make23toVCF3.py` source file to the public repository
- Added the Windows launcher, PyInstaller spec, and application icon
- Updated GitHub links from `lukisch` to `biotec-line`
- Replaced direct contact email references with GitHub-native reporting paths
- Expanded `.gitignore` for genetic data, local caches, credentials, and internal coordination files
- Documented the PySide6 migration and repository contents

## [1.0.0] - 2026-02-13

### Initial Public Release

- PyQt6 GUI with dark theme
- VCF v4.2 output format
- Dual reference genome support (GRCh37 / GRCh38)
- Automatic build detection via dbSNP position validation
- Automatic sex detection from Y chromosome variants
- PAR (pseudo-autosomal region) handling for correct X/Y ploidy
- NCBI dbSNP REST API integration with persistent local cache
- Optional FASTA reference download with automatic indexing
- Adaptive multi-threading (4-200 workers, targeting 70% CPU usage)
- Indel detection and handling (I/D markers)
- Internal ID (i-prefix) to rsID mapping via cache lookup
- Compatible with 23andMe and other providers using the same TSV format
