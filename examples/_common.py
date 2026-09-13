from __future__ import annotations

import argparse
from pathlib import Path

from piperg2p import get_g2p


def parser(description: str) -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=description)
    value.add_argument(
        "--config", required=True, type=Path, help="Piper .onnx.json voice config"
    )
    value.add_argument("--language", default="en-us")
    return value


def load_g2p(args: argparse.Namespace):
    return get_g2p(args.language, config=args.config)
