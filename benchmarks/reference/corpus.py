from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_corpus(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("cases"), list):
        raise TypeError("benchmark corpus must contain a cases list")
    return value


def cases_for_suite(corpus: dict[str, Any], suite: str) -> list[dict[str, Any]]:
    return [case for case in corpus["cases"] if case.get("suite", "core") == suite]
