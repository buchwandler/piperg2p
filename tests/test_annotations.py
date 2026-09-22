from piperg2p import PiperG2P, TokenAnnotation, VoiceConfig


def test_annotations_are_source_aligned_and_preserved_in_token_metadata():
    config = VoiceConfig.from_dict(
        {
            "num_symbols": 8,
            "num_speakers": 1,
            "audio": {"sample_rate": 22050},
            "phoneme_type": "text",
            "phoneme_id_map": {"_": 0, "^": 1, "$": 2, "a": 3, "b": 4, " ": 5, "c": 6},
        }
    )
    g2p = PiperG2P("en-us", config)
    result = g2p.phonemize_prepared(
        "ab c",
        annotations=[
            TokenAnnotation(
                0,
                2,
                text="ab",
                pos="NOUN",
                tag="NN",
                lemma="ab",
                morph="Number=Sing",
            )
        ],
    )
    assert result.tokens[0].meta == {
        "pos": "NOUN",
        "tag": "NN",
        "lemma": "ab",
        "morph": "Number=Sing",
    }
    g2p.close()


def test_annotation_mapping_preserves_morph_metadata():
    config = VoiceConfig.from_dict(
        {
            "num_symbols": 4,
            "num_speakers": 1,
            "audio": {"sample_rate": 22050},
            "phoneme_type": "text",
            "phoneme_id_map": {"_": 0, "^": 1, "$": 2, "a": 3},
        }
    )
    g2p = PiperG2P("en-us", config)
    result = g2p.phonemize_prepared(
        "a",
        annotations=[{"start": 0, "end": 1, "text": "a", "morph": "VerbForm=Fin"}],
    )
    assert result.tokens[0].meta == {"morph": "VerbForm=Fin"}
    g2p.close()
