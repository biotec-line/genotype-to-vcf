"""Regressionstests für translator.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from translator import TranslationSystem


def test_is_german_does_not_match_plain_english():
    """Bug B: _is_german('Hello World') darf nicht True zurückgeben."""
    tr = TranslationSystem.__new__(TranslationSystem)
    tr.translations = {}
    tr.translations_file = Path("/nonexistent/translations.json")
    tr.current_lang = "de"
    tr.string_patterns = []
    tr.german_hints = []
    assert not tr._is_german("Hello World"), (
        "_is_german erkennt englischen Text fälschlich als Deutsch (Bug B: 'aeoeueAeOeUess' statt 'äöüÄÖÜß')"
    )


def test_is_german_matches_umlaut_text():
    """_is_german muss echte Umlaute als Deutsch erkennen."""
    tr = TranslationSystem.__new__(TranslationSystem)
    tr.translations = {}
    tr.translations_file = Path("/nonexistent/translations.json")
    tr.current_lang = "de"
    tr.string_patterns = []
    tr.german_hints = []
    assert tr._is_german("Öffne Datei")
    assert tr._is_german("Bitte bestätigen")
    assert tr._is_german("Schließen")


def test_is_german_does_not_match_common_words():
    """Gewöhnliche englische Wörter ohne Umlaute sollen nicht als Deutsch erkannt werden."""
    tr = TranslationSystem.__new__(TranslationSystem)
    tr.translations = {}
    tr.translations_file = Path("/nonexistent/translations.json")
    tr.current_lang = "de"
    tr.string_patterns = []
    tr.german_hints = []
    for word in ("Start", "Stop", "OK", "Error", "File", "Open"):
        assert not tr._is_german(word), f"'{word}' fälschlich als Deutsch erkannt"
