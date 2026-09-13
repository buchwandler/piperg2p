from piperg2p import VoiceConfig, cache_info, clear_cache, get_g2p
from piperg2p.cache import get_or_create, set_maxsize


def _config():
    return VoiceConfig.from_dict(
        {
            "num_symbols": 6,
            "num_speakers": 1,
            "audio": {"sample_rate": 22050},
            "phoneme_type": "text",
            "phoneme_id_map": {"_": 0, "^": 1, "$": 2, "a": 3, "b": 4, " ": 5},
        }
    )


def test_get_g2p_reuses_identity_and_clear_cache_closes_frontend():
    clear_cache()
    first = get_g2p("en-us", config=_config())
    second = get_g2p("en-us", config=_config())
    assert first is second
    assert cache_info().size == 1
    clear_cache()
    assert cache_info().size == 0


def test_cache_is_bounded_and_closes_evicted_values():
    class Value:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    clear_cache()
    set_maxsize(1)
    first = Value()
    get_or_create("one", lambda: first)
    get_or_create("two", Value)
    assert first.closed
    assert cache_info().size == 1
    clear_cache()
    set_maxsize(8)
