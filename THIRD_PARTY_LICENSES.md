# Genotype-to-VCF Pro — Level 1 Software Bill of Materials (SBOM) & Third-Party Licenses

Stand: 2026-09-22
Kanonisches Repository: https://github.com/biotec-line/genotype-to-vcf
Dachorganisation: biotec-line / open-bricks
Projektlizenz: [MIT License](LICENSE)
Zentrale Attribution: [NOTICE](NOTICE)

---

## 1. Projektlizenz & Lizenz-Isolation

Der Anwendungscode von **Genotype-to-VCF Pro** (`Make23toVCF3.py`, CLI-Module, Hilfsskripte, Test-Suites) steht unter der **MIT License** (siehe [`LICENSE`](LICENSE)).

### LGPL-3.0 Dynamische Bindung & Copyleft-Isolation
Die grafische Benutzeroberfläche basiert auf **PySide6** (Qt for Python). PySide6 steht unter der **LGPL-3.0-only** bzw. GPL-2.0/3.0.
* **Dynamische Bindung**: Die Anwendung interagiert mit PySide6 ausschließlich über standardmäßige dynamische Python-Modulimporte (`import PySide6`).
* **Keine Copyleft-Kontamination**: Gemäß Ziffer 4 der GNU LGPL v3 bleibt der MIT-lizenzierte Anwendungscode vollständig unabhängig und wird durch die Nutzung von PySide6 nicht mit Copyleft belegt.
* **Austauschbarkeit**: Anwender können die PySide6-Laufzeitkomponenten im Python-Environment unabhängig aktualisieren oder austauschen.

---

## 2. Governance- & Sicherheits-Invarianten (INV-LOCAL-01 bis INV-SLA-10)

| Invariante | Bezeichnung | Spezifikation / Nachweis |
|---|---|---|
| **INV-LOCAL-01** | Local-First Privacy Boundary | Genomische Rohdaten, erzeugte VCF-Dateien und lokale Referenzindizes verbleiben strikt auf der lokalen Maschine. |
| **INV-LOCAL-02** | Unprivileged Execution | Desktop-GUI und CLI laufen unprivilegiert im Benutzerkontext (`RunAsInvoker`), keine Administratorrechte erforderlich. |
| **INV-LOCAL-03** | Zero Unsolicited Egress | Netzwerkverkehr erfolgt ausschließlich bei expliziter Nutzeraktion (dbSNP REST API für rsID-Lookups, optionaler Ensembl-Download). |
| **INV-LOCAL-04** | Non-Clinical Research Purpose | Reine Forschungs- und Entwicklungssoftware; kein Medizinprodukt im Sinne von MDR (EU) 2017/745 oder IVDR (EU) 2017/746. |
| **INV-LOCAL-05** | VCF 4.2 Standard Compliance | Vollständige Einhaltung der VCF 4.2 Spezifikation inkl. PAR1/PAR2-Ploidie- und Geschlechtschromosomen-Regeln. |
| **INV-LOCAL-06** | Tiered Reference Resolution | Drei-Stufen-Fallback: (1) Lokale indizierte FASTA, (2) Atomarer lokaler Cache (`cache.json`), (3) NCBI dbSNP REST API. |
| **INV-LOCAL-07** | Headless Automation Isolation | Vollwertige CLI-Pipeline für automatisierte, reproduzierbare Konvertierungen ohne GUI-Abhängigkeit. |
| **INV-LOCAL-08** | LGPL-3.0 Dynamic Linking Isolation | PySide6 Qt-Bindungen sind strikt dynamisch gekapselt; 100% MIT-Lizenzreinheit des Anwendungscodes. |
| **INV-LOCAL-09** | Version Freeze Discipline | Pfad-A- und Pfad-B-Läufe modifizieren gemäß T-20260920-167562623 niemals Versionsnummern. |
| **INV-LOCAL-10** | Statutory Disclaimer & SLA | Haftungsprivilegierung gem. § 521 BGB; verbindliches Sicherheits-SLA (48h Acknowledgment / 5 Werktage Triage). |

---

## 3. Direkte Laufzeit-Abhängigkeiten (Direct Runtime Dependencies)

| Paket | Spezifikation (`requirements.txt`) | Geprüfte Version | Lizenz (SPDX) | Upstream-Quelle |
|---|---|---|---|---|
| **PySide6** | `PySide6>=6.5.0` | 6.11.1 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | https://pypi.org/project/PySide6/ |
| **requests** | `requests>=2.33.1` | 2.34.2 | Apache-2.0 | https://pypi.org/project/requests/ |
| **pyfaidx** | `pyfaidx>=0.7.0` | 0.9.0.4 | BSD-3-Clause | https://pypi.org/project/pyfaidx/ |
| **psutil** | `psutil>=5.9.0` | 7.2.2 | BSD-3-Clause | https://pypi.org/project/psutil/ |

---

## 4. Qt for Python Komponenten (Installed via PySide6)

| Paket | Geprüfte Version | Lizenz (SPDX) | Upstream-Quelle |
|---|---|---|---|
| **PySide6_Addons** | 6.11.1 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | https://pypi.org/project/PySide6-Addons/ |
| **PySide6_Essentials** | 6.11.1 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | https://pypi.org/project/PySide6-Essentials/ |
| **shiboken6** | 6.11.1 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | https://pypi.org/project/shiboken6/ |

---

## 5. Transitive Laufzeitpakete (Transitive Runtime Packages)

| Paket | Geprüfte Version | Lizenz (SPDX) | Zweck / Herkunft |
|---|---|---|---|
| **certifi** | 2026.6.17 | MPL-2.0 | TLS/SSL-Zertifikatsbündel für HTTPS (via `requests`) |
| **charset-normalizer** | 3.4.7 | MIT | Zeichensatz-Erkennung für HTTP-Antworten (via `requests`) |
| **idna** | 3.18 | BSD-3-Clause | Internationalized Domain Names in Applications (via `requests`) |
| **packaging** | 26.2 | Apache-2.0 OR BSD-2-Clause | Versions- und Metadaten-Handling |
| **urllib3** | 2.7.0 | MIT | HTTP-Verbindungspooling und Transport (via `requests`) |

---

## 6. Operative Schutz- und Ausschlussregeln

1. **Ausschluss von Forschungs- und Nutzerdaten**: Genom-Rohdaten (`genome_*`), VCF-Ausgabedateien, FASTA-Referenzgenome (`*.fa`, `*.fasta`), `.fai`-Indexdateien, lokale Caches (`cache.json`), EXE-Binärdateien und Koordinationsdateien (`LOCK*.txt`) sind Daten bzw. Artefakte und verbleiben strikt gitignoriert.
2. **Paketierungs-Vorgabe**: Beim Erstellen von Standalone-Builds (z. B. via PyInstaller) sind die Upstream-Lizenztexte von PySide6 und den abhängigen Bibliotheken im Auslieferungsverzeichnis beizulegen.
3. **Audit-Zyklus**: Diese SBOM wird bei jeder Änderung an `requirements.txt` sowie im Rahmen von Pfad-A-Hygiene-Audits verifiziert.
