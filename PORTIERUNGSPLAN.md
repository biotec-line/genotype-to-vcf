# Portierungsplan: Genotype-to-VCF Pro Converter

Stand: 2026-05-27

## Zweck und Ausgangslage

Genotype-to-VCF Pro konvertiert DTC-Genotypdaten lokal in VCF 4.2. Der fachliche Kern ist nicht eine mobile Alltags-App, sondern ein datenschutzsensibles Bioinformatik-Werkzeug für Forschung, Imputation, Archivierung und nachgelagerte Analyse.

Die aktuelle Version ist eine PySide6-Desktop-App mit Windows-EXE, Quellcode-Start, optionaler lokaler FASTA-Referenz und Fallback auf NCBI dbSNP. Große Referenzdateien, genetische Rohdaten und IVDR/MDR-Abgrenzung sprechen gegen öffentliche Upload-Webapps und gegen Mobile-Klone.

## Plattformentscheidung

| Option | Entscheidung | Begründung |
|---|---|---|
| Windows Store | Nicht aktiv verfolgen | Store-Onboarding passt schlecht zu 3-GB-Referenzen, genetischen Daten, optionalem NCBI/Ensembl-Netzwerkzugriff und enger Bioinformatik-Nische. GitHub bleibt transparenter. |
| Android | Kein nativer Klon | Mobile Geräte sind für 3-GB-FASTA, große Rohdaten und lokale VCF-Ausgaben ungeeignet. Datenschutz- und Dateizugriffsprobleme überwiegen den Nutzen. |
| Webapp | Keine öffentliche Upload-Webapp | Genetische Rohdaten dürfen nicht über einen fremden Server laufen. Später höchstens eine vollständig browserlokale Demo oder ein Validierer ohne Upload. |
| iOS | Kein nativer Klon | Dieselben Daten-, Speicher- und Dateisystemgrenzen wie Android; App-Review und medizinische Abgrenzung wären unverhältnismäßig. |
| Mac App | Sinnvoll als Source-Smoke, später optionales DMG | Viele Bioinformatik-Nutzer arbeiten auf macOS. Ein Quellcode-Start und später ein signierter Direkt-Download sind sinnvoller als App Store. |
| Linux Version | Sinnvoll als Source-Smoke, später optionales AppImage | Linux ist im Bioinformatik-Umfeld relevant. CLI/headless-Nutzung und reproduzierbare Source-Starts haben hier höheren Wert als Store-Pakete. |

## Zielbild

1. Windows bleibt der primäre Komfort-Build mit EXE und GitHub-Release.
2. macOS und Linux werden als unterstützte Workstation-Ziele über Source-Smokes dokumentiert.
3. Ein CLI/headless-Pfad wird als spätere Voraussetzung für Linux/macOS, Automatisierung und LLM-/Pipeline-Nutzung geführt.
4. Mobile und öffentliche Webapps sind Nicht-Ziele, solange genetische Rohdaten oder Referenzgenome verarbeitet werden.
5. VCF 4.2 ist bereits das portable Austauschformat; ein zusätzliches JSON-Exportformat ist aktuell nicht nötig.

## Umsetzungsstatus

| Bereich | Status | Nächster Schritt |
|---|---|---|
| Windows EXE | Vorhanden | Release-Artefakte weiter über GitHub statt Store pflegen. |
| Windows Store | Bewusst ausgeschlossen | Root-Store-Pipeline mit diesem Plan verknüpfen. |
| macOS | Geplant | Source-Smoke mit Python 3.10-3.12, PySide6 und pyfaidx dokumentieren. |
| Linux | Geplant | Source-Smoke und optionalen CLI/headless-Test definieren. |
| Android/iOS | Nicht-Ziel | Keine Tasks anlegen, außer späterer browserlokaler Demo ohne Datenupload. |
| Web | Nicht-Ziel für Uploads | Nur lokale statische Demo oder Dokumentationsseite zulassen. |

## Offene Aufgaben

- P0: README um Plattformstrategie und klare Store-/Mobile-Abgrenzung ergänzen.
- P1: macOS- und Linux-Source-Smoke definieren: Installation, Start, Testlauf und FASTA-freier dbSNP-Fallback.
- P1: CLI/headless-Konzept prüfen, damit Konvertierungen ohne GUI automatisierbar werden.
- P2: GitHub-Release-Checkliste um macOS-/Linux-Hinweise und SHA256SUMS für Windows-Artefakte erweitern.
- P3: Browserlokale Demo nur dann prüfen, wenn sie vollständig ohne Server-Upload, ohne Referenzgenom-Bundling und mit klarer Forschungsabgrenzung funktioniert.

## Nicht-Ziele

- Keine öffentliche Genotyp-Upload-Webapp.
- Keine Android-/iOS-Version mit lokalen Genomdaten als MVP.
- Keine gebündelten Referenzgenome im Repository oder Store-Paket.
- Keine klinische oder diagnostische Zweckbestimmung.
