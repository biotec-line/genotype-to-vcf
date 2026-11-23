# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed / Review-Nachsorge zu #12 (2026-11-23)
- **`--cache` überschreibt keine Nutzerdateien mehr:** Neuer `_validate_cache_path()` blockiert `--cache` auf `--input`, `--output`, `--fasta` (inkl. `.fai`/`.gz`), konfigurierte Referenzen und den Programmcode (inkl. Symlink/Hardlink-Aliasse). `load_cache(..., strict=True)` überschreibt nur noch vorhandene Dateien im rsID-Cache-Schema (`{"rs…": {"assemblies": {…}}}`); leere, Nicht-JSON- oder fremde JSON-Dateien werden abgelehnt.
- **Pfadfreie Fehlerausgabe:** `atomic_write_json()` meldet Schreibfehler ohne Zielpfad auf `stderr`, damit `--detect-build`-stdout maschinenlesbar bleibt; CLI-Dateifehler (`OSError`, z. B. fehlende Eingabe) werden ohne Pfad gemeldet.
- **Browser-Preflight im Gleichlauf:** `docs/browser-local-demo/demo.mjs` überspringt leere Genotypen ebenfalls (`skippedEmptyGenotype`).
- **`--preflight --json` gehärtet:** Nicht-kanonische Chromosomenwerte werden als `other` gezählt (keine freien Spalteninhalte auf stdout), leere Genotypen zählen nicht mehr als gültig (`skipped_empty_genotype`).
- **CLI-Kombinationen:** `--json` ohne `--preflight` sowie `--preflight` mit `--output`/`--detect-build` enden mit `parser.error()` (Exit 2).

### Added / Multi-Target & Workstation CLI (2026-11-23)
- **Headless Linux/macOS Workstation CLI (`Make23toVCF3.py`, `pyproject.toml`):** Made `PySide6` and `psutil` optional at module import time so headless CLI workflows (`--input`, `--detect-build`, `--preflight`, `--version`) run cleanly on display-free Linux/macOS servers and containers without `libEGL.so.1` (returning exit code `1` with an actionable diagnostic only when `--gui` or zero-arg GUI launch is requested). Added `--preflight [--json]` (zero-network 4-column structural validation without file-path or rsID output), `--fasta <path>` and `--cache <path>` (with `_validate_vcf_output` overwrite protection and parent-directory creation), `--version`, numerical DTC chromosome normalization (`23/25->X`, `24->Y`, `26->MT`) in `parse_genotype_file` / `_write_vcf_atomic`, `[project.scripts] genotype-to-vcf = "Make23toVCF3:main"`, and aligned `pyproject.toml` runtime dependencies with `requirements.txt` (`psutil>=5.9.0`, `requests>=2.33.1`).
- **6-Language Zero-Egress Browser Preflight (`docs/browser-local-demo/`):** Added full Tier-2 6-language support (`de`, `en`, `es`, `zh`, `ja`, `ru`) with an accessible `#lang-select` switcher, strict `Content-Security-Policy` (`default-src 'none'; connect-src 'none'`), quote-aware semicolon-CSV (`;`) parsing, numerical DTC chromosome mapping (`23..26`), extended header recognition (`rs_id`, `marker_id`, `snp_name`, `variant_id`), specific 5-column AncestryDNA layout diagnostics, no-call counting (`--`/`-`/`00`), and 2 MiB newline-aligned file sampling so multi-megabyte raw exports stay responsive in the browser.
- **Cross-Platform Smoke & CI Gates (`tests/source_platform_smoke.py`, `.github/workflows/ci.yml`, `tests/test_cli_headless.py`, `tests/test_browser_local_demo.mjs`):** Expanded `source_platform_smoke.py` to 6 gates (including Qt-free subprocess smoke, `--preflight --json`, `--fasta`/`--cache`, 6-language parity, and Node demo tests) and wired `manage_translations.py --check` plus `node --test tests/test_browser_local_demo.mjs` into GitHub Actions CI across Ubuntu, macOS, and Windows.

