from __future__ import annotations

from _common import parser

from piperg2p import phonemize_prepared


def main() -> int:
    """Show the canonical structured prepared-text call."""
    args = parser("Basic structured PiperG2P prepared-text result").parse_args()
    result = phonemize_prepared(
        "Hello world",
        language=args.language,
        config=args.config,
        espeak_mode=args.espeak_mode,
    )
    print("phonemes:", result.phonemes)
    print("token_ids:", result.token_ids)
    print("warnings:", result.warnings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
