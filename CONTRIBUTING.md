# Contributing / Beitragen

## Deutsch

Vielen Dank für Ihr Interesse an Genotype-to-VCF Pro.

### Bugs melden

- Öffnen Sie ein [GitHub Issue](../../issues) mit einer klaren Beschreibung.
- Nennen Sie Betriebssystem, Python-Version und Fehlermeldung.
- Hängen Sie **niemals** echte Genomdaten, VCF-Dateien, FASTA-Referenzen, API-Caches oder persönliche Rohdaten an.

### Feature-Wünsche

- Öffnen Sie ein [GitHub Issue](../../issues) mit dem Label `enhancement`.
- Beschreiben Sie den Anwendungsfall und das erwartete Verhalten.

### Pull Requests

1. Forken Sie das Repository.
2. Erstellen Sie einen Feature-Branch: `git checkout -b feature/my-feature`.
3. Ändern Sie die Anwendung in `Make23toVCF3.py` oder die zugehörige Dokumentation.
4. Testen Sie ausschließlich mit synthetischen oder öffentlichen Beispieldaten.
5. Committen Sie die Änderungen mit einer klaren Commit-Nachricht.
6. Pushen Sie den Branch und öffnen Sie einen Pull Request.

### Entwicklungsstil

- Python 3.8+ kompatibel halten.
- PEP-8-Konventionen beachten.
- Die aktuelle Single-File-Anwendungsstruktur in `Make23toVCF3.py` nur bewusst aufbrechen.
- Komplexe bioinformatische Logik knapp kommentieren.
- Build-Artefakte (`build/`, `dist/`, `releases/`, `*.exe`) nicht committen.

## English

Thank you for your interest in contributing to Genotype-to-VCF Pro.

### Reporting Bugs

- Open a [GitHub Issue](../../issues) with a clear description.
- Include your operating system, Python version, and error message.
- **Never** attach real genomic data, VCF files, FASTA references, API caches, or personal raw data.

### Feature Requests

- Open a [GitHub Issue](../../issues) with the label `enhancement`.
- Describe the use case and expected behavior.

### Pull Requests

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Change the application in `Make23toVCF3.py` or the related documentation.
4. Test only with synthetic or public sample data.
5. Commit your changes with a clear commit message.
6. Push the branch and open a pull request.

### Development Style

- Keep Python 3.8+ compatibility.
- Follow PEP 8 conventions.
- Only split the current single-file application structure in `Make23toVCF3.py` deliberately.
- Add concise comments for complex bioinformatics logic.
- Do not commit build artifacts (`build/`, `dist/`, `releases/`, `*.exe`).

## Development Setup

```bash
pip install -r requirements.txt
python Make23toVCF3.py
```

For Windows executable builds:

```bash
pip install pyinstaller
build_exe.bat
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
