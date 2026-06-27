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


def test_parse_genotype_file_normalizes_lowercase_genotype(tmp_path):
    raw = tmp_path / "lowercase-genotype.tsv"
    raw.write_text("rs789\t3\t13579\tag\n", encoding="utf-8")

    assert converter.parse_genotype_file(str(raw)) == [("rs789", "3", 13579, "AG")]


def test_parse_genotype_file_latin1_fallback(tmp_path):
    """Bug B: Datei in latin-1-Encoding soll ohne UnicodeDecodeError gelesen werden.

    Einige FTDNA-Exporte enthalten Kommentarzeilen mit Umlauten in Windows-ANSI
    (latin-1/cp1252). Das bisherige utf-8-sig-Opening warf UnicodeDecodeError.
    """
    raw = tmp_path / "ftdna_latin1.txt"
    # Kopfzeile mit Umlaut in latin-1: "# Erstellt von Anbieter Müller"
    content = b"# Erstellt von Anbieter M\xfcller\nrs123\t1\t12345\tAG\n"
    raw.write_bytes(content)

    result = converter.parse_genotype_file(str(raw))
    assert result == [("rs123", "1", 12345, "AG")]
