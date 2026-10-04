from __future__ import annotations

from _common import load_g2p, parser


def main() -> int:
    """Inspect backend diagnostics and structured result metadata."""
    args = parser("Inspect backend diagnostics and result metadata").parse_args()
    g2p = load_g2p(args)
    try:
        result = g2p.phonemize_prepared("Hello world")
        print("diagnostics:", result.diagnostics)
        print("tokens:", result.tokens)
        print("missing_phonemes:", result.missing_phonemes)
        print("warnings:", result.warnings)
        print("sentences:", result.sentences)
    finally:
        g2p.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
