from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = ROOT / "examples"
EXECUTABLE_EXAMPLES = (
    "cache_and_batch.py",
    "debug_mode_demo.py",
    "demo_both_features.py",
    "espeak_fallback.py",
    "explicit_language_spans.py",
    "external_annotations.py",
    "lexicon_selection.py",
    "marker_demo.py",
    "mixed_language_auto.py",
    "new_api_demo.py",
    "result_inspection.py",
    "structured_stress.py",
)
TEXT_VOICE_EXAMPLES = (
    "cache_and_batch.py",
    "debug_mode_demo.py",
    "external_annotations.py",
    "new_api_demo.py",
    "result_inspection.py",
    "structured_stress.py",
)


def _text_voice_config(path: Path) -> Path:
    symbols = set("Hello worldGood morningSee you") | set("həloʊˈˌ")
    phoneme_id_map = {"^": [0], "_": [1], "$": [2]}
    phoneme_id_map.update(
        {symbol: [index + 3] for index, symbol in enumerate(sorted(symbols))}
    )
    config = {
        "phoneme_type": "text",
        "num_symbols": len(phoneme_id_map),
        "num_speakers": 1,
        "audio": {"sample_rate": 22050},
        "phoneme_id_map": phoneme_id_map,
    }
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def _assert_example_help(script: str) -> None:
    result = subprocess.run(
        [sys.executable, str(EXAMPLE_DIR / script), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout.casefold()


@pytest.mark.parametrize("script", EXECUTABLE_EXAMPLES)
def test_every_example_has_help(script: str) -> None:
    _assert_example_help(script)


def test_lexicon_discovery_help_needs_only_language() -> None:
    result = subprocess.run(
        [sys.executable, str(EXAMPLE_DIR / "lexicon_selection.py"), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--language" in result.stdout
    assert "--config" not in result.stdout


@pytest.mark.parametrize("script", TEXT_VOICE_EXAMPLES)
def test_offline_text_voice_examples(script: str, tmp_path: Path) -> None:
    config = _text_voice_config(tmp_path / "text-voice.onnx.json")
    result = subprocess.run(
        [
            sys.executable,
            str(EXAMPLE_DIR / script),
            "--config",
            str(config),
            "--language",
            "en-us",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
