"""
manage_translations.py - Auto-Scanner und Paritätsprüfer für GUI-Strings
=========================================================================
Findet deutsche Strings in .py-Dateien, pflegt locales/translations.json und
prüft im --check-Modus auf lückenlose 6-Sprachen-Parität (de, en, es, zh, ja, ru).

Verwendung:
    python manage_translations.py [PROJEKTVERZEICHNIS]
    python manage_translations.py --check [--dir PROJEKTVERZEICHNIS]
"""

import argparse
import json
import os
import re

TRANSLATION_FILE = "locales/translations.json"
SUPPORTED_LANGUAGES = ("de", "en", "es", "zh", "ja", "ru")

STRING_PATTERNS = [
    re.compile(r'text\s*=\s*"([^"]+)"'),
    re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
]

GERMAN_HINTS = [
    "datei", "filter", "fehler", "laden", "speichern",
    "ansicht", "optionen", "zurueck", "anzeigen", "export",
    "import", "einstellungen", "abbrechen", "hilfe", "bearbeiten",
    "oeffnen", "schliessen", "start", "aktualisieren",
]


def is_german(text):
    if any(ch in text for ch in "\u00e4\u00f6\u00fc\u00c4\u00d6\u00dc\u00df"):
        return True
    text_lower = text.lower()
    return any(w in text_lower for w in GERMAN_HINTS)


def find_german_strings(source_dir):
    german_strings = set()
    skip_dirs = {"build", "dist", "venv", ".venv", "__pycache__", "releases"}

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue
                for pattern in STRING_PATTERNS:
                    for match in pattern.findall(content):
                        if is_german(match):
                            german_strings.add(match.strip())
    return german_strings


def check_translations(source_dir="."):
    """Validate that locales/translations.json exists and covers all 6 languages."""
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)
    if not os.path.isfile(trans_file):
        return {"ok": False, "total": 0, "missing": [f"<missing file: {trans_file}>"]}

    try:
        with open(trans_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "total": 0, "missing": [f"<invalid json: {exc}>"]}

    if not isinstance(translations, dict) or not translations:
        return {"ok": False, "total": 0, "missing": ["<empty catalog>"]}

    missing = []
    for key, entry in sorted(translations.items()):
        if not isinstance(entry, dict):
            missing.append(f"{key}: invalid entry")
            continue
        for lang in SUPPORTED_LANGUAGES:
            if not str(entry.get(lang, "")).strip():
                missing.append(f"{key}[{lang}]")

    return {"ok": not missing, "total": len(translations), "missing": missing}


def manage_translations(source_dir="."):
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)

    if os.path.exists(trans_file):
        try:
            with open(trans_file, "r", encoding="utf-8") as f:
                translations = json.load(f)
        except (json.JSONDecodeError, OSError):
            translations = {}
    else:
        translations = {}

    found = find_german_strings(source_dir)

    added = []
    for s in sorted(found):
        if s not in translations:
            translations[s] = {"de": s, "en": ""}
            added.append(s)

    os.makedirs(os.path.dirname(trans_file), exist_ok=True)
    with open(trans_file, "w", encoding="utf-8") as f:
        json.dump(translations, f, indent=2, ensure_ascii=False)
        f.write("\n")

    if added:
        print(f"[+] {len(added)} neue Eintraege hinzugefuegt:")
        for s in added[:20]:
            print(f"    - {s}")
        if len(added) > 20:
            print(f"    ... und {len(added) - 20} weitere")
    else:
        print("[i] Keine neuen deutschen Strings gefunden.")

    missing = [k for k, v in translations.items() if not v.get("en")]
    if missing:
        print(f"\n[!] {len(missing)} fehlende englische Uebersetzungen")
    else:
        print("\n[ok] Alle Strings haben englische Uebersetzungen.")

    print(f"\n[i] Gesamt: {len(translations)} Strings in {trans_file}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Manage or verify 6-language GUI translations.")
    parser.add_argument("legacy_dir", nargs="?", default=None, help="Optionales Zielverzeichnis.")
    parser.add_argument("--dir", dest="target_dir", default=".", help="Projektverzeichnis.")
    parser.add_argument("--check", action="store_true", help="Prüft 6-Sprachen-Parität (Exit 0/1).")
    args = parser.parse_args(argv)

    source_dir = args.legacy_dir or args.target_dir
    if args.check:
        report = check_translations(source_dir)
        if report["ok"]:
            print(f"[ok] 6-Sprachen-Parität vollständig ({report['total']} Keys x 6 Sprachen).")
            return 0
        print(f"[!] Fehlende Übersetzungen ({len(report['missing'])}): {', '.join(report['missing'][:20])}")
        return 1

    manage_translations(source_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
