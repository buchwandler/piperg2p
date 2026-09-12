from __future__ import annotations

import json

from benchmarks.benchmark_reference import _compare_cases, main


def test_reference_case_comparison_reports_mismatches():
    actual = [{"id": "case", "phoneme_type": "text", "sentences": []}]
    expected = [{"id": "case", "phoneme_type": "text", "sentences": [{"ids": [1]}]}]
    comparison = _compare_cases(actual, expected)
    assert comparison[0]["status"] == "mismatch"


def test_reference_runner_does_not_create_missing_expected_output(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus.json"
    corpus.write_text(
        json.dumps(
            {
                "profile": {"name": "test", "reference": "piper", "commit": "pinned"},
                "cases": [{"id": "text", "phoneme_type": "text", "text": "a"}],
            }
        ),
        encoding="utf-8",
    )
    config = tmp_path / "voice.json"
    config.write_text(
        json.dumps(
            {
                "num_symbols": 4,
                "num_speakers": 1,
                "audio": {"sample_rate": 22050},
                "phoneme_type": "text",
                "phoneme_id_map": {"_": 0, "^": 1, "$": 2, "a": 3},
            }
        ),
        encoding="utf-8",
    )
    expected = tmp_path / "expected.json"
    output = tmp_path / "report.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "benchmark_reference",
            "--corpus",
            str(corpus),
            "--config",
            str(config),
            "--expected",
            str(expected),
            "--output",
            str(output),
        ],
    )

    assert main() == 1
    assert not expected.exists()
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["comparison"]["status"] == "missing-expected"
