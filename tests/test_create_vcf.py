from pathlib import Path

import Make23toVCF3 as converter


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
