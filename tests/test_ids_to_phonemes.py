import pytest

from piperg2p import VoiceConfig, encode_phonemes, ids_to_phonemes
from piperg2p.errors import ConfigError


def _config():
    return VoiceConfig.from_dict(
        {
            "num_symbols": 8,
            "num_speakers": 1,
            "audio": {"sample_rate": 22050},
            "phoneme_type": "text",
            "phoneme_id_map": {
                "_": 0,
                "^": 1,
                "$": 2,
                "a": 3,
                "x": [4, 5],
                "b": 6,
            },
        }
    )


def test_ids_to_phonemes_decodes_framing_and_multi_id_symbols():
    config = _config()
    encoded = encode_phonemes(["a", "x", "b"], config.phoneme_id_map)
    assert ids_to_phonemes(encoded.ids, config) == "axb"


def test_ids_to_phonemes_rejects_unknown_sequences():
    with pytest.raises(ConfigError, match="cannot decode"):
        ids_to_phonemes([1, 0, 99, 2], _config())
