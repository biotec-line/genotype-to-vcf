import threading
from pathlib import Path

import Make23toVCF3 as converter


def test_create_vcf_no_crash_when_signal_callback_none_and_stop_set(tmp_path):
    """Bug A: create_vcf darf nicht AttributeError werfen wenn signal_callback=None und stop_event gesetzt."""
    out_path = tmp_path / "out.vcf"
    # Erzeuge Varianten die den idx%1000==0 Zweig erreichen
    variants = [(f"rs{i}", "1", i, "AG") for i in range(1, 1002)]
    cache = {
        f"rs{i}": {"assemblies": {"GRCh37": {"chrom": "1", "pos": i, "ref": "A"}}}
        for i in range(1, 1002)
    }
    stop = threading.Event()
    stop.set()

    # Darf keinen AttributeError werfen (signal_callback=None ist der Default)
    result = converter.create_vcf(
        variants,
        "GRCh37",
        str(out_path),
        cache,
        stop_event=stop,
    )
    assert result == 0, "Abbruch bei stop_event soll 0 zurückgeben"


def test_create_vcf_accepts_lowercase_genotype(tmp_path):
    out_path = tmp_path / "out.vcf"
    variants = [("rs1", "1", 100, "ag")]
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

    written = converter.create_vcf(
        variants,
        "GRCh37",
        str(out_path),
        cache,
        sex="unknown",
    )

    assert written == 1
    records = [
        line
        for line in Path(out_path).read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    assert records == ["1\t100\trs1\tA\tG\t.\tPASS\t.\tGT\t0/1"]
