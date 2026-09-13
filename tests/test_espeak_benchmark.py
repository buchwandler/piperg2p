from __future__ import annotations

import subprocess
import types
from pathlib import Path

from benchmarks.reference.compare import compare_case, metrics
from benchmarks.reference.espeak import EspeakReference


def test_reference_uses_independent_ipa3_command(monkeypatch):
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return types.SimpleNamespace(returncode=0, stdout="həˈləʊ\n", stderr="")

    monkeypatch.setattr(subprocess, "run", run)
    reference = EspeakReference("/usr/bin/espeak")
    result = reference.run("hello", voice="en-us")
    assert any("--ipa=3" in command for command, _ in calls)
    assert any("--stdin" in command for command, _ in calls)
    assert any(kwargs.get("input") == "hello\n" for _, kwargs in calls)
    assert result.raw == "həˈləʊ"


def test_comparison_reports_symbol_metrics():
    values = [
        compare_case("same", "abc", "abc"),
        compare_case("different", "abc", "adc"),
    ]
    result = metrics(values)
    assert result["cases_total"] == 2
    assert result["cases_passed"] == 1
    assert result["symbol_substitutions"] == 1


def test_benchmark_reports_missing_candidate_backend_as_infrastructure_error(
    monkeypatch, capsys
):
    from benchmarks import benchmark_espeak
    from piperg2p import BackendUnavailableError

    def unavailable(*args, **kwargs):
        raise BackendUnavailableError("test eSpeak missing")

    monkeypatch.setattr(benchmark_espeak, "run_candidate", unavailable)
    rc = benchmark_espeak.main(
        [
            "--quick",
            "--suite",
            "core",
            "--candidate",
            "cli",
            "--reference-source",
            "golden",
            "--golden",
            str(
                Path(benchmark_espeak.__file__).parent
                / "goldens"
                / "espeak_ipa3_en-us.json"
            ),
            "--format",
            "summary",
        ]
    )
    output = capsys.readouterr().out
    assert rc == 2
    assert "candidate_errors: 5" in output
    assert "candidate_error: hello: test eSpeak missing" in output
