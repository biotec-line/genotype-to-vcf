"""Regressionstests - bugfix-library-transfer Batch #20 (2026-06-21)."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
MANAGE_TRANSLATIONS = ROOT / "manage_translations.py"


class TestU2ManageTranslations(unittest.TestCase):
    def _module(self):
        spec = importlib.util.spec_from_file_location(
            "manage_translations_under_test",
            MANAGE_TRANSLATIONS,
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def _src(self):
        return MANAGE_TRANSLATIONS.read_text(encoding="utf-8")

    def test_json_load_wrapped_in_try(self):
        src = self._src()
        self.assertIn(
            "json.JSONDecodeError",
            src,
            "manage_translations: json.load ohne JSONDecodeError-Handler - BUG-U2",
        )

    def test_invalid_translations_json_is_rebuilt(self):
        module = self._module()
        with self.subTest("invalid json does not abort scan"):
            from tempfile import TemporaryDirectory

            with TemporaryDirectory() as tmp:
                project = Path(tmp)
                (project / "locales").mkdir()
                translations = project / "locales" / "translations.json"
                translations.write_text("{not json", encoding="utf-8")
                (project / "app.py").write_text(
                    'from PySide6.QtWidgets import QLabel\nQLabel("Öffnen")\n',
                    encoding="utf-8",
                )

                module.manage_translations(str(project))

                rebuilt = translations.read_text(encoding="utf-8")
                self.assertIn("Öffnen", rebuilt)
                self.assertIn('"en": ""', rebuilt)


if __name__ == "__main__":
    unittest.main()
