from pathlib import Path

import pytest

import Make23toVCF3 as converter


@pytest.mark.parametrize("chrom, expected_sex", [("Y", "male"), ("1", "female")])
def test_cli_auto_sex_keeps_inference_out_of_progress_logs(
    tmp_path, monkeypatch, capsys, chrom, expected_sex
):
    raw = tmp_path / "input.tsv"
    raw.write_text("".join(f"rs{i}\t{chrom}\t{100+i}\tAG\n" for i in range(1, 7)), encoding="utf-8")
    output = tmp_path / "output.vcf"
    cache = {f"rs{i}": {"assemblies": {"GRCh37": {
        "chrom": chrom, "pos": 100+i, "ref": "A",
    }}} for i in range(1, 7)}
    monkeypatch.setattr(converter, "load_cache", lambda: cache)
    monkeypatch.setattr(converter, "resolve_fasta_path_for_run", lambda *args, **kwargs: None)
    original_write = converter._write_vcf_atomic
    observed_sex = []

    def write(*args, **kwargs):
        observed_sex.append(args[5])
        return original_write(*args, **kwargs)

    monkeypatch.setattr(converter, "_write_vcf_atomic", write)
    assert converter.main(["--input", str(raw), "--output", str(output),
                           "--build", "GRCh37"]) == 0
    captured = capsys.readouterr()
    assert observed_sex == [expected_sex]
    assert output.exists()
    assert "VCF geschrieben." in captured.out
    assert "male" not in (captured.out + captured.err).lower()
    assert "female" not in (captured.out + captured.err).lower()
    assert "Geschlechtsprüfung abgeschlossen." in captured.err


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


