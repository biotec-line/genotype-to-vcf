"""
TranslationSystem - Multi-Language Support für Anwendungen
============================================================
Version: 1.2.0 (6-Sprachen-GUI-Integration, atomare Persistenz & Systemerkennung)
Quelle: ARC_EntwicklungsschleifeAdvanced/TranslationSystem.py v2.4

Verwendung:
-----------
from translator import TranslationSystem

translator = TranslationSystem('de')
label.setText(translator.t('Datei öffnen'))
translator.set_language('en')
"""

import json
import locale
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Union

LANGUAGE_DISPLAY_NAMES: Dict[str, str] = {
    "de": "Deutsch",
    "en": "English",
    "es": "Español",
    "zh": "简体中文",
    "ja": "日本語",
    "ru": "Русский",
}


def detect_system_language(default: str = "de") -> str:
    """Detect the current OS UI language and map it to a supported 2-letter code."""
    try:
        loc, _ = locale.getlocale()
    except (TypeError, ValueError):
        loc = None
    if not loc:
        return default
    code = re.split(r"[-_.]", str(loc).strip().lower())[0]
    if code in LANGUAGE_DISPLAY_NAMES:
        return code
    return default


def resolve_app_dir(app_dir: Union[str, Path, None] = None) -> Path:
    """Resolve the base directory containing locales/translations.json."""
    if app_dir is not None:
        return Path(app_dir)
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path.cwd()


class TranslationSystem:
    """Multi-Language Support System v1.2.0"""

    SUPPORTED_LANGUAGES = ["de", "en", "es", "zh", "ja", "ru"]

    def __init__(
        self,
        default_lang: str = "de",
        app_dir: Union[str, Path, None] = None,
        *,
        auto_save_missing: bool = True,
    ):
        """
        Initialisiert Translation-System.

        Args:
            default_lang: Standard-Sprache ('de', 'en', 'es', 'zh', 'ja', 'ru')
            app_dir: Verzeichnis der Anwendung (default: aktuelles Verzeichnis bzw. _MEIPASS)
            auto_save_missing: Unbekannte deutsche Keys automatisch in translations.json sichern
        """
        self.current_lang = default_lang if default_lang in self.SUPPORTED_LANGUAGES else "de"
        self.app_dir = resolve_app_dir(app_dir)
        self.auto_save_missing = auto_save_missing

        self.translations_file = self.app_dir / "locales" / "translations.json"

        self.string_patterns = [
            re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addAction\s*\([^,]*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addTab\s*\([^,]+,\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'text\s*=\s*"([^"]+)"'),
        ]

        self.german_hints = [
            "datei", "bearbeiten", "ansicht", "hilfe", "oeffnen", "speichern",
            "schliessen", "einstellungen", "abbrechen", "ok", "ja", "nein",
            "start", "stop", "pause", "fortsetzen", "laden", "aktualisieren",
            "filter", "fehler", "export", "import", "optionen", "anzeigen",
        ]

        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self):
        if self.translations_file.exists():
            try:
                with open(self.translations_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self.translations = loaded if isinstance(loaded, dict) else {}
            except Exception:
                self.translations = {}
        else:
            self.translations = {}

    def _save_translations(self):
        self.translations_file.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.translations_file.with_name(
            f"{self.translations_file.name}.tmp.{os.getpid()}"
        )
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.translations, f, indent=2, ensure_ascii=False)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.translations_file)
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass

    def t(self, key: str, **kwargs) -> str:
        """
        Übersetzt einen Key in die aktuelle Sprache.

        Args:
            key: Translation-Key (oft der deutsche Originaltext oder eine semantische ID)
            **kwargs: Optionale Format-Platzhalter

        Returns:
            Übersetzter Text oder Fallback (Zielsprache -> EN -> DE -> Key)
        """
        text = key
        if key in self.translations:
            lang_dict = self.translations[key]
            val = lang_dict.get(self.current_lang)
            if val:
                text = val
            else:
                # Fallback-Kette: Zielsprache -> EN -> DE -> key
                text = lang_dict.get("en") or lang_dict.get("de") or key
        elif self.auto_save_missing and self._is_german(key):
            self.translations[key] = {"de": key, "en": ""}
            self._save_translations()

        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError, IndexError):
                return text
        return text

    def set_language(self, lang: str):
        if lang in self.SUPPORTED_LANGUAGES:
            self.current_lang = lang

    def get_language(self) -> str:
        return self.current_lang

    def get_supported_languages(self) -> List[str]:
        return list(self.SUPPORTED_LANGUAGES)

    def add_translation(
        self,
        key: str,
        de: str = "",
        en: str = "",
        es: str = "",
        zh: str = "",
        ja: str = "",
        ru: str = "",
    ):
        self.translations[key] = {
            "de": de or key,
            "en": en,
            "es": es,
            "zh": zh,
            "ja": ja,
            "ru": ru,
        }
        self._save_translations()

    def scan_and_update(self, project_dir: Union[Path, None] = None) -> Dict:
        """Scannt Projekt-Dateien nach deutschen Strings und aktualisiert translations.json."""
        if project_dir is None:
            project_dir = self.app_dir

        found_strings = self._find_german_strings(project_dir)

        added = []
        for s in sorted(found_strings):
            if s not in self.translations:
                self.translations[s] = {"de": s, "en": "", "es": "", "zh": "", "ja": "", "ru": ""}
                added.append(s)

        if added:
            self._save_translations()

        missing = [k for k, v in self.translations.items() if not v.get("en")]

        return {"added": added, "missing": missing, "total": len(self.translations)}

    def _find_german_strings(self, directory: Path) -> Set[str]:
        german_strings = set()
        skip_dirs = {"build", "dist", "venv", ".venv", "__pycache__", "releases"}

        for py_file in directory.rglob("*.py"):
            if any(folder in py_file.parts for folder in skip_dirs):
                continue
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            for pattern in self.string_patterns:
                for match in pattern.findall(content):
                    if match and self._is_german(match):
                        german_strings.add(match.strip())

        return german_strings

    def _is_german(self, text: str) -> bool:
        if any(ch in text for ch in "äöüÄÖÜß"):
            return True
        text_lower = text.lower()
        return any(hint in text_lower for hint in self.german_hints)

    def get_missing_translations(self, lang: str = "en") -> List[str]:
        return [k for k, v in self.translations.items() if not v.get(lang)]


if __name__ == "__main__":
    tr = TranslationSystem("de")
    print(f"Sprache: {tr.get_language()}")
    result = tr.scan_and_update()
    print(f"Scan: {result['total']} Strings, {len(result['added'])} neu, {len(result['missing'])} ohne EN")
