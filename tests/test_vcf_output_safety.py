"""Synthetic, offline tests for VCF publication and source preservation."""
import ctypes
import os
import shutil
import stat
import subprocess
import tempfile
import threading
from pathlib import Path

import pytest

import Make23toVCF3 as converter


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    src, dst = tmp_path / "raw.tsv", tmp_path / "result.vcf"
    src.write_bytes(b"rs1\t1\t100\tAG\n")
    dst.write_bytes(b"old-output")
    cache_path = tmp_path / "state-cache.json"
    cache_path.write_bytes(b"original-cache")
    reference = tmp_path / "reference.fa"
    reference.write_bytes(b"ACGT\n")
    Path(str(reference) + ".fai").write_bytes(b"1\t4\t0\t4\t5\n")
    Path(str(reference) + ".gz").write_bytes(b"original-compressed")
    cache = {"rs1": {"assemblies": {"GRCh37": {"chrom": "1", "pos": 100, "ref": "A"}}}}
    monkeypatch.setattr(converter, "CACHE_FILE", str(cache_path))
    monkeypatch.setattr(converter, "FASTA_PATHS", {"GRCh37": str(reference)})
    monkeypatch.setattr(converter, "resolve_fasta_path_for_run", lambda *a, **k: None)
    monkeypatch.setattr(converter, "load_cache", lambda *a, **k: cache)
    def no_network(*args, **kwargs):
        pytest.fail("Network is excluded from these tests")
    monkeypatch.setattr(converter, "adaptive_parallel_fetch", no_network)
    monkeypatch.setattr(converter.requests, "get", no_network)
    initial = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    yield src, dst, cache, initial
    for path in tmp_path.iterdir():
        if path.is_file():
            path.chmod(stat.S_IREAD | stat.S_IWRITE)


def originals_unchanged(fixture):
    src, _, _, initial = fixture
    assert {path.name: path.read_bytes() for path in src.parent.iterdir()} == initial


def pipeline(fixture, **kwargs):
    src, dst, cache, _ = fixture
    return converter.run_conversion_pipeline(str(src), "female", "GRCh37", cache,
                                              output_path=str(dst), **kwargs)


def test_pipeline_overwrites_existing_result_after_complete_write(fixture):
    result = pipeline(fixture)
    assert result["written"] == 1
    assert fixture[0].read_bytes() == b"rs1\t1\t100\tAG\n"
    assert fixture[1].read_bytes().startswith(b"##fileformat=VCFv4.2")
    assert {path.name for path in fixture[0].parent.iterdir()} == set(fixture[3])


@pytest.mark.parametrize("alias", ["direct", "relative", "hardlink"])
def test_raw_input_alias_rejected(fixture, monkeypatch, alias):
    src, _, cache, _ = fixture
    target = src
    if alias == "relative":
        monkeypatch.chdir(src.parent)
        target = Path("raw.tsv")
    elif alias == "hardlink":
        target = src.parent / "hardlink.vcf"
        os.link(src, target)
    inode = src.stat().st_ino
    with pytest.raises((ValueError, shutil.SameFileError)):
        converter.run_conversion_pipeline(str(src), "female", "GRCh37", cache, output_path=str(target))
    assert src.read_bytes() == b"rs1\t1\t100\tAG\n" and src.stat().st_ino == inode
    assert not list(src.parent.glob(".vcf-*.tmp"))


@pytest.mark.parametrize("protected", ["state-cache.json", "reference.fa", "reference.fa.fai", "reference.fa.gz"])
@pytest.mark.parametrize("exists", [True, False])
def test_reserved_resource_paths_rejected_before_reference_work(fixture, monkeypatch, protected, exists):
    src, _, cache, initial = fixture
    target = src.parent / protected
    if not exists:
        target.unlink()
    def forbidden(*a, **k):
        pytest.fail("Protected destination must fail before reference/API work")
    monkeypatch.setattr(converter, "resolve_fasta_path_for_run", forbidden)
    with pytest.raises((ValueError, shutil.SameFileError)):
        converter.run_conversion_pipeline(str(src), "female", "GRCh37", cache, output_path=str(target))
    assert src.read_bytes() == initial[src.name]
    if exists:
        assert target.read_bytes() == initial[protected]
    else:
        assert not target.exists()


