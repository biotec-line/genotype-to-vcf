"""Contract tests for repository metadata, licensing, SBOM, CI hardening, and invariants."""

from pathlib import Path
import re
import subprocess

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python <3.11


ROOT = Path(__file__).resolve().parents[1]


def test_canonical_notice_present_and_well_formed():
    notice_file = ROOT / "NOTICE"
    assert notice_file.is_file(), "Root NOTICE file must exist"
    content = notice_file.read_text(encoding="utf-8")

    assert "Genotype-to-VCF Pro" in content
    assert "Lukas Geiger" in content
    assert "biotec-line" in content
    assert "open-bricks" in content
    assert "MIT License" in content

    # Check key invariants
    for inv in [
        "INV-LOCAL-01",
        "INV-LOCAL-02",
        "INV-LOCAL-03",
        "INV-LOCAL-04",
        "INV-LOCAL-05",
        "INV-LOCAL-06",
        "INV-LOCAL-07",
        "INV-LOCAL-08",
        "INV-LOCAL-09",
        "INV-LOCAL-10",
    ]:
        assert inv in content, f"NOTICE must document invariant {inv}"


def test_level_1_sbom_present_and_well_formed():
    sbom_file = ROOT / "THIRD_PARTY_LICENSES.md"
    assert sbom_file.is_file(), "Level 1 SBOM file THIRD_PARTY_LICENSES.md must exist"
    content = sbom_file.read_text(encoding="utf-8")

    assert "Level 1 Software Bill of Materials" in content
    assert "LGPL-3.0" in content
    assert "PySide6" in content
    assert "Dynamische Bindung" in content or "dynamic linking" in content.lower()
    assert "INV-LOCAL-01" in content
    assert "INV-SLA-10" in content or "INV-LOCAL-10" in content

    # Verify requirements coverage
    req_file = ROOT / "requirements.txt"
    for line in req_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pkg = re.split(r"[><=~]", line)[0].strip().lower()
        assert pkg in content.lower(), f"Package {pkg} must be documented in Level 1 SBOM"


def test_pep621_pyproject_metadata_and_version_freeze():
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.is_file()

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    # Strict Version Freeze Rule T-20260920-167562623: Pfad A/B passes never bump versions
    assert project.get("version") == "1.0.3", "Version must be 1.0.3"
    assert project.get("license") == "MIT", "PEP 639 license string must be 'MIT'"
    classifiers = project.get("classifiers", [])
    assert not any(c.startswith("License ::") for c in classifiers), (
        "Do not combine PEP 639 string license with License :: OSI classifiers"
    )

    license_files = project.get("license-files", [])
    for expected_file in ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"]:
        assert expected_file in license_files, f"{expected_file} must be declared in license-files"

    urls = project.get("urls", {})
    assert "Homepage" in urls
    assert "Repository" in urls
    assert "Documentation" in urls
    assert "Issues" in urls
    assert "Notice" in urls
    assert "Third-Party Licenses" in urls
    assert "Marketing Log" not in urls

    scripts = project.get("scripts", {})
    assert scripts.get("genotype-to-vcf") == "Make23toVCF3:main"

    declared_deps = {
        re.split(r"[><=~!\[]", dep)[0].strip().lower()
        for dep in project.get("dependencies", [])
    }
    req_deps = {
        re.split(r"[><=~!\[]", line)[0].strip().lower()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    assert req_deps <= declared_deps, (
        f"pyproject.toml dependencies {declared_deps} must cover requirements.txt {req_deps}"
    )

    pytest_opts = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert "--basetemp=" not in pytest_opts.get("addopts", "")
    conftest_content = (ROOT / "conftest.py").read_text(encoding="utf-8")
    assert "pytest_configure" in conftest_content
    assert "config.rootpath" in conftest_content

    pytest_ini_content = (ROOT / "pytest.ini").read_text(encoding="utf-8")
    assert "--basetemp=" not in pytest_ini_content

    ruff_opts = data.get("tool", {}).get("ruff", {})
    assert ruff_opts.get("line-length") == 100


def test_gitignore_cloud_sync_and_lock_guards():
    gitignore_path = ROOT / ".gitignore"
    assert gitignore_path.is_file()
    content = gitignore_path.read_text(encoding="utf-8")

    # Multi-host sync conflict protection
    assert "*conflicted copy*" in content
    assert "*-WORKSTATION*" in content
    assert "*-ASUS*" in content
    assert "*-LAPTOP*" in content
    assert "*-Mac" in content

    # System-wide and scoped locks
    assert "LOCK" in content
    assert "LOCK.user.*" in content
    assert "LOCK.until.*" in content
    assert "LOCK.condition.*" in content
    assert ".automation-lock" in content

    # Temporary test caches
    assert ".pytest_tmp/" in content
    assert ".ruff_cache/" in content


def test_ci_workflows_hardened():
    ci_dir = ROOT / ".github" / "workflows"
    ci_file = ci_dir / "ci.yml"
    stale_file = ci_dir / "stale.yml"
    welcome_file = ci_dir / "welcome.yml"

    for wf_path in (ci_file, stale_file, welcome_file):
        assert wf_path.is_file(), f"Workflow {wf_path.name} must exist"
        wf_content = wf_path.read_text(encoding="utf-8")
        assert "cancel-in-progress: true" in wf_content, f"{wf_path.name} must specify cancel-in-progress"
        assert "timeout-minutes:" in wf_content, f"{wf_path.name} must specify timeout-minutes"

    # Specific CI checks
    ci_content = ci_file.read_text(encoding="utf-8")
    assert "contents: read" in ci_content
    assert "compileall" in ci_content
    assert "ruff check" in ci_content


def test_security_sla_and_bgb_disclaimer():
    security_file = ROOT / "SECURITY.md"
    assert security_file.is_file()
    sec_content = security_file.read_text(encoding="utf-8")

    assert "48" in sec_content, "SECURITY.md must define 48h acknowledgment SLA"
    assert "5" in sec_content, "SECURITY.md must define 5-day triage SLA"
    assert "521 BGB" in sec_content, "SECURITY.md must include § 521 BGB statutory disclaimer"

    readme_file = ROOT / "README.md"
    readme_content = readme_file.read_text(encoding="utf-8")
    assert "521 BGB" in readme_content, "README.md must include § 521 BGB statutory disclaimer"


def test_marketing_log_not_tracked_and_ignored():
    gitignore_content = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "MARKETING-LOG.txt" in gitignore_content

    try:
        res = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "MARKETING-LOG.txt"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return
    assert res.returncode != 0, "MARKETING-LOG.txt must not be tracked in git"


def test_p022_llm_and_skill_entrypoints():
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "Make23toVCF3.py" in skill_text
    assert "--input" in skill_text
    assert "--detect-build" in skill_text
    assert "--preflight" in skill_text
    assert "--fasta" in skill_text
    assert "--cache" in skill_text
    assert "--version" in skill_text

    llm_text = (ROOT / "llm.txt").read_text(encoding="utf-8")
    assert "llms.txt" in llm_text

    llms_text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "SKILL.md" in llms_text
    assert "1.0.3" in llms_text
    assert "Last-checked: 2026-11-23" in llms_text

    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")
    assert "Install with your LLM" in readme_en
    assert "Mit deinem LLM installieren" in readme_de
    assert "SKILL.md" in readme_en and "SKILL.md" in readme_de
