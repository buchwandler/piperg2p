from __future__ import annotations

from _common import load_g2p, parser

from piperg2p import LanguageRoutingConfig


def main() -> int:
    """Demonstrate deterministic automatic routing from local evidence."""
    args = parser(
        "Conservative automatic routing with offline word evidence"
    ).parse_args()
    default_language = args.language.casefold().replace("_", "-")
    candidate_language = "de-de" if default_language != "de-de" else "en-us"
    evidence_word = "Welt" if candidate_language == "de-de" else "Hello"
    g2p = load_g2p(args)
    try:
        routing = LanguageRoutingConfig(
            mode="auto",
            languages=(args.language, candidate_language),
            lexicons={candidate_language: {evidence_word: True}},
        )
        result = g2p.phonemize_prepared("Hello Welt", language_routing=routing)
        print("phonemes:", result.phonemes)
        for route in result.language_routes:
            print("route:", route)
        assert any(
            route.reason == "lexicon-evidence"
            and route.language == candidate_language
            and evidence_word in route.evidence
            for route in result.language_routes
        ), "the configured in-memory evidence must produce a lexicon-evidence route"
    finally:
        g2p.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
