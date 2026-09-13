from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1] / "piperg2p"


def test_piperg2p_has_no_direct_semantic_preparation_imports() -> None:
    prohibited = (
        "from numeralform",
        "import numeralform",
        "from spokenform",
        "import spokenform",
    )
    offenders: list[str] = []
    for path in ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if any(marker in text for marker in prohibited):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_core_import_and_text_frontend_work_without_semantic_packages() -> None:
    code = """
import builtins

real_import = builtins.__import__


def blocked(name, *args, **kwargs):
    if name == "numeralform" or name.startswith("numeralform."):
        raise ModuleNotFoundError("blocked numeralform")
    if name == "spokenform" or name.startswith("spokenform."):
        raise ModuleNotFoundError("blocked spokenform")
    return real_import(name, *args, **kwargs)


builtins.__import__ = blocked

from piperg2p import PiperFrontend, VoiceConfig

config = VoiceConfig.from_dict(
    {
        "phoneme_type": "text",
        "num_symbols": 4,
        "num_speakers": 1,
        "audio": {"sample_rate": 22050},
        "phoneme_id_map": {"_": 0, "^": 1, "$": 2, "a": 3},
    }
)
result = PiperFrontend(config).phonemize_prepared("a")
assert result.sentences
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
