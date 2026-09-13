from piperg2p import __all__

SHARED_PUBLIC_API = {
    "get_g2p", "phonemize", "phonemize_prepared", "phonemes", "phoneme_ids",
    "tokenize", "cache_info", "clear_cache", "PhonemizeResult", "TokenSpan",
    "TokenAnnotation", "OverrideSpan", "available_lexicons", "lexicon_info",
    "parse_delimited", "apply_marker_overrides", "ids_to_phonemes",
}


def test_shared_sibling_api_is_exported():
    assert SHARED_PUBLIC_API <= set(__all__)
