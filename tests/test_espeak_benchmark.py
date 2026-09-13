from __future__ import annotations

import subprocess
import types

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
    assert calls[-1][1]["input"] == "hello\n"
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