def test_cli_version_flag_prints_frozen_app_version(capsys):
    exit_code = converter.main(["--version"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert f"Genotype-to-VCF Pro {converter.APP_VERSION}" in captured.out
    assert captured.err == ""


def test_cli_preflight_json_and_text_zero_network(tmp_path, monkeypatch, capsys):
    raw = tmp_path / "mixed_export.csv"
    raw.write_text(
        "\ufeff# comment header\n"
        "rs_id;chromosome;position;genotype\n"
        '"rs100";"23";"60005";"ag"\n'
        "rs101;24;15000;--\n"
        "rs102;26;73;tt\n"
        "rs_ancestry,1,555,A,G\n"
        "rs_zero\t2\t0\tAA\n"
        "rs_badpos\t2\tnot_an_int\tCC\n\n",
        encoding="utf-8",
    )

    def _forbid_cache(*_args, **_kwargs):
        raise AssertionError("--preflight must not read or create cache.json")

    monkeypatch.setattr(converter, "load_cache", _forbid_cache)

    exit_code = converter.main(["--input", str(raw), "--preflight", "--json"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert str(raw) not in captured.out
    assert "rs100" not in captured.out

    import json

    report = json.loads(captured.out)
    assert report["compatible"] is True
    assert report["has_warnings"] is True
    assert report["valid_records"] == 3
    assert report["no_call_records"] == 1
    assert report["skipped_comment"] == 1
    assert report["skipped_header"] == 1
    assert report["skipped_five_column_layout"] == 1
    assert report["skipped_unsupported_layout"] == 1
    assert report["skipped_invalid_position"] == 2
    assert report["chromosomes"] == {"X": 1, "Y": 1, "MT": 1}

    #Incompatible file (0 valid 4-column records) returns exit code 1
    ancestry_only = tmp_path / "ancestry_5col.txt"
    ancestry_only.write_text(
        "rsid\tchromosome\tposition\tallele1\tallele2\nrs1\t1\t100\tA\tG\n",
        encoding="utf-8",
    )
    bad_exit = converter.main(["--input", str(ancestry_only), "--preflight"])
    bad_captured = capsys.readouterr()
    assert bad_exit == 1
    assert str(ancestry_only) not in (bad_captured.out + bad_captured.err)


def test_cli_explicit_fasta_and_cache_paths_outside_base_dir(tmp_path, monkeypatch, capsys):
    ref_dir = tmp_path / "workstation_refs"
    ref_dir.mkdir()
    fasta_path = ref_dir / "GRCh38_mini.fa"
    # 10 bases on chr1: A C G T A C G T A C (newline = 11 bytes per line)
    fasta_path.write_bytes(b">1\nACGTACGTAC\n")
    fai_path = ref_dir / "GRCh38_mini.fa.fai"
    fai_path.write_text("1\t10\t3\t10\t11\n", encoding="utf-8")

    cache_dir = tmp_path / "workstation_cache"
    cache_path = cache_dir / "custom_cache.json"

    raw = tmp_path / "sample.tsv"
    raw.write_text("rs999\t1\t3\tGA\n", encoding="utf-8")
    out_vcf = tmp_path / "out" / "sample.vcf"

    def _forbid_network(*_args, **_kwargs):
        raise AssertionError("Offline FASTA run must not query NCBI dbSNP")

    monkeypatch.setattr(converter, "adaptive_parallel_fetch", _forbid_network)

    exit_code = converter.main(
        [
            "--input",
            str(raw),
            "--output",
            str(out_vcf),
            "--build",
            "GRCh38",
            "--sex",
            "female",
            "--fasta",
            str(fasta_path),
            "--cache",
            str(cache_path),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0, captured.err
    assert out_vcf.is_file()
    records = [
        line
        for line in out_vcf.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    # pos 3 in ACGTACGTAC is 'G', genotype GA -> ALT A, GT 0/1
    assert records == ["1\t3\trs999\tG\tA\t.\tPASS\t.\tGT\t0/1"]

    # Direct Python API call passing pathlib.Path objects for fasta_override and cache_path
    out_vcf_pathobj = tmp_path / "out" / "sample_pathobj.vcf"
    api_res = converter.run_conversion_pipeline(
        raw,
        "female",
        "GRCh38",
        {},
        output_path=out_vcf_pathobj,
        fasta_override=fasta_path,
        cache_path=cache_path,
    )
    assert api_res is not None and api_res["written"] == 1

    # Output protection must reject overwriting --fasta or --cache
    overwrite_fasta = converter.main(
        [
            "--input",
            str(raw),
            "--output",
            str(fasta_path),
            "--build",
            "GRCh38",
            "--sex",
            "female",
            "--fasta",
            str(fasta_path),
            "--cache",
            str(cache_path),
        ]
    )
    capsys.readouterr()
    assert overwrite_fasta == 1
    assert fasta_path.read_bytes() == b">1\nACGTACGTAC\n"

    overwrite_cache = converter.main(
        [
            "--input",
            str(raw),
            "--output",
            str(cache_path),
            "--build",
            "GRCh38",
            "--sex",
            "female",
            "--fasta",
            str(fasta_path),
            "--cache",
            str(cache_path),
        ]
    )
    capsys.readouterr()
    assert overwrite_cache == 1


def test_headless_import_and_cli_succeed_without_pyside6_or_psutil(tmp_path):
    import subprocess
    import sys

    raw = tmp_path / "headless.tsv"
    raw.write_text("rs1\t1\t2\tCT\n", encoding="utf-8")
    fasta = tmp_path / "mini.fa"
    fasta.write_bytes(b">1\nACGT\n")
    (tmp_path / "mini.fa.fai").write_text("1\t4\t3\t4\t5\n", encoding="utf-8")
    cache_file = tmp_path / "cache.json"
    out_vcf = tmp_path / "headless.vcf"

    repo_root = Path(__file__).resolve().parents[1]
    script = f"""
import builtins
import sys

real_import = builtins.__import__
def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "psutil" or name == "PySide6" or name.startswith("PySide6."):
        raise ImportError(f"Simulated headless environment missing {{name}}")
    return real_import(name, globals, locals, fromlist, level)

builtins.__import__ = blocked_import
sys.path.insert(0, {str(repo_root)!r})

import Make23toVCF3 as conv
assert conv.PYSIDE6_AVAILABLE is False

rc_preflight = conv.main(["--input", {str(raw)!r}, "--preflight", "--json"])
assert rc_preflight == 0

rc_conv = conv.main([
    "--input", {str(raw)!r},
    "--output", {str(out_vcf)!r},
    "--build", "GRCh37",
    "--sex", "female",
    "--fasta", {str(fasta)!r},
    "--cache", {str(cache_file)!r},
])
assert rc_conv == 0

rc_gui = conv.main(["--gui"])
assert rc_gui == 1
print("HEADLESS_NO_QT_OK")
"""
    proc = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", "-c", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
    )
    assert proc.returncode == 0, f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    assert "HEADLESS_NO_QT_OK" in proc.stdout
    assert "PySide6" in proc.stderr
    records = [
        line
        for line in out_vcf.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    assert records == ["1\t2\trs1\tC\tT\t.\tPASS\t.\tGT\t0/1"]
