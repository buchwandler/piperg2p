from __future__ import annotations

from dataclasses import dataclass

import pytest

from piperg2p import BackendDiagnostics, PiperFrontend, VoiceConfig
from piperg2p.errors import LexiconConfigurationError, MissingPhonemeError
from piperg2p.lexicons.base import LexiconDiagnostics, LexiconPronunciation
from piperg2p.lexicons.overlay import compose_lexicon_overlay
from piperg2p.raw_blocks import parse_raw_blocks


@dataclass
class FakeLookup:
    values: dict[str, str]

    def __post_init__(self):
        self.words: list[str] = []
        self.closed = False

    @property
    def diagnostics(self):
        return LexiconDiagnostics(True, "fake", "en-us", ("fake",), "override")

    def lookup(self, word, *, tag=None):
        self.words.append(word)
        value = self.values.get(word)
        return LexiconPronunciation(value, "fake", matched_key=word) if value else None

    def lookup_many(self, words, *, tag=None):
        self.words.extend(words)
        return tuple(
            LexiconPronunciation(self.values[word], "fake", matched_key=word)
            if word in self.values
            else None
            for word in words
        )

    def close(self):
        self.closed = True


class FakeBackend:
    def __init__(self):
        self.calls: list[str] = []
        self.diagnostics = BackendDiagnostics(implementation="fake")
        self.closed = False

    def phonemize(self, text, *, voice):
        self.calls.append(text)
        return [[*text]] if text else []

    def close(self):
        self.closed = True


def test_overlay_hit_bypasses_espeak_and_coalesces_misses():
    lookup = FakeLookup({"special": "Q"})
    backend = FakeBackend()
    groups = compose_lexicon_overlay(
        parse_raw_blocks("alpha special beta gamma"),
        lookup,
        lambda text: backend.phonemize(text, voice="en-us"),
    )
    assert backend.calls == ["alpha ", " beta gamma"]
    assert lookup.words == ["alpha", "special", "beta", "gamma"]
    assert groups == [[*"alpha ", "Q", *" beta gamma"]]


def test_overlay_raw_block_has_precedence_over_lookup():
    lookup = FakeLookup({"known": "Q", "RAW": "R"})
    backend = FakeBackend()

    groups = compose_lexicon_overlay(
        parse_raw_blocks("known [[RAW]] known"),
        lookup,
        lambda text: backend.phonemize(text, voice="en-us"),
    )
    assert lookup.words == ["known", "known"]
    assert groups == [["Q", " ", "R", "A", "W", " ", "Q"]]


def _config():
    symbols = {"_": 0, "^": 1, "$": 2}
    for value in "abcdefghijklmnopqrstuvwxyz Q ":
        symbols.setdefault(value, len(symbols))
    return VoiceConfig.from_dict(
        {
            "num_symbols": len(symbols),
            "num_speakers": 1,
            "audio": {"sample_rate": 22050},
            "phoneme_type": "espeak",
            "phoneme_id_map": symbols,
        }
    )


def test_frontend_reports_injected_lexicon_and_closes_only_owned_backend():
    lookup = FakeLookup({"known": "Q"})
    backend = FakeBackend()
    frontend = PiperFrontend(_config(), backend=backend, lexicon_backend=lookup, missing="error")
    result = frontend.phonemize("known unknown")
    assert result.diagnostics.lexicon.implementation == "fake"
    assert result.sentences[0].phonemes == ("Q", " ", "u", "n", "k", "n", "o", "w", "n")
    frontend.close()
    assert backend.closed
    assert not lookup.closed


def test_frontend_rejects_lexicons_for_non_espeak_and_conflicting_sources():
    text_config = VoiceConfig.from_dict(
        {
            "num_symbols": 4,
            "num_speakers": 1,
            "audio": {"sample_rate": 22050},
            "phoneme_type": "text",
            "phoneme_id_map": {"_": 0, "^": 1, "$": 2, "a": 3},
        }
    )
    with pytest.raises(LexiconConfigurationError, match="only supports"):
        PiperFrontend(text_config, lexicons=("id",), backend=FakeBackend())
    with pytest.raises(LexiconConfigurationError, match="mutually exclusive"):
        PiperFrontend(_config(), lexicons=("id",), lexicon_backend=FakeLookup({}), backend=FakeBackend())


def test_unencodable_hit_uses_existing_missing_policy():
    lookup = FakeLookup({"known": "Z"})
    with pytest.raises(MissingPhonemeError):
        PiperFrontend(_config(), backend=FakeBackend(), lexicon_backend=lookup, missing="error").phonemize("known")
