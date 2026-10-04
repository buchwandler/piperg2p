from __future__ import annotations

from _common import load_g2p, parser

from piperg2p import OverrideSpan


def main() -> int:
    """Route one source span through an explicit eSpeak voice."""
    args = parser("Route one source span through an explicit eSpeak voice").parse_args()
    text = "Hello Welt"
    start, end = 6, 10
    routed_voice = "de-de"
    g2p = load_g2p(args)
    try:
        result = g2p.phonemize_prepared(
            text,
            overrides=[OverrideSpan(start, end, {"lang": routed_voice})],
        )
        print("phonemes:", result.phonemes)
        print("explicit route:", text[start:end], (start, end), "->", routed_voice)
        print(
            "override metadata:",
            [
                (token.text, token.lang, token.meta)
                for token in result.tokens
                if "override" in token.meta
            ],
        )
    finally:
        g2p.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
