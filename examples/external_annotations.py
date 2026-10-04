from __future__ import annotations

from _common import load_g2p, parser

from piperg2p import TokenAnnotation


def main() -> int:
    """Pass caller-owned linguistic metadata without running an NLP model."""
    args = parser(
        "Pass source-aligned caller POS, tag, lemma, and morphology"
    ).parse_args()
    g2p = load_g2p(args)
    try:
        result = g2p.phonemize_prepared(
            "Hello world",
            annotations=[
                TokenAnnotation(
                    0,
                    5,
                    text="Hello",
                    pos="INTJ",
                    tag="UH",
                    lemma="hello",
                    morph="Number=Sing",
                )
            ],
        )
        print(
            "annotated tokens:", [(token.text, token.meta) for token in result.tokens]
        )
        print("phonemes:", result.phonemes)
    finally:
        g2p.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
