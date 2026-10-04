from __future__ import annotations

from _common import parser

from piperg2p import get_g2p


def main() -> int:
    """Show configured Lexphon lookup with Piper-owned eSpeak fallback."""
    selected = parser("Demonstrate Lexphon misses falling back to PiperG2P eSpeak")
    selected.add_argument(
        "--lexicon",
        required=True,
        help="identifier of an already-installed Lexphon pronunciation asset",
    )
    selected.add_argument(
        "--text",
        default="Hello world",
        help="prepared text to phonemize (default: %(default)s)",
    )
    args = selected.parse_args()
    g2p = get_g2p(
        args.language,
        config=args.config,
        lexicons=(args.lexicon,),
        use_espeak_fallback=True,
        espeak_mode=args.espeak_mode,
    )
    try:
        result = g2p.phonemize_prepared(args.text)
        print("text:", args.text)
        print("phonemes:", result.phonemes)
        print("lexicon diagnostics:", result.diagnostics.lexicon)
        print("warnings:", result.warnings)
        print("A lexicon miss is sent to PiperG2P's configured eSpeak backend.")
    finally:
        g2p.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
