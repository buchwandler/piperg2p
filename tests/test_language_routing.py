from piperg2p.language_routing import route_language
from piperg2p.types import LanguageRoutingConfig


def test_auto_routing_switches_only_on_unambiguous_evidence():
    config = LanguageRoutingConfig(
        mode="auto",
        languages=("de-de", "en-us"),
        lexicons={"en-us": {"world": "w"}},
    )
    route = route_language("world", "de-de", config)
    assert route.language == "en-us"
    assert route.reason == "lexicon-evidence"


def test_auto_routing_keeps_default_for_unknown_words():
    config = LanguageRoutingConfig(mode="auto", languages=("de-de", "en-us"), lexicons={})
    assert route_language("unknown", "de-de", config).language == "de-de"
