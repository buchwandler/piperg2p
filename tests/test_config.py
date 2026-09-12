import pytest

from piperg2p import (
    ConfigError,
    PhonemeType,
    PiperConfig,
    PiperFrontend,
    UnsupportedCompatibilityError,
    UnsupportedPhonemeTypeError,
    VoiceConfig,
)
from piperg2p.registry import REGISTRY


def raw_config(**updates):
    value = {
        "num_symbols": 8,
        "num_speakers": 1,
        "audio": {"sample_rate": 22050},
        "phoneme_type": "text",
        "phoneme_id_map": {"_": 0, "^": 1, "$": 2, "a": 3, "b": [4], "ab": [5]},
    }
    value.update(updates)
    return value


def test_config_is_typed_immutable_and_round_trips():
    config = VoiceConfig.from_dict(raw_config())
    assert config.phoneme_type is PhonemeType.TEXT
    assert PiperConfig is VoiceConfig
    assert config.phoneme_id_map["a"] == (3,)
    with pytest.raises(TypeError):
        config.phoneme_id_map["x"] = (6,)
    assert VoiceConfig.from_dict(config.to_dict()) == config


def test_strict_config_requires_core_fields():
    with pytest.raises(ConfigError, match="sample_rate"):
        VoiceConfig.from_dict(
            {"num_symbols": 1, "num_speakers": 1, "phoneme_id_map": {"_": 0}}
        )
    with pytest.raises(ConfigError, match="num_symbols"):
        VoiceConfig.from_dict(
            {
                "num_speakers": 1,
                "audio": {"sample_rate": 22050},
                "phoneme_id_map": {"_": 0},
            }
        )


def test_lenient_config_infers_legacy_defaults():
    config = VoiceConfig.from_dict({"phoneme_id_map": {"_": 0}}, strict=False)
    assert config.num_symbols == 1
    assert config.sample_rate == 22050


def test_config_rejects_unknown_phoneme_type_and_bad_ids():
    with pytest.raises(UnsupportedPhonemeTypeError):
        VoiceConfig.from_dict(raw_config(phoneme_type="unknown"))
    with pytest.raises(ConfigError, match="negative"):
        VoiceConfig.from_dict(raw_config(phoneme_id_map={"_": 0, "^": 1, "$": -1}))
    with pytest.raises(ConfigError, match="outside"):
        VoiceConfig.from_dict(raw_config(num_symbols=3))


def test_arabic_espeak_profile_is_explicitly_unsupported():
    config = VoiceConfig.from_dict(
        raw_config(phoneme_type="espeak", espeak={"voice": "ar"})
    )
    with pytest.raises(
        UnsupportedCompatibilityError, match="Arabic Piper eSpeak preprocessing"
    ):
        PiperFrontend(config)


def test_deferred_frontends_are_not_advertised_as_implemented():
    for phoneme_type in (
        PhonemeType.PINYIN,
        PhonemeType.HEBREW,
        PhonemeType.JAPANESE,
        PhonemeType.THAI,
    ):
        spec = REGISTRY[phoneme_type]
        assert not spec.implemented
        assert spec.backend_factory is None


def test_vowel_clusters_validate_merged_symbol():
    config = VoiceConfig.from_dict(raw_config(vowel_clusters=[["a", "b"]]))
    assert config.vowel_clusters == frozenset({("a", "b")})
    with pytest.raises(ConfigError, match="absent"):
        VoiceConfig.from_dict(raw_config(vowel_clusters=[["a", "x"]]))
