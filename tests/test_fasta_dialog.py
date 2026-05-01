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
