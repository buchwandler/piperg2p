"""Inspect the pinned Phase 1 corpus without importing Piper at runtime."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=Path(__file__).parent / "data" / "core.json")
    args = parser.parse_args()
    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    print(json.dumps({"profile": corpus["profile"], "cases": len(corpus["cases"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
