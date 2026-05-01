# Changelog

All notable changes to this project will be documented in this file.

## [1.0.2] - 2026-05-01

### Build and Repository Hygiene

- Added a guarded `build_exe.bat` PyInstaller wrapper for reproducible Windows builds
- Extended `.gitignore` to keep local release folders and raw genotype exports out of Git
- Updated README build instructions to match the tracked PyInstaller spec
- Bilingualized contributor and security guidance for the current GitHub repository
- Confirmed local genome data, reference FASTA files, caches, and build outputs remain untracked

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
