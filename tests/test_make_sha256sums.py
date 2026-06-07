"""Tests fuer scripts/make_sha256sums.py."""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import make_sha256sums


def test_compute_sha256_for_single_file(tmp_path):
    f = tmp_path / "test.exe"
    f.write_bytes(b"hello world")
    expected = hashlib.sha256(b"hello world").hexdigest()
    result = make_sha256sums.compute_sha256(f)
    assert result == expected


def test_generate_sums_returns_lines_for_each_file(tmp_path):
    (tmp_path / "a.exe").write_bytes(b"aaa")
    (tmp_path / "b.zip").write_bytes(b"bbb")
    lines = make_sha256sums.generate_sums(tmp_path, patterns=["*.exe", "*.zip"])
    assert len(lines) == 2
    for line in lines:
        parts = line.split("  ", 1)
        assert len(parts) == 2
        assert len(parts[0]) == 64


def test_generate_sums_writes_sha256sums_file(tmp_path):
    (tmp_path / "release.exe").write_bytes(b"data")
    make_sha256sums.write_sha256sums(tmp_path, patterns=["*.exe"])
    out = tmp_path / "SHA256SUMS"
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "release.exe" in content
    assert len(content.strip().split("\n")) == 1


def test_generate_sums_empty_directory(tmp_path):
    lines = make_sha256sums.generate_sums(tmp_path, patterns=["*.exe"])
    assert lines == []
