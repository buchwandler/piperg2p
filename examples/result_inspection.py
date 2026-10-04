from __future__ import annotations

from _common import load_g2p, parser

from piperg2p import ConfigError, ids_to_phonemes


def main() -> int:
    """Inspect a structured result and its voice-specific ID decoding."""
    args = parser(
        "Inspect result tokens, sentences, IDs, and decoded symbols"
    ).parse_args()
    g2p = load_g2p(args)
    try:
        result = g2p.phonemize_prepared("Hello world")
        print("clean_text:", result.clean_text)
        print("tokens:", result.tokens)
        print("sentences:", result.sentences)
        print("phonemes:", result.phonemes)
        print("token_ids:", result.token_ids)
        try:
            decoded = ids_to_phonemes(result.token_ids, g2p.config)
        except ConfigError as exc:
            print("ids_to_phonemes unavailable (ambiguous map):", exc)
        else:
            print("ids_to_phonemes (diagnostic, not a guaranteed inverse):", decoded)
    finally:
        g2p.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