@pytest.mark.parametrize("cancel_at", ["entry", "first-progress", "final-progress"])
def test_pipeline_cancel_keeps_previous_result(fixture, cancel_at):
    stop = threading.Event()
    if cancel_at == "entry":
        stop.set()
    def progress(value):
        if (cancel_at == "first-progress" and value == 0) or (cancel_at == "final-progress" and value == 100):
            stop.set()
    result = pipeline(fixture, stop_event=stop, progress_signal=converter.CallbackSignal(progress))
    assert result is None
    originals_unchanged(fixture)


@pytest.mark.parametrize("variants", [[], [("rs1", "1", 100, "AG")]])
def test_direct_writer_cancel_returns_zero_without_publishing(fixture, variants):
    stop = threading.Event()
    stop.set()
    assert converter.create_vcf(variants, "GRCh37", str(fixture[1]), fixture[2], stop_event=stop) == 0
    originals_unchanged(fixture)


def test_zero_valid_records_without_cancel_is_success(fixture):
    count = converter.create_vcf([("rs1", "1", 100, "--")], "GRCh37", str(fixture[1]), fixture[2])
    assert count == 0
    assert fixture[1].read_bytes().startswith(b"##fileformat=VCFv4.2")


def test_bad_record_after_valid_record_preserves_previous_result(fixture):
    variants = [("rs1", "1", 100, "AG"), ("rs2", "1", 101, None)]
    with pytest.raises(AttributeError):
        converter.create_vcf(variants, "GRCh37", str(fixture[1]), fixture[2])
    originals_unchanged(fixture)


def test_replace_failure_preserves_error_and_previous_result(fixture, monkeypatch):
    error = PermissionError("synthetic publish failure")
    def fail(*a):
        raise error
    monkeypatch.setattr(converter.os, "replace", fail)
    with pytest.raises(PermissionError) as caught:
        pipeline(fixture)
    assert caught.value is error
    originals_unchanged(fixture)


def test_progress_error_preserves_original_error_and_result(fixture):
    error = RuntimeError("callback failure")
    def fail(value):
        raise error
    with pytest.raises(RuntimeError) as caught:
        pipeline(fixture, progress_signal=converter.CallbackSignal(fail))
    assert caught.value is error
    originals_unchanged(fixture)


def test_late_input_alias_before_publication_rejected(fixture):
    src, dst, _, initial = fixture
    def alias_at_100(value):
        if value == 100:
            dst.unlink()
            os.link(src, dst)
    with pytest.raises((ValueError, shutil.SameFileError)):
        pipeline(fixture, progress_signal=converter.CallbackSignal(alias_at_100))
    assert os.path.samefile(src, dst)
    assert src.read_bytes() == initial[src.name]
    assert {path.name for path in src.parent.iterdir()} == set(initial)


def test_final_progress_is_emitted_once(fixture):
    values = []
    assert pipeline(fixture, progress_signal=converter.CallbackSignal(values.append))["written"] == 1
    assert values.count(100) == 1


def test_cancel_during_last_identity_check_does_not_publish(fixture, monkeypatch):
    stop = threading.Event()
    final_phase = threading.Event()
    original_stat = os.stat
    def progress(value):
        if value == 100:
            final_phase.set()
    def checking(path, *args, **kwargs):
        result = original_stat(path, *args, **kwargs)
        if final_phase.is_set():
            stop.set()
        return result
    monkeypatch.setattr(converter.os, "stat", checking)
    assert pipeline(fixture, stop_event=stop, progress_signal=converter.CallbackSignal(progress)) is None
    originals_unchanged(fixture)


@pytest.mark.parametrize("failure", ["write", "flush", "close", "fdopen", "reserve"])
def test_stage_io_fault_keeps_primary_error_and_originals(fixture, monkeypatch, failure):
    error = OSError("stage IO fault")
    original_fdopen = os.fdopen
    class FaultStream:
        def __init__(self, stream):
            self.stream = stream
        def write(self, value):
            if failure == "write":
                self.stream.write(value[:5])
                raise error
            return self.stream.write(value)
        def flush(self):
            if failure == "flush":
                raise error
            self.stream.flush()
        def close(self):
            already_closed = self.stream.closed
            self.stream.close()
            if failure == "close" and not already_closed:
                raise error
    def faulty_fdopen(*args, **kwargs):
        if failure == "fdopen":
            raise error
        return FaultStream(original_fdopen(*args, **kwargs))
    def fail_reservation(**kwargs):
        raise error
    if failure == "reserve":
        monkeypatch.setattr(tempfile, "mkstemp", fail_reservation)
    else:
        monkeypatch.setattr(os, "fdopen", faulty_fdopen)
    with pytest.raises(OSError) as caught:
        pipeline(fixture)
    assert caught.value is error
    originals_unchanged(fixture)


