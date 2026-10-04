from __future__ import annotations

from _common import load_g2p, parser

from piperg2p import OverrideSpan


def main() -> int:
    """Apply structured stress after explicit phoneme override resolution."""
    value = parser(
        "Apply stress to an explicit phoneme override; requires a compatible voice map"
    )
    value.add_argument(
        "--phonemes",
        default="həloʊ",
        help="resolved IPA symbols to stress; every symbol must exist in the selected voice map",
    )
    args = value.parse_args()
    text = "Hello"
    g2p = load_g2p(args)
    try:
        result = g2p.phonemize_prepared(
            text,
            overrides=[OverrideSpan(0, len(text), {"ph": args.phonemes, "stress": 2})],
        )
        print("resolved override:", args.phonemes)
        print("phonemes after stress:", result.phonemes)
        print("missing_phonemes:", result.missing_phonemes)
        print("warnings:", result.warnings)
    finally:
        g2p.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
