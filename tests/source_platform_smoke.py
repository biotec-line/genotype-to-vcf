from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Make23toVCF3 as converter
from manage_translations import check_translations


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_cli_write_smoke(tmp_dir: Path) -> None:
    raw = tmp_dir / "sample.tsv"
    raw.write_text("rs1\t1\t100\tAG\n", encoding="utf-8")
    out_path = tmp_dir / "sample.vcf"
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

    original_load_cache = converter.load_cache
    original_resolve_fasta = converter.resolve_fasta_path_for_run

    try:
        converter.load_cache = lambda path=converter.CACHE_FILE: cache
        converter.resolve_fasta_path_for_run = lambda *args, **kwargs: None

        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
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
    finally:
        converter.load_cache = original_load_cache
        converter.resolve_fasta_path_for_run = original_resolve_fasta

    _assert(exit_code == 0, f"CLI conversion returned {exit_code}.\nSTDERR:\n{stderr.getvalue()}")
    _assert(out_path.exists(), "VCF output file was not created.")
    records = [
        line
        for line in out_path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    _assert(
        records == ["1\t100\trs1\tA\tG\t.\tPASS\t.\tGT\t0/1"],
        f"Unexpected VCF records: {records!r}",
    )
    _assert("VCF geschrieben." in stdout.getvalue(), "CLI success message missing.")
    _assert(str(out_path) not in stdout.getvalue(), "CLI stdout must not expose the output path.")


def run_detect_build_smoke(tmp_dir: Path) -> None:
    raw = tmp_dir / "sample-detect.tsv"
    raw.write_text("rs1\t1\t100\tAG\n", encoding="utf-8")

    original_load_cache = converter.load_cache
    original_detect_build = converter.detect_build_robust

    try:
        converter.load_cache = lambda path=converter.CACHE_FILE: {}
        converter.detect_build_robust = (
            lambda variants, cache, signal_callback, stop_event: "GRCh38"
        )

        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = converter.main(["--input", str(raw), "--detect-build"])
    finally:
        converter.load_cache = original_load_cache
        converter.detect_build_robust = original_detect_build

    _assert(exit_code == 0, f"Build detection returned {exit_code}.\nSTDERR:\n{stderr.getvalue()}")
    _assert(stdout.getvalue().strip() == "GRCh38", "Detected build output mismatch.")


def run_preflight_smoke(tmp_dir: Path) -> None:
    raw = tmp_dir / "sample-preflight.csv"
    raw.write_text(
        "# synthetic preflight\n"
        "rs_id;chromosome;position;genotype\n"
        '"rs10";"23";"60005";"ag"\n'
        "rs11;26;73;tt\n",
        encoding="utf-8",
    )
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = converter.main(["--input", str(raw), "--preflight", "--json"])
    _assert(exit_code == 0, f"Preflight returned {exit_code}.\nSTDERR:\n{stderr.getvalue()}")
    payload = json.loads(stdout.getvalue())
    _assert(payload["compatible"] is True, "Preflight compatible flag must be True.")
    _assert(payload["valid_records"] == 2, f"Expected 2 valid records, got {payload}")
    _assert(payload["chromosomes"] == {"X": 1, "MT": 1}, f"Unexpected chromosomes: {payload}")
    _assert(str(raw) not in stdout.getvalue(), "Preflight JSON must not leak input file paths.")
    _assert("rs10" not in stdout.getvalue(), "Preflight JSON must not leak rsIDs.")


def run_workstation_fasta_cache_smoke(tmp_dir: Path) -> None:
    fasta_path = tmp_dir / "refs" / "mini.fa"
    fasta_path.parent.mkdir(parents=True, exist_ok=True)
    fasta_path.write_bytes(b">1\nACGT\n")
    (tmp_dir / "refs" / "mini.fa.fai").write_text("1\t4\t3\t4\t5\n", encoding="utf-8")
    cache_path = tmp_dir / "cache" / "workstation_cache.json"
    raw = tmp_dir / "sample-ws.tsv"
    raw.write_text("rs77\t1\t4\tTA\n", encoding="utf-8")
    out_vcf = tmp_dir / "out-ws.vcf"

    ver_out = io.StringIO()
    with contextlib.redirect_stdout(ver_out):
        ver_rc = converter.main(["--version"])
    _assert(ver_rc == 0 and converter.APP_VERSION in ver_out.getvalue(), "--version check failed.")

    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        rc = converter.main(
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
    _assert(rc == 0, f"Workstation --fasta/--cache conversion failed: {stderr.getvalue()}")
    records = [
        line
        for line in out_vcf.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    _assert(
        records == ["1\t4\trs77\tT\tA\t.\tPASS\t.\tGT\t0/1"],
        f"Unexpected workstation VCF records: {records!r}",
    )


def run_qt_free_headless_subprocess_smoke(tmp_dir: Path) -> None:
    raw = tmp_dir / "noqt.tsv"
    raw.write_text("rs1\t1\t1\tAG\n", encoding="utf-8")
    script = (
        "import builtins, sys\n"
        "real_import = builtins.__import__\n"
        "def guard(name, *a, **kw):\n"
        "    if name == 'psutil' or name == 'PySide6' or name.startswith('PySide6.'):\n"
        "        raise ImportError(name)\n"
        "    return real_import(name, *a, **kw)\n"
        "builtins.__import__ = guard\n"
        f"sys.path.insert(0, {str(PROJECT_ROOT)!r})\n"
        "import Make23toVCF3 as c\n"
        "assert c.PYSIDE6_AVAILABLE is False\n"
        f"assert c.main(['--input', {str(raw)!r}, '--preflight', '--json']) == 0\n"
    )
    proc = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", "-c", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
    )
    _assert(
        proc.returncode == 0,
        f"Qt-free headless smoke failed ({proc.returncode}):\n{proc.stderr}",
    )


def run_translation_and_web_demo_parity_smoke() -> None:
    report = check_translations(str(PROJECT_ROOT))
    _assert(bool(report.get("ok")), f"Translation parity check failed: {report.get('missing')}")
    node_bin = shutil.which("node")
    if node_bin:
        proc = subprocess.run(
            [node_bin, "--test", str(PROJECT_ROOT / "tests" / "test_browser_local_demo.mjs")],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        _assert(
            proc.returncode == 0,
            f"Browser-local demo Node tests failed:\n{proc.stdout}\n{proc.stderr}",
        )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="23tovcf-smoke-") as temp_dir:
        tmp_dir = Path(temp_dir)
        run_cli_write_smoke(tmp_dir)
        run_detect_build_smoke(tmp_dir)
        run_preflight_smoke(tmp_dir)
        run_workstation_fasta_cache_smoke(tmp_dir)
        run_qt_free_headless_subprocess_smoke(tmp_dir)
        run_translation_and_web_demo_parity_smoke()
    print("source platform smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