def test_identity_permission_error_is_not_assumed_distinct(fixture, monkeypatch):
    original_stat = os.stat
    error = PermissionError("protected identity")
    def denied(path, *args, **kwargs):
        if os.fspath(path) == converter.CACHE_FILE:
            raise error
        return original_stat(path, *args, **kwargs)
    monkeypatch.setattr(os, "stat", denied)
    try:
        with pytest.raises(PermissionError) as caught:
            pipeline(fixture)
    finally:
        monkeypatch.setattr(os, "stat", original_stat)
    assert caught.value is error
    originals_unchanged(fixture)


@pytest.mark.parametrize("kind", ["raw", "reference", "cache"])
def test_symlink_to_protected_original_rejected(fixture, kind):
    src, _, cache, initial = fixture
    protected = src if kind == "raw" else src.parent / ("reference.fa" if kind == "reference" else "state-cache.json")
    target = src.parent / "linked.vcf"
    try:
        target.symlink_to(protected)
    except OSError as error:
        if os.name == "nt" and error.winerror == 1314:
            pytest.skip("Windows symlink privilege unavailable (1314)")
        raise
    with pytest.raises((ValueError, shutil.SameFileError)):
        converter.run_conversion_pipeline(str(src), "female", "GRCh37", cache, output_path=str(target))
    assert target.is_symlink() and protected.read_bytes() == initial[protected.name]
    assert not list(src.parent.glob(".vcf-*.tmp"))


@pytest.mark.skipif(os.name != "nt", reason="Windows namespace aliases")
@pytest.mark.parametrize("suffix", [".", " ", ":vcf"])
def test_windows_input_name_alias_rejected(fixture, suffix):
    src, _, cache, _ = fixture
    with pytest.raises((ValueError, shutil.SameFileError)):
        converter.run_conversion_pipeline(str(src), "female", "GRCh37", cache, output_path=str(src) + suffix)
    originals_unchanged(fixture)


@pytest.mark.skipif(os.name != "nt", reason="Native Windows sharing denial")
def test_sharing_denial_keeps_original_result(fixture):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    create.restype = ctypes.c_void_p
    close = kernel.CloseHandle
    close.argtypes = [ctypes.c_void_p]
    close.restype = ctypes.c_int
    handle = create(str(fixture[1]), 0x80000000, 3, None, 3, 0x80, None)
    assert handle not in (None, ctypes.c_void_p(-1).value)
    try:
        with pytest.raises(OSError) as caught:
            pipeline(fixture)
        assert caught.value.winerror in (5, 32)
        originals_unchanged(fixture)
    finally:
        assert close(handle)


def test_unrelated_legacy_temporary_names_preserved(fixture):
    src, dst, _, _ = fixture
    foreign = Path(str(dst) + ".tmp")
    foreign.write_bytes(b"foreign-output")
    pipeline(fixture)
    assert foreign.read_bytes() == b"foreign-output"
    assert len(list(src.parent.iterdir())) == len(fixture[3]) + 1


def test_cli_same_input_output_fails_without_cache_or_network_work(fixture, monkeypatch, capsys):
    def forbidden(*a, **k):
        pytest.fail("Invalid explicit destination must fail before cache initialization")
    monkeypatch.setattr(converter, "load_cache", forbidden)
    rc = converter.main(["--input", str(fixture[0]), "--output", str(fixture[0]),
                         "--build", "GRCh37", "--sex", "female"])
    assert rc != 0
    assert "VCF geschrieben" not in capsys.readouterr().out
    originals_unchanged(fixture)


def test_worker_none_result_is_cancelled_not_error_or_success(fixture, monkeypatch):
    monkeypatch.setattr(converter, "run_conversion_pipeline", lambda *a, **k: None)
    worker = converter.ConversionWorker(str(fixture[0]), "female", "GRCh37", fixture[2])
    finished, errors, logs = [], [], []
    worker.finished_signal.connect(finished.append)
    worker.error_signal.connect(errors.append)
    worker.log_signal.connect(logs.append)
    worker.run()
    assert not finished and not errors and any("abgebrochen" in text for text in logs)


