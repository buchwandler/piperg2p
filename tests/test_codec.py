from piperg2p import PiperFrontend, VoiceConfig, encode_phonemes


def _config(phoneme_type="text"):
    return VoiceConfig.from_dict({
        "num_symbols": 7,
        "num_speakers": 1,
        "audio": {"sample_rate": 22050},
        "espeak": {"voice": "en-us"},
        "phoneme_type": phoneme_type,
        "phoneme_id_map": {"_": [0], "^": [1], "$": [2], "a": [3], "b": [4], " ": [5], ".": [6]},
    })


def test_piper_id_framing():
    result = encode_phonemes(["a", "b"], _config().phoneme_id_map)
    assert result.ids == (1, 0, 3, 0, 4, 0, 2)


def test_text_frontend_uses_config_map():
    result = PiperFrontend(_config()).phonemize("ab")
    assert result.sentences[0].phonemes == ("a", "b")
    assert result.sentences[0].ids == (1, 0, 3, 0, 4, 0, 2)