### Added / Fixed (2026-11-22)
- Wired `translator.py` (`v1.2.0`) and `locales/translations.json` (49 keys across `de`, `en`, `es`, `zh`, `ja`, `ru`) into `Make23toVCF3.py` (`MainWindow` + `ConversionWorker`), adding a live language selector (`combo_lang`) while keeping canonical internal `itemData` values (`Auto`, `female`, `male`, `GRCh37`, `GRCh38`).
- Bundled `locales/translations.json` in `23toVCF_Pro.spec` and added `_resource_base_dir()` for PyInstaller compatibility.
- Added `--check` 6-language parity validation mode to `manage_translations.py`.
- Resolved GUI and browser-demo UX/accessibility findings: `setBuddy()`, localized `accessibleName`/`accessibleDescription`/`toolTip` metadata, keyboard navigation (`setTabOrder` + `Ctrl+O`/`Ctrl+Return`/`Escape`), WCAG AA contrast for disabled buttons (`#b5b5b5` on `#2c2c2c`) and placeholder label (`#c0c0c0`), visible `:focus`/`:focus-visible` outlines, accessible file input (`docs/browser-local-demo/demo.css`), `role="status"`/`aria-live="polite"`, and `<caption class="sr-only">` + `<th scope="col">`.
- Added `tests/test_gui_i18n_and_a11y.py` covering 6-language GUI switching, canonical `itemData` preservation, A11y metadata, QSS contrast/focus rules, and browser-demo A11y markup.

### Changed / Hygiene (2026-11-18)
- Untracked `MARKETING-LOG.txt` (`git rm --cached`) and excluded it plus agent/staging/temp artifacts in `.gitignore`.
- Standardized `pyproject.toml` to PEP 639 (`license = "MIT"` without a conflicting OSI license classifier), added `[tool.setuptools] py-modules`, and updated `[project.urls]`.
- Moved default pytest `basetemp` anchoring out of `addopts` (`pyproject.toml` / `pytest.ini`) into `conftest.py` (`config.rootpath / ".pytest_tmp"`) so runs from any working directory remain isolated.
- Replaced host-scoped build paths in `build_exe.bat`, `README.md`, `README_de.md`, and `CHANGELOG.md` with `%LOCALAPPDATA%\23tovcf_pro_build` (`LOCAL_BUILD` override preserved).
- Added P-022 LLM/agent entrypoints (`SKILL.md`, `llm.txt`), updated `llms.txt`, and added copyable LLM installation prompts to `README.md` and `README_de.md`.

## [1.0.3] - 2026-10-04

### Added / Fixed (certified from an unpushed working copy, 2026-10-04)
- Parsing: semicolon-delimited CSV exports and malformed/unclosed CSV quotes no longer abort `parse_genotype_file`; additional header names are skipped.
- Chromosome normalisation: `normalize_chrom` maps numerical DTC codes (23/25 -> X, 24 -> Y, 26 -> MT), used for sex detection, PAR and ploidy.
- Thread safety: `save_cache` and `lookup_rsid_from_cache` take the cache lock (no more `dictionary changed size during iteration`).
- i18n: `translator.py` 1.1.0 supports de/en/es/zh/ja/ru with fallback chain target -> EN -> DE -> key; `locales/translations.json` filled for all six languages.
- Tests: regression tests for the above plus a repository privacy/security contract test.

### Changed (2026-10-04)
- Minimum Python version raised from 3.8 to 3.10 (`requires-python`, classifiers, README badge/requirements) to match the versions actually tested in CI (3.10 to 3.12) and the ruff target.

