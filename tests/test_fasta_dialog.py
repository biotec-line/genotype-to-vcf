import Make23toVCF3 as converter


class LogSignal:
    def __init__(self):
        self.messages = []

    def emit(self, message):
        self.messages.append(message)


def test_missing_fasta_uses_callable_ask_callback(tmp_path):
    original_paths = dict(converter.FASTA_PATHS)
    calls = []

    def ask(title, message):
        calls.append((title, message))
        return False

    try:
        converter.FASTA_PATHS["GRCh38"] = str(tmp_path / "missing.fa")

        result = converter.ensure_fasta_with_choice(
            "GRCh38",
            LogSignal(),
            ask,
        )
    finally:
        converter.FASTA_PATHS.clear()
        converter.FASTA_PATHS.update(original_paths)

    assert result is None
    assert calls
    assert calls[0][0] == "Referenz laden?"
    assert "GRCh38" in calls[0][1]


def test_fasta_paths_are_build_specific():
    assert converter.FASTA_PATHS["GRCh37"] != converter.FASTA_PATHS["GRCh38"]
    assert "GRCh37" in converter.FASTA_PATHS["GRCh37"]
    assert "GRCh38" in converter.FASTA_PATHS["GRCh38"]


def test_fetch_base_from_fasta_supports_mt_aliases(tmp_path):
    chrm_fasta = tmp_path / "chrM.fa"
    chrm_fasta.write_text(
        ">chrM\n"
        "ACGT\n",
        encoding="ascii",
    )

    converter.build_fasta_index(str(chrm_fasta))
    chrm_fai = converter.load_fai_index(str(chrm_fasta) + ".fai")
    assert converter.fetch_base_from_fasta(str(chrm_fasta), chrm_fai, "MT", 1) == "A"

    mt_fasta = tmp_path / "MT.fa"
    mt_fasta.write_text(
        ">MT\n"
        "TGCA\n",
        encoding="ascii",
    )

    converter.build_fasta_index(str(mt_fasta))
    mt_fai = converter.load_fai_index(str(mt_fasta) + ".fai")
    assert converter.fetch_base_from_fasta(str(mt_fasta), mt_fai, "chrM", 1) == "T"