def test_worker_completed_publication_survives_late_stop(fixture, monkeypatch):
    worker = converter.ConversionWorker(str(fixture[0]), "female", "GRCh37", fixture[2])
    def committed(*a, **k):
        worker.is_interrupted.set()
        return {"written": 1, "output_path": str(fixture[1])}
    monkeypatch.setattr(converter, "run_conversion_pipeline", committed)
    finished, errors = [], []
    worker.finished_signal.connect(finished.append)
    worker.error_signal.connect(errors.append)
    worker.run()
    assert len(finished) == 1 and not errors


@pytest.mark.skipif(os.name != "nt", reason="Native Windows readonly destination")
def test_readonly_destination_failure_keeps_attributes(fixture):
    dst = fixture[1]
    dst.chmod(stat.S_IREAD)
    mode = dst.stat().st_mode
    with pytest.raises(PermissionError):
        pipeline(fixture)
    originals_unchanged(fixture)
    assert dst.stat().st_mode == mode


@pytest.mark.skipif(os.name != "nt", reason="Native Windows junction alias")
def test_parent_junction_input_alias(fixture):
    src, _, cache, _ = fixture
    alias = src.parent.parent / (src.parent.name + "-junction")
    result = subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(src.parent)], capture_output=True, check=False)
    assert result.returncode == 0
    try:
        with pytest.raises((ValueError, shutil.SameFileError)):
            converter.run_conversion_pipeline(str(src), "female", "GRCh37", cache,
                                              output_path=str(alias / src.name))
        originals_unchanged(fixture)
    finally:
        os.rmdir(alias)


def test_parallel_vcf_writers_use_different_private_stages(fixture, monkeypatch):
    src, dst, cache, initial = fixture
    barrier = threading.Barrier(2)
    stages, completed, errors = [], [], []
    original_replace = os.replace
    def blocked_replace(stage, target):
        stages.append(Path(stage))
        barrier.wait(timeout=10)
        original_replace(stage, target)
    monkeypatch.setattr(converter.os, "replace", blocked_replace)
    def write(genotype):
        try:
            count = converter.create_vcf([("rs1", "1", 100, genotype)], "GRCh37", str(dst), cache)
            completed.append(genotype)
            assert count == 1
        except (OSError, AssertionError, threading.BrokenBarrierError) as error:
            errors.append(error)
    threads = [threading.Thread(target=write, args=(gt,)) for gt in ("AG", "AA")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)
    assert all(not thread.is_alive() for thread in threads)
    assert len(stages) == 2 and stages[0] != stages[1]
    assert completed
    assert all(os.name == "nt" and isinstance(e, OSError) and e.winerror in (5, 32) for e in errors)
    records = [line for line in dst.read_text().splitlines() if not line.startswith("#")]
    assert len(records) == 1
    assert (records[0].endswith("0/1") and "AG" in completed) or (records[0].endswith("0/0") and "AA" in completed)
    assert src.read_bytes() == initial[src.name]
    assert {path.name for path in src.parent.iterdir()} == set(initial)


@pytest.mark.parametrize("resource", ["cache", "reference-index"])
@pytest.mark.parametrize("entry", ["pipeline", "public-writer"])
def test_resource_reconfiguration_does_not_unprotect_initial_path(fixture, monkeypatch, resource, entry):
    src, dst, cache, initial = fixture
    if resource == "cache":
        original = Path(converter.CACHE_FILE)
    else:
        original = Path(converter.FASTA_PATHS["GRCh37"] + ".fai")

    def reconfigure(progress):
        if progress != 100:
            return
        dst.unlink()
        os.link(original, dst)
        if resource == "cache":
            monkeypatch.setattr(converter, "CACHE_FILE", str(src.parent / "new-cache.json"))
        else:
            monkeypatch.setattr(converter, "FASTA_PATHS", {"GRCh37": str(src.parent / "new-reference.fa")})

    progress = converter.CallbackSignal(reconfigure)
    with pytest.raises((ValueError, shutil.SameFileError)):
        if entry == "pipeline":
            pipeline(fixture, progress_signal=progress)
        else:
            converter.create_vcf([("rs1", "1", 100, "AG")], "GRCh37", str(dst), cache,
                                 progress_signal=progress)
    assert os.path.samefile(original, dst)
    assert dst.read_bytes() == initial[original.name]
    for name, content in initial.items():
        if name != dst.name:
            assert (src.parent / name).read_bytes() == content
    assert {path.name for path in src.parent.iterdir()} == set(initial)
