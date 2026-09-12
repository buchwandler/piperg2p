import sys
import warnings

import pytest

from piperg2p import (
    BackendFallbackWarning,
    BackendUnavailableError,
    EspeakBackend,
    EspeakCliBackend,
    NativeEspeakProvider,
)
from piperg2p.backends.espeak.clauses import (
    Clause,
    compose_clauses,
    merge_vowel_clusters,
)
from piperg2p.backends.espeak.discovery import discover


def test_clause_composition_preserves_punctuation_and_normalizes():
    clauses = [
        Clause("a", ",", False),
        Clause("e", ".", True),
        Clause("?", None, True),
    ]
    assert compose_clauses(clauses) == [["a", ",", " ", "e", "."], ["?"]]


def test_clause_composition_removes_switches_and_merges_longest():
    assert merge_vowel_clusters(
        ["a", "b", "c"], frozenset({("a", "b"), ("a", "b", "c")})
    ) == ["abc"]
    assert compose_clauses([Clause("a(b)\u0301", None, False)], frozenset()) == [
        ["a", "\u0301"]
    ]


def test_discovery_finds_explicit_executable(tmp_path):
    executable = tmp_path / "espeak"
    executable.write_text("", encoding="utf-8")
    assert discover(executable=str(executable)).executable == str(executable)
    with pytest.raises(BackendUnavailableError):
        discover(executable=str(tmp_path / "missing"))


def test_cli_backend_uses_utf8_and_reports_best_effort(monkeypatch):
    executable = sys.executable
    calls = []

    class Process:
        returncode = 0
        stdout = "hɛlə"
        stderr = ""

    def run(args, **kwargs):
        calls.append((args, kwargs))
        return Process()

    monkeypatch.setattr("subprocess.run", run)
    backend = EspeakCliBackend(executable=executable)
    assert backend.phonemize("hé", voice="en-us") == [["h", "ɛ", "l", "ə"]]
    assert calls[0][1]["encoding"] == "utf-8"
    assert backend.diagnostics.parity == "best-effort"


def test_native_provider_can_initialize_if_library_is_installed():
    try:
        provider = NativeEspeakProvider()
    except BackendUnavailableError:
        pytest.skip("native eSpeak library unavailable")
    try:
        clauses = provider.clauses("Hello, world.", "en-us")
        assert clauses
        assert provider.diagnostics.version
        if provider.diagnostics.exact_clause_api:
            assert clauses[0].terminator == ","
            assert clauses[-1].sentence_end
        else:
            assert provider.diagnostics.parity == "best-effort"
    finally:
        provider.close()


def test_auto_backend_prefers_native_or_diagnoses_cli():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        backend = EspeakBackend(mode="auto")
    assert backend.diagnostics.parity in {"exact", "best-effort"}
    if backend.diagnostics.parity == "best-effort":
        assert any(issubclass(item.category, BackendFallbackWarning) for item in caught)
    backend.close()
