import Make23toVCF3 as converter


def test_parse_genotype_file_accepts_quoted_csv_rows(tmp_path):
    raw = tmp_path / "quoted-provider-export.csv"
    raw.write_text(
        '"rsid","chromosome","position","genotype"\n'
        '"rs123","chr1","12345","AG"\n',
        encoding="utf-8",
    )

    assert converter.parse_genotype_file(str(raw)) == [("rs123", "1", 12345, "AG")]


def test_parse_genotype_file_normalizes_uppercase_chr_prefix(tmp_path):
    raw = tmp_path / "uppercase-chr.tsv"
    raw.write_text("rs456\tCHR2\t67890\tCC\n", encoding="utf-8")

    assert converter.parse_genotype_file(str(raw)) == [("rs456", "2", 67890, "CC")]