### Fixed (2026-10-04)
- VCF output is now written to a private temporary file and published atomically via `os.replace`; cancellation or errors no longer overwrite an existing VCF, and the input, cache and FASTA files are protected against being chosen as output (see `VCF_OUTPUT_SAFETY.md`, PR #2).

### Repository Hygiene & Governance Hardening (2026-09-22)
- Added canonical root `NOTICE` file with copyright attribution to Lukas Geiger (c/o biotec-line / open-bricks) and detailed governance invariants (INV-LOCAL-01 through INV-SLA-10).
- Created Level 1 SBOM in `THIRD_PARTY_LICENSES.md` documenting PySide6 LGPL-3.0 dynamic linking isolation (zero copyleft contamination), unprivileged RunAsInvoker non-elevation, and full dependency inventory.
- Hardened PEP 621 `pyproject.toml` with `license-files`, expanded `[project.urls]`, pytest `--basetemp=.pytest_tmp`, and ruff lint configuration while strictly maintaining version freeze at `1.0.2` (T-20260920-167562623).
- Added multi-host cloud-sync conflict, system-wide lock (`LOCK.user.*`, `LOCK.until.*`, `LOCK.condition.*`), and local cache guards to `.gitignore`.
- Hardened GitHub Actions workflows (`ci.yml`, `stale.yml`, `welcome.yml`) with job-level `timeout-minutes`, concurrency cancellation (`cancel-in-progress: true`), and least-privilege permissions.
- Added statutory limitation of liability (§ 521 BGB Gefälligkeitsrecht) and 48-hour acknowledgment / 5-day triage Security SLA to `SECURITY.md`, `README.md`, and `README_de.md`.
- Implemented comprehensive contract test suite `tests/test_metadata.py` bringing total passing tests to 34/34 (100% green).
- Created local `MARKETING-LOG.txt` tracking positioning, target personas, and discoverability keywords.

### Discoverability & Marketing (2026-07-26)
- Added visual Shields.io badges (Python version, Pytest status 27/27 passed, VCF Standard 4.2, Privacy Local-First, LLM-Ready, MIT License) to `README.md` and `README_de.md`.
- Added GitHub Flavored Markdown (GFM) Callout Note (`> [!NOTE]`) for AI agent indexation, privacy boundaries, and offline local execution.
- Added Mermaid System Architecture & Data Flow Diagram to `README.md` and `README_de.md` visualizing the 4-column format auto-detection, build detection, sex determination, REF base resolution pipeline, and VCF 4.2 writer.
- Created standard PEP 621 `pyproject.toml` containing project metadata, keywords, dependency declarations, URLs, and Pytest configuration.
- Synchronized `llms.txt` header/footer timestamps to `2026-07-26` and updated main files list.

### Documentation / Maintenance (2026-07-24)
- Technical hygiene & maintenance check: verified git status, test suite (27 passed, 1 subtest passed), and llms.txt synchronization.
- Updated repository hygiene metadata and llms.txt Last-checked timestamp to 2026-07-24.

### Documentation / Maintenance (2026-07-22)
- Added dedicated German documentation landing page (README_de.md) and updated top-level language navigation bar ([English](README.md) | [Deutsch](README_de.md)).
- Synchronized llms.txt repository hygiene timestamp to 2026-07-22.
- Verified test suite (27/27 passed), syntax compilation, and git diff compliance.


### Build / Release
- Release-Status am 2026-07-22 geprüft: Der nach `1.0.2` gesammelte Stand bleibt bewusst unter `[Unreleased]`; es wird kein `1.0.3`-Release-Kandidat, Versions-Bump, Artefakt-Build oder Upload impliziert. Vor einer separaten Release-Freigabe sind ein frischer Windows-EXE-/SHA256SUMS-Check und die erneut dokumentierten Source-Smokes erforderlich.
- EXE neu gebaut 2026-06-01 (PyInstaller, 23toVCF_Pro.spec); 9/9 Tests grün, Smoke OK. EXE war 2026-05-01; Anlass: Make23toVCF3.py 2026-05-30.
- `build_exe.bat` nutzt nun standardmäßig `%LOCALAPPDATA%\23tovcf_pro_build` (überschreibbar per `LOCAL_BUILD`) als lokalen Build-Root außerhalb des Projektbaums und führt PyInstaller mit `--clean` aus.

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

- `PORTIERUNGSPLAN.md` wurde am 2026-07-22 als kanonische interne Plattformsteuerung wiederhergestellt; README und `AUFGABEN.txt` ergänzen ihn, ersetzen ihn aber nicht.

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
