from __future__ import annotations

import pytest

from piperg2p import PiperFrontend, PiperG2P, VoiceConfig, clear_cache, get_g2p


def _text_config() -> VoiceConfig:
    return VoiceConfig.from_dict(
        {
            "num_symbols": 6,
            "num_speakers": 1,
            "audio": {"sample_rate": 22050},
            "phoneme_type": "text",
            "phoneme_id_map": {"_": 0, "^": 1, "$": 2, "a": 3, "b": 4, " ": 5},
        }
    )


def test_custom_backend_rejects_non_default_espeak_mode():
    config = _text_config()

    with pytest.raises(ValueError, match="mutually exclusive"):
        PiperFrontend(config, backend=object(), espeak_mode="native")


def test_use_cli_remains_compatible_and_resolves_cli_mode():
    g2p = PiperG2P("en-us", _text_config(), use_cli=True)

    assert g2p.frontend.espeak_mode == "cli"
    g2p.close()


def test_conflicting_use_cli_and_espeak_mode_is_rejected():
    with pytest.raises(ValueError, match="incompatible"):
        PiperG2P("en-us", _text_config(), use_cli=True, espeak_mode="native")


def test_cache_identity_includes_espeak_mode():
    clear_cache()
    first = get_g2p("en-us", config=_text_config(), espeak_mode="auto")
    second = get_g2p("en-us", config=_text_config(), espeak_mode="native")

    assert first is not second
    first.close()
    second.close()
    clear_cache()
