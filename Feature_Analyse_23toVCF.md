# Feature-Analyse: Genotype-to-VCF Pro Converter

**Ursprüngliche Analyse:** 02.01.2026

**Mit dem Projektstand synchronisiert:** 15.07.2026

**Analysierter Release-Stand:** `1.0.2` plus lokale, noch nicht veröffentlichte Änderungen unter `[Unreleased]`

> Diese Datei ist eine kompakte Status- und Differenzanalyse. Bedienung, vollständige Featurebeschreibung und Datenschutzdetails stehen in [README.md](README.md); die Änderungshistorie steht in [CHANGELOG.md](CHANGELOG.md). Eine Release-Entscheidung für den `[Unreleased]`-Stand ist separat als `TW-23VCF-02` / TASKPLAN #629 offen.

## Kurzbeschreibung und belastbarer Claim

Genotype-to-VCF Pro konvertiert lokale DTC-Genotyp-Exporte im kompatiblen Vier-Spalten-TSV-/CSV-Format in VCF 4.2. Der aktuelle Produktpfad umfasst eine PySide6-Desktop-GUI und eine CLI-/Headless-Schnittstelle. GRCh37/GRCh38, Build- und Geschlechtserkennung, PAR-/Ploidie-Regeln, lokaler FASTA-Zugriff, Cache und dbSNP-Fallback sind implementiert und durch Projektcode sowie Regressionstests belegt.

Der belastbare Status lautet **veröffentlichtes Open-Source-Tool in Version 1.0.2 mit späteren unveröffentlichten Verbesserungen**. Die frühere Bewertung „Production Ready (80 %)“ und „8/10“ vom 02.01.2026 war eine undokumentierte Momentaufnahme ohne messbares Abnahmemodell und wird nicht als aktueller Qualitäts-, Release- oder Produktionsclaim fortgeführt.

## Aktueller Evidenz-Snapshot

| Fläche | Belegter Stand am 15.07.2026 | Grenze |
|---|---|---|
| Hauptimplementierung | [Make23toVCF3.py](Make23toVCF3.py) umfasst **1.367 physische UTF-8-Zeilen**; `APP_VERSION = "1.0.2"` | Zeilenzahl ist eine Größenangabe, kein Qualitätsmaß |
| GUI | PySide6 mit gemeinsamem Konvertierungspfad | kein klinisch validierter Workflow |
| CLI / Headless | `--input`, `--output`, `--build`, `--sex`, `--detect-build`, optional `--gui`; GUI und CLI nutzen `run_conversion_pipeline()` | ohne lokale FASTA sind dbSNP-Netzwerkabfragen möglich |
| Eingaben | kompatible Vier-Spalten-TSV-/CSV-Exporte, darunter 23andMe-artige Formate | AncestryDNA-Fünf-Spaltenformat und abweichende Layouts sind nicht unterstützt |
| Referenzauflösung | lokale FASTA, lokaler Cache, danach NCBI-dB-SNP-Fallback | „offline-fähig“ gilt nur mit lokal ausreichender FASTA-/Cachebasis |
| Plattformen | Windows-EXE ist Hauptkanal; macOS und Linux sind als Source-Smokes dokumentiert | keine nativen macOS-/Linux-Pakete, keine Store- oder Mobile-Ziele |
| Browser | `docs/browser-local-demo/index.html` für lokalen Formatcheck und read-only Vorschau | kein VCF-Writer, kein Upload, keine Speicherung und kein Cloudprodukt |
| Release | README, Anwendung und Root-Registry führen `1.0.2`; spätere Änderungen stehen in `[Unreleased]` | nächster Release-Status ist nicht entschieden; siehe #629 |

## Funktionsmatrix

