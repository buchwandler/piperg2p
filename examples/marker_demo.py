from __future__ import annotations

from _common import load_g2p, parser

from piperg2p import apply_marker_overrides, parse_delimited


def main() -> int:
    """Parse marked source ranges, then assign ordinary Piper overrides."""
    args = parser("Convert marked source ranges to Piper overrides").parse_args()
    clean, ranges, marker_warnings = parse_delimited("Say @hello@ today")
    g2p = load_g2p(args)
    try:
        result = g2p.phonemize_prepared(
            clean,
            overrides=apply_marker_overrides(
                clean, ranges, {1: {"lang": args.language}}
            ),
        )
        print("phonemes:", result.phonemes)
        print("marker warnings:", marker_warnings)
        print("phonemization warnings:", result.warnings)
    finally:
        g2p.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
