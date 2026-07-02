from pathlib import Path

import Make23toVCF3 as converter


def test_main_cli_writes_vcf_with_explicit_build(tmp_path, monkeypatch, capsys):
    raw = tmp_path / "sample.tsv"
    raw.write_text("rs1\t1\t100\tAG\n", encoding="utf-8")
    out_path = tmp_path / "sample.vcf"
    cache = {
        "rs1": {
            "assemblies": {
                "GRCh37": {
                    "chrom": "1",
                    "pos": 100,
                    "ref": "A",
                }
            }
        }
    }

    monkeypatch.setattr(converter, "load_cache", lambda path=converter.CACHE_FILE: cache)
    monkeypatch.setattr(converter, "resolve_fasta_path_for_run", lambda *args, **kwargs: None)

    exit_code = converter.main(
        [
            "--input",
            str(raw),
            "--output",
            str(out_path),
            "--build",
            "GRCh37",
            "--sex",
            "female",
        ]
    )

    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert "VCF geschrieben." in stdout
    assert str(out_path) not in stdout
    records = [
        line
        for line in Path(out_path).read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    assert records == ["1\t100\trs1\tA\tG\t.\tPASS\t.\tGT\t0/1"]


def test_main_cli_creates_missing_output_directory(tmp_path, monkeypatch, capsys):
    raw = tmp_path / "sample.tsv"
    raw.write_text("rs1\t1\t100\tAG\n", encoding="utf-8")
    out_path = tmp_path / "nested" / "exports" / "sample.vcf"
    cache = {
        "rs1": {
            "assemblies": {
                "GRCh37": {
                    "chrom": "1",
                    "pos": 100,
                    "ref": "A",
                }
            }
        }
    }

    monkeypatch.setattr(converter, "load_cache", lambda path=converter.CACHE_FILE: cache)
    monkeypatch.setattr(converter, "resolve_fasta_path_for_run", lambda *args, **kwargs: None)

    exit_code = converter.main(
        [
            "--input",
            str(raw),
            "--output",
            str(out_path),
            "--build",
            "GRCh37",
            "--sex",
            "female",
        ]
    )

    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert out_path.exists()
    assert "VCF geschrieben." in stdout
    assert str(out_path) not in stdout
    records = [
        line
        for line in Path(out_path).read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    assert records == ["1\t100\trs1\tA\tG\t.\tPASS\t.\tGT\t0/1"]


def test_main_cli_detect_build_prints_detected_build(tmp_path, monkeypatch, capsys):
    raw = tmp_path / "sample.tsv"
    raw.write_text("rs1\t1\t100\tAG\n", encoding="utf-8")

    monkeypatch.setattr(converter, "load_cache", lambda path=converter.CACHE_FILE: {})
    monkeypatch.setattr(
        converter,
        "detect_build_robust",
        lambda variants, cache, signal_callback, stop_event: "GRCh38",
    )

    exit_code = converter.main(["--input", str(raw), "--detect-build"])
    stdout = capsys.readouterr().out.strip()

    assert exit_code == 0
    assert stdout == "GRCh38"


def test_main_cli_accepts_case_insensitive_build_and_sex_aliases(tmp_path, monkeypatch, capsys):
    raw = tmp_path / "sample.tsv"
    raw.write_text("rs1\t1\t100\tAG\n", encoding="utf-8")
    out_path = tmp_path / "sample.vcf"
    cache = {
        "rs1": {
            "assemblies": {
                "GRCh37": {
                    "chrom": "1",
                    "pos": 100,
                    "ref": "A",
                }
            }
        }
    }

    monkeypatch.setattr(converter, "load_cache", lambda path=converter.CACHE_FILE: cache)
    monkeypatch.setattr(converter, "resolve_fasta_path_for_run", lambda *args, **kwargs: None)

    exit_code = converter.main(
        [
            "--input",
            str(raw),
            "--output",
            str(out_path),
            "--build",
            "hg19",
            "--sex",
            "FEMALE",
        ]
    )

    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert "VCF geschrieben." in stdout
    records = [
        line
        for line in Path(out_path).read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    assert records == ["1\t100\trs1\tA\tG\t.\tPASS\t.\tGT\t0/1"]