| Bereich | Status | Primäre Evidenz |
|---|---|---|
| GRCh37 / GRCh38 inklusive `hg19`-/`hg38`-Alias | implementiert und getestet | `Make23toVCF3.py`, `tests/test_cli_headless.py` |
| Automatische Build-Erkennung | implementiert | `Make23toVCF3.py`, `tests/source_platform_smoke.py` |
| Geschlechts- und PAR-/Ploidie-Behandlung | implementiert; Artefaktfälle regressionsgesichert | `Make23toVCF3.py`, `tests/test_create_vcf.py` |
| Lokale FASTA und mitochondriale Aliasauflösung | implementiert | `Make23toVCF3.py`, `tests/test_fasta_dialog.py` |
| dbSNP-Lookups, persistenter Cache und adaptive Threads | implementiert | `Make23toVCF3.py` |
| GUI sowie gemeinsamer CLI-/Headless-Pfad | implementiert | `Make23toVCF3.py`, `tests/test_cli_headless.py` |
| macOS-/Linux-Source-Smoke | am 03.06.2026 dokumentiert ausgeführt | README, `tests/source_platform_smoke.py`, CI-Workflow |
| Browserlokaler Vier-Spalten-Preflight | im lokalen Dirty-/Untracked-Scope vorhanden und im `[Unreleased]`-Block dokumentiert | `docs/browser-local-demo/`, `tests/test_browser_local_demo.mjs`, CHANGELOG |

## Grenzen und nicht belegte Fähigkeiten

- Das Tool erzeugt VCF-Dateien, interpretiert aber keine Varianten, Risiken oder klinischen Befunde und ist kein Medizinprodukt.
- Genotyp-Rohdaten bleiben lokal. Nur rsIDs können für dbSNP-Auflösung und optional Referenzdateien für den FASTA-Download das Netzwerk nutzen.
- Der Browserpfad ist bewusst nur ein lokaler Format-Preflight. Desktop-App und CLI bleiben die einzigen Konvertierungspfade.
- „Unterstützt beide Referenzgenome“ bedeutet nicht, dass Referenzdaten mitgeliefert werden; lokale FASTA-Dateien sind groß und werden nicht versioniert.
- Der frühere qualitative Vergleich mit plink, BCFtools und nicht benannten Online-Tools wird nicht weitergeführt: Er hatte keine datierten Quellen, reproduzierbaren Kriterien oder Versionsstände.

## Ursprüngliche Erweiterungsideen – heutige Einordnung

| Idee vom 02.01.2026 | Stand 15.07.2026 | Einordnung |
|---|---|---|
| AncestryDNA-Support | nicht implementiert | Fünf-Spaltenformat bleibt ausdrücklich nicht unterstützt |
| VCF-Merge | nicht implementiert | keine aktuell terminierte Projektanforderung |
| ClinVar-/dbSNP-Annotation | nicht implementiert | dbSNP wird zur Referenzauflösung genutzt, nicht als klinische Annotation |
| Genotyp-Qualitätsscores | nicht implementiert | DTC-Eingaben liefern dafür keine belastbare allgemeine Qualitätsgrundlage |

Diese vier Punkte sind historische Ideen, keine zugesagte Roadmap und keine Voraussetzung für den dokumentierten 1.0.2-Konvertierungsumfang.

## Historische Differenz zur Analyse vom 02.01.2026

- Die Größenangabe wurde von **775** auf **1.367** physische Zeilen der aktuellen Hauptdatei aktualisiert.
- CLI-/Headless-Nutzung, gemeinsamer GUI-/CLI-Konvertierungspfad, macOS-/Linux-Smokes und der browserlokale Nicht-Upload-Preflight sind später hinzugekommen.
- Die pauschale Prozent-/Sternebewertung wurde durch überprüfbare Status- und Grenzaussagen ersetzt.
- Auto-Download und Offline-Fähigkeit sind jetzt präzisiert: GUI-Download beziehungsweise lokale FASTA-/Cachebasis; Headless darf nichtinteraktiv auf dbSNP zurückfallen.
- Die ursprünglichen Erweiterungsempfehlungen sind datiert und als offene, nicht terminierte Ideen klassifiziert.

## Pflegevertrag

- Produktbedienung und vollständige Featureliste: [README.md](README.md)
- Veröffentlichte und unveröffentlichte Änderungen: [CHANGELOG.md](CHANGELOG.md)
- Projektaufgaben und Entscheidungen: lokale `AUFGABEN.txt`
- Portfolio-/Release-Stand: `.TOPICS/.SOFTWARE/releases.json`

Diese Analyse wird nur aktualisiert, wenn sich der belegte Capability- oder Claim-Rahmen ändert. Einzelne Changelog-Einträge oder Bedienhinweise werden hier nicht dupliziert.
