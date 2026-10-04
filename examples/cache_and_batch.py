from __future__ import annotations

from _common import parser

from piperg2p import cache_info, clear_cache, get_g2p


def main() -> int:
    """Demonstrate repeated facade reuse and bounded-cache lifecycle."""
    args = parser("Reuse a bounded PiperG2P cache entry").parse_args()
    first = get_g2p(args.language, config=args.config, espeak_mode=args.espeak_mode)
    second = get_g2p(args.language, config=args.config, espeak_mode=args.espeak_mode)
    try:
        print("same cached object:", first is second)
        print("cache:", cache_info())
        for text in ("Hello world", "Good morning", "See you"):
            print("phonemes:", first.phonemize(text))
    finally:
        clear_cache()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
