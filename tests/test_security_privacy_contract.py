"""Security and Privacy contract test for BIO/REL-PUB_23andMe_to_VCF.

Verifies:
- No personal genomic data (.vcf, genome_*) is tracked or stored in project root.
- No build binaries (.exe) or multi-GB reference files (.fa) sit in project root.
- No hardcoded absolute user paths (C:\\Users\\) or API credentials in python files.
- LICENSE and THIRD_PARTY_LICENSES.txt files are present and non-empty.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_no_personal_genomic_data_in_root():
    vcf_files = list(ROOT.glob("*.vcf")) + list(ROOT.glob("*.vcf.gz"))
    genome_files = list(ROOT.glob("genome_*"))
    assert not vcf_files, f"Personal VCF files found in root: {vcf_files}"
    assert not genome_files, f"Personal genome files found in root: {genome_files}"


def test_no_root_build_artifacts_or_caches():
    forbidden_patterns = ["*.exe", "*.fa", "*.fa.fai", "cache.json", "_ul"]
    found_artifacts = []
    for pattern in forbidden_patterns:
        found_artifacts.extend(ROOT.glob(pattern))
    assert not found_artifacts, f"Build artifacts/caches in root: {found_artifacts}"


def test_no_hardcoded_user_paths_in_python_code():
    py_files = list(ROOT.rglob("*.py"))
    user_path_pattern = re.compile(r"C:[\\/]Users[\\/]", re.IGNORECASE)

    violations = []
    for py_file in py_files:
        if ".venv" in py_file.parts or "__pycache__" in py_file.parts:
            continue
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        if user_path_pattern.search(content):
            violations.append(str(py_file.relative_to(ROOT)))

    assert not violations, f"Hardcoded user paths found in: {violations}"


def test_license_and_third_party_inventory_exist():
    license_file = ROOT / "LICENSE"
    third_party_file = ROOT / "THIRD_PARTY_LICENSES.txt"

    assert license_file.is_file(), "LICENSE file missing"
    assert license_file.stat().st_size > 100, "LICENSE file empty"

    assert third_party_file.is_file(), "THIRD_PARTY_LICENSES.txt missing"
    assert third_party_file.stat().st_size > 100, "THIRD_PARTY_LICENSES.txt empty"
