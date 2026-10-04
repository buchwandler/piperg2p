from __future__ import annotations

import argparse
from pathlib import Path

from piperg2p import PiperG2P, get_g2p


def _language_argument(
    value: argparse.ArgumentParser, *, required: bool = False
) -> None:
    value.add_argument(
        "--language",
        default=None if required else "en-us",
        required=required,
        help="source/routing language label (not a Piper voice/model selector)",
    )


def parser(description: str) -> argparse.ArgumentParser:
    """Build the shared parser for examples that need a Piper voice config."""
    value = argparse.ArgumentParser(description=description)
    value.add_argument(
        "--config",
        required=True,
        type=Path,
        help="Piper .onnx.json voice configuration",
    )
    _language_argument(value)
    value.add_argument(
        "--espeak-mode",
        choices=("auto", "native", "cli"),
        default="auto",
        help="eSpeak backend mode for eSpeak voice configs (default: auto)",
    )
    return value


def language_parser(description: str) -> argparse.ArgumentParser:
    """Build a parser for local language/lexicon discovery without a voice."""
    value = argparse.ArgumentParser(description=description)
    _language_argument(value, required=True)
    return value


def load_g2p(args: argparse.Namespace) -> PiperG2P:
    """Create a reusable facade using the shared example options."""
    return get_g2p(
        args.language,
        config=args.config,
        espeak_mode=args.espeak_mode,
    )
