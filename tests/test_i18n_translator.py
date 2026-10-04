"""
Unit-Tests für die I18N-Multi-Language-Erweiterung in translator.py.
"""

from pathlib import Path
from translator import TranslationSystem


def test_supported_languages():
    tr = TranslationSystem('de')
    assert 'de' in tr.SUPPORTED_LANGUAGES
    assert 'en' in tr.SUPPORTED_LANGUAGES
    assert 'es' in tr.SUPPORTED_LANGUAGES
    assert 'zh' in tr.SUPPORTED_LANGUAGES
    assert 'ja' in tr.SUPPORTED_LANGUAGES
    assert 'ru' in tr.SUPPORTED_LANGUAGES

    for lang in ['de', 'en', 'es', 'zh', 'ja', 'ru']:
        tr.set_language(lang)
        assert tr.get_language() == lang


def test_app_dir_path_casting(tmp_path):
    tr = TranslationSystem('de', app_dir=str(tmp_path))
    assert isinstance(tr.app_dir, Path)
    assert tr.app_dir == tmp_path


def test_multi_language_translation_lookup(tmp_path):
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(parents=True, exist_ok=True)
    translations_file = locales_dir / "translations.json"
    translations_file.write_text(
        '{\n'
        '  "Starten": {\n'
        '    "de": "Starten",\n'
        '    "en": "Start",\n'
        '    "es": "Iniciar",\n'
        '    "zh": "开始",\n'
        '    "ja": "開始",\n'
        '    "ru": "Запуск"\n'
        '  }\n'
        '}\n',
        encoding='utf-8'
    )

    tr = TranslationSystem('de', app_dir=tmp_path)
    tr.set_language('es')
    assert tr.t('Starten') == "Iniciar"

    tr.set_language('zh')
    assert tr.t('Starten') == "开始"

    tr.set_language('ja')
    assert tr.t('Starten') == "開始"

    tr.set_language('ru')
    assert tr.t('Starten') == "Запуск"


def test_fallback_chain(tmp_path):
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(parents=True, exist_ok=True)
    translations_file = locales_dir / "translations.json"
    translations_file.write_text(
        '{\n'
        '  "Text": {\n'
        '    "de": "Deutscher Text",\n'
        '    "en": "English Text",\n'
        '    "es": ""\n'
        '  }\n'
        '}\n',
        encoding='utf-8'
    )

    tr = TranslationSystem('de', app_dir=tmp_path)
    tr.set_language('es')
    # Since 'es' is empty string, it should fall back to 'en'
    assert tr.t('Text') == "English Text"
