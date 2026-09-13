from piperg2p import OverrideSpan, PiperG2P, VoiceConfig


def _g2p():
    symbols = {"_": 0, "^": 1, "$": 2, " ": 3}
    symbols.update({character: index + 4 for index, character in enumerate("abcdefghijklmnopqrstuvwxyz" )})
    return PiperG2P(
        "en-us",
        VoiceConfig.from_dict(
            {
                "num_symbols": 40,
                "num_speakers": 1,
                "audio": {"sample_rate": 22050},
                "phoneme_type": "text",
                "phoneme_id_map": symbols,
            }
        ),
    )


def test_phoneme_override_is_resolved_directly_and_offsets_are_preserved():
    g2p = _g2p()
    result = g2p.phonemize_prepared("abc", overrides=[OverrideSpan(0, 1, {"ph": "z"})])
    assert result.phonemes == "z"
    assert result.tokens[0].char_start == 0
    assert result.tokens[0].meta["override"] == {"ph": "z"}
    g2p.close()


def test_snap_overlap_records_source_offsets():
    g2p = _g2p()
    result = g2p.phonemize_prepared("abc", overrides=[OverrideSpan(1, 2, {"ph": "z"})])
    assert result.phonemes == "z"
    assert "(1, 2) snapped to (0, 3)" in result.warnings[0]
    g2p.close()
