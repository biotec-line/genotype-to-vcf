from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _normalise_package_name(requirement: str) -> str:
    requirement = requirement.strip()
    for separator in ("==", ">=", "<=", "~=", "!=", ">", "<", "["):
        if separator in requirement:
            requirement = requirement.split(separator, 1)[0]
    return requirement.strip().replace("_", "-").lower()


def test_third_party_license_inventory_covers_runtime_requirements():
    requirements = [
        _normalise_package_name(line)
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    inventory = (ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")
    normalised_inventory = inventory.replace("_", "-").lower()

    assert "project license" in normalised_inventory
    assert "checked: 2026-07-06" in normalised_inventory
    assert "not a complete frozen transitive sbom" in normalised_inventory

    for package in requirements:
        assert package in normalised_inventory

    for package in ("pyside6-addons", "pyside6-essentials", "shiboken6"):
        assert package in normalised_inventory


def test_license_inventory_does_not_include_private_data_artifacts():
    inventory = (ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8").lower()

    forbidden_artifacts = [
        "genome_",
        ".vcf",
        "cache.json",
        "homo_sapiens",
    ]

    for artifact in forbidden_artifacts:
        assert artifact not in inventory
