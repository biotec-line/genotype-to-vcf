from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Make23toVCF3 as converter


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


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="23tovcf-smoke-") as temp_dir:
        tmp_dir = Path(temp_dir)
        run_cli_write_smoke(tmp_dir)
        run_detect_build_smoke(tmp_dir)
    print("source platform smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
