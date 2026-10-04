from __future__ import annotations

from _common import load_g2p, parser

from piperg2p import OverrideSpan


def main() -> int:
    """Combine a prepared result with an explicit source-span override."""
    args = parser(
        "Combine the prepared-result API with an explicit language-span override"
    ).parse_args()
    text = "Hello Welt"
    g2p = load_g2p(args)
    try:
        result = g2p.phonemize_prepared(
            text,
            overrides=[OverrideSpan(6, 10, {"lang": "de-de"})],
        )
        print("phonemes:", result.phonemes)
        print(
            "override tokens:",
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
