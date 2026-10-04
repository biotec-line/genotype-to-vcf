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


def test_cache_thread_safety(tmp_path):
    import threading
    import Make23toVCF3 as converter

    cache = {}
    cache_file = tmp_path / "test_cache.json"

    def writer():
        for i in range(100):
            converter.cache_upsert(cache, f"rs{i}", "GRCh38", "1", i, "A")
        # Nested mutation: same rsid, changing builds (grows entry["assemblies"])
        for i in range(2000):
            converter.cache_upsert(cache, "rs_shared", f"build{i}", "1", i, "A")

    def saver():
        for _ in range(200):
            converter.save_cache(cache, str(cache_file))

    def reader():
        for i in range(100):
            converter.lookup_rsid_from_cache("1", i, "GRCh38", cache)

    threads = [
        threading.Thread(target=writer),
        threading.Thread(target=saver),
        threading.Thread(target=reader),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert "rs99" in cache
    assert len(cache["rs_shared"]["assemblies"]) == 2000


def test_save_cache_snapshot_is_isolated_from_nested_updates(tmp_path, monkeypatch):
    import Make23toVCF3 as converter

    cache = {}
    converter.cache_upsert(cache, "rs1", "GRCh37", "1", 1, "A")
    seen = {}

    def fake_write(path, obj):
        # A concurrent upsert lands while the snapshot is being serialized.
        converter.cache_upsert(cache, "rs1", "GRCh38", "1", 2, "C")
        seen["builds"] = sorted(obj["rs1"]["assemblies"])

    monkeypatch.setattr(converter, "atomic_write_json", fake_write)
    converter.save_cache(cache, str(tmp_path / "c.json"))
    assert seen["builds"] == ["GRCh37"]  # deep snapshot, not a live view


def test_normalize_chrom_and_numerical_dtc_codes():
    import Make23toVCF3 as converter

    assert converter.normalize_chrom("23") == "X"
    assert converter.normalize_chrom("24") == "Y"
    assert converter.normalize_chrom("25") == "X"
    assert converter.normalize_chrom("26") == "MT"
    assert converter.normalize_chrom("chrM") == "MT"

    # Test sex detection with numerical chromosome 24
    variants = [(f"rs{i}", "24", 1000 + i, "AA") for i in range(10)]
    assert converter.detect_sex_from_variants(variants) == "male"

    # Test ploidy logic with numerical chromosome 24 for female/male
    assert converter.ploidy_for_site("24", 2_700_000, "GRCh37", "female") == 0
    assert converter.ploidy_for_site("24", 2_700_000, "GRCh37", "male") == 1


if __name__ == "__main__":
    unittest.main()


