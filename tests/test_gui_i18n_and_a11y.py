"""Tests for 6-language GUI i18n wiring, accessibility, and browser-demo A11y."""

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

import Make23toVCF3 as converter
from manage_translations import check_translations
from translator import LANGUAGE_DISPLAY_NAMES, TranslationSystem, detect_system_language

ROOT = Path(__file__).resolve().parents[1]


def _ensure_qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_locales_catalog_has_full_six_language_parity():
    report = check_translations(str(ROOT))
    assert report["ok"], f"Missing translations: {report['missing']}"
    assert report["total"] >= 30


def test_translator_formatting_and_detect_system_language(monkeypatch, tmp_path):
    tr = TranslationSystem("en", app_dir=ROOT, auto_save_missing=False)
    msg = tr.t("conversion_finished_msg", written=42, output_path="out.vcf")
    assert "42" in msg
    assert "out.vcf" in msg

    monkeypatch.setattr("translator.locale.getlocale", lambda: ("es_ES", "UTF-8"))
    assert detect_system_language() == "es"

    monkeypatch.setattr("translator.locale.getlocale", lambda: ("pt_BR", "UTF-8"))
    assert detect_system_language(default="en") == "en"

    # auto_save_missing=False must never write into app_dir
    ro_tr = TranslationSystem("de", app_dir=tmp_path, auto_save_missing=False)
    assert ro_tr.t("Öffne bitte sofort") == "Öffne bitte sofort"
    assert not (tmp_path / "locales" / "translations.json").exists()


def test_main_window_six_language_switching_and_canonical_item_data(monkeypatch):
    _ensure_qapp()
    monkeypatch.setattr(converter, "load_cache", lambda: {})

    window = converter.MainWindow()
    try:
        assert window.combo_lang.count() == len(LANGUAGE_DISPLAY_NAMES)
        assert window.lbl_sex.buddy() is window.combo_sex
        assert window.lbl_build.buddy() is window.combo_build
        assert window.lbl_lang.buddy() is window.combo_lang

        # Select a mock file and verify filename survives language switching
        window.file_path = "/tmp/sample_23andme.txt"
        window.lbl_file.setText("sample_23andme.txt")

        expected_start_labels = {
            "de": "🚀 Konvertierung Starten",
            "en": "🚀 Start Conversion",
            "es": "🚀 Iniciar conversión",
            "zh": "🚀 开始转换",
            "ja": "🚀 変換を開始",
            "ru": "🚀 Начать конвертацию",
        }
        expected_female_labels = {
            "de": "Weiblich",
            "en": "Female",
            "es": "Femenino",
            "zh": "女性",
            "ja": "女性",
            "ru": "Женский",
        }

        for lang in ("de", "en", "es", "zh", "ja", "ru"):
            idx = window.combo_lang.findData(lang)
            assert idx >= 0
            window.combo_lang.setCurrentIndex(idx)

            assert window.translator.get_language() == lang
            assert window.btn_start.text() == expected_start_labels[lang]
            assert window.lbl_file.text() == "sample_23andme.txt"

            # Canonical data values stay stable while display labels change
            window.combo_sex.setCurrentIndex(1)
            assert window.combo_sex.itemText(1) == expected_female_labels[lang]
            assert window.combo_sex.currentData() == "female"

            window.combo_build.setCurrentIndex(2)
            assert window.combo_build.currentData() == "GRCh38"

            # Every interactive control exposes localized A11y metadata
            for widget in (
                window.btn_file,
                window.combo_sex,
                window.combo_build,
                window.combo_lang,
                window.btn_start,
                window.btn_cancel,
            ):
                assert widget.accessibleName().strip()
                assert widget.accessibleDescription().strip()
                assert widget.toolTip().strip()

            assert window.progress_bar.accessibleName().strip()
            assert window.txt_log.accessibleName().strip()
            assert window.txt_log.placeholderText().strip()

        # When no file is selected, lbl_file updates with language switch
        window.file_path = None
        window.set_language("en")
        assert window.lbl_file.text() == "No file selected"
    finally:
        window.close()


def test_main_window_qss_contrast_and_keyboard_shortcuts(monkeypatch):
    _ensure_qapp()
    monkeypatch.setattr(converter, "load_cache", lambda: {})

    window = converter.MainWindow()
    try:
        qss = window.styleSheet()
        assert "QPushButton#CancelButton:disabled" in qss
        assert "color: #b5b5b5;" in qss
        assert "background-color: #2c2c2c;" in qss
        assert "QPushButton:focus" in qss
        assert "QComboBox:focus" in qss
        assert "#64b5f6" in qss
        assert "color: #c0c0c0;" in window.lbl_file.styleSheet()

        shortcuts = {
            window.shortcut_open.key().toString(),
            window.shortcut_start_return.key().toString(),
            window.shortcut_cancel.key().toString(),
        }
        assert "Ctrl+O" in shortcuts
        assert "Esc" in shortcuts
    finally:
        window.close()


def test_conversion_worker_uses_translator_messages(tmp_path, monkeypatch):
    _ensure_qapp()
    tr = TranslationSystem("en", app_dir=ROOT, auto_save_missing=False)
    monkeypatch.setattr(
        converter,
        "run_conversion_pipeline",
        lambda *args, **kwargs: {"written": 7, "output_path": str(tmp_path / "out.vcf")},
    )
    worker = converter.ConversionWorker("in.tsv", "female", "GRCh37", {}, translator=tr)
    finished = []
    worker.finished_signal.connect(finished.append)
    worker.run()
    assert finished and "Success! 7 variants written." in finished[0]


def test_browser_local_demo_accessibility_markup():
    html = (ROOT / "docs" / "browser-local-demo" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "docs" / "browser-local-demo" / "demo.css").read_text(encoding="utf-8")

    assert 'id="status-banner" class="status info" role="status" aria-live="polite"' in html
    assert 'id="warnings" class="warnings" aria-live="polite"' in html
    assert '<caption class="sr-only">' in html
    assert '<th scope="col">rsID</th>' in html

    assert "display: none;" not in css
    assert ":focus-visible" in css
    assert ".button:focus-within" in css
    assert ".sr-only" in css
