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


def test_create_vcf_i_type_snp_resolved_from_cache(tmp_path):
    """Bug C: i-Typ-SNP (interne 23andMe-ID) soll geschrieben werden, wenn die
    rs-ID per Position aus dem Cache auflösbar ist.

    Bisher wurde get_ref() mit der i-ID aufgerufen (nie im Cache) → ref_base='N'
    → continue, bevor das i→rs-Mapping lief. Fix: Mapping VOR get_ref() ausführen.
    """
    out_path = tmp_path / "out.vcf"
    variants = [("i7002762", "1", 500, "CT")]
    cache = {
        "rs123456": {
            "assemblies": {
                "GRCh37": {"chrom": "1", "pos": 500, "ref": "C"}
            }
        }
    }

    written = converter.create_vcf(variants, "GRCh37", str(out_path), cache, sex="unknown")

    assert written == 1, "i-Typ-SNP mit auflösbarer rs-ID soll als VCF-Eintrag geschrieben werden"
    records = [
        line
        for line in Path(out_path).read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    assert len(records) == 1
    fields = records[0].split("\t")
    assert fields[2] == "rs123456", "rsid soll auf rs123456 gemappt sein"
    assert "I_ID=i7002762" in fields[7], "INFO soll Original-ID als I_ID enthalten"
    assert fields[9] == "0/1", "Genotyp CT mit Ref C soll 0/1 ergeben"


def test_create_vcf_hemizygous_het_call_skipped(tmp_path):
    """Bug A: Heterozygote Genotypen auf haploiden Stellen (z.B. chrY, male)
    sind Probe-Artefakte und sollen übersprungen werden.

    Bisher: 'AG' auf ploid=1-Stelle → ALT='G', GT='0' (inkonsistenter VCF-Eintrag).
    Nach Fix: Het-Call auf ploid=1 wird als no-call behandelt → kein Eintrag.
    """
    out_path = tmp_path / "out.vcf"
    variants = [("rs1", "Y", 2_700_000, "AG")]  # Position außerhalb PAR1/PAR2
    cache = {
        "rs1": {
            "assemblies": {
                "GRCh37": {"chrom": "Y", "pos": 2_700_000, "ref": "A"}
            }
        }
    }

    written = converter.create_vcf(variants, "GRCh37", str(out_path), cache, sex="male")

    assert written == 0, "Heterozygote Genotypen auf haploiden chrY-Stellen sollen übersprungen werden"


def test_create_vcf_hemizygous_homozygous_alt_written(tmp_path):
    """Komplementärtest zu test_create_vcf_hemizygous_het_call_skipped:
    Homozygote Alt-Calls auf ploid=1-Stellen sollen korrekt als GT '1' erscheinen.
    """
    out_path = tmp_path / "out.vcf"
    variants = [("rs2", "Y", 2_700_000, "GG")]  # homozygot alt
    cache = {
        "rs2": {
            "assemblies": {
                "GRCh37": {"chrom": "Y", "pos": 2_700_000, "ref": "A"}
            }
        }
    }

    written = converter.create_vcf(variants, "GRCh37", str(out_path), cache, sex="male")

    assert written == 1
    records = [
        line
        for line in Path(out_path).read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    assert len(records) == 1
    assert records[0].split("\t")[9] == "1", "Homozygot-Alt 'GG' auf ploid=1 soll GT '1' ergeben"
