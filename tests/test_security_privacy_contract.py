"""Security and privacy contract test for genotype-to-vcf.

Checks the tracked file set (``git ls-files``), not the working tree, so local
runs that create ``cache.json``, VCFs, FASTA files or a built EXE do not fail:

- No personal genomic data (.vcf, genome_*) is tracked.
- No build binaries (.exe), reference files (.fa) or cache files are tracked.
- No hardcoded absolute user paths (C:\\Users\\) in tracked Python files.
- LICENSE and THIRD_PARTY_LICENSES.txt are present and non-empty.
"""

import fnmatch
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def tracked_files():
    try:
        result = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git is unavailable or the project root is not a git repository")
    return [line for line in result.stdout.splitlines() if line]


def matching(files, patterns):
    return [f for f in files if any(fnmatch.fnmatch(Path(f).name, p) for p in patterns)]


def test_no_personal_genomic_data_tracked():
    found = matching(tracked_files(), ["*.vcf", "*.vcf.gz", "genome_*"])
    assert not found, f"Personal genomic files are tracked: {found}"


def test_no_build_artifacts_or_caches_tracked():
    found = matching(tracked_files(), ["*.exe", "*.fa", "*.fa.fai", "*.fa.gz", "cache.json", "_ul"])
    assert not found, f"Build artifacts/caches are tracked: {found}"


def test_no_hardcoded_user_paths_in_tracked_python_code():
    user_path_pattern = re.compile(r"C:[\\/]Users[\\/]", re.IGNORECASE)
    violations = []
    for name in tracked_files():
        if not name.endswith(".py"):
            continue
        content = (ROOT / name).read_text(encoding="utf-8", errors="ignore")
        if user_path_pattern.search(content):
            violations.append(name)
    assert not violations, f"Hardcoded user paths found in: {violations}"


def test_license_and_third_party_inventory_exist():
    license_file = ROOT / "LICENSE"
    third_party_file = ROOT / "THIRD_PARTY_LICENSES.txt"

    assert license_file.is_file(), "LICENSE file missing"
    assert license_file.stat().st_size > 100, "LICENSE file empty"

    assert third_party_file.is_file(), "THIRD_PARTY_LICENSES.txt missing"
    assert third_party_file.stat().st_size > 100, "THIRD_PARTY_LICENSES.txt empty"
