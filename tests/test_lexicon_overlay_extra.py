from __future__ import annotations

from dataclasses import dataclass

from piperg2p.diagnostics import BackendDiagnostics
from piperg2p.lexicons.base import LexiconDiagnostics, LexiconPronunciation
from piperg2p.lexicons.overlay import compose_lexicon_overlay
from piperg2p.raw_blocks import parse_raw_blocks


@dataclass
class FakeLookup:
    values: dict[str, str]

    def __post_init__(self):
        self.words: list[str] = []

    @property
    def diagnostics(self):
        return LexiconDiagnostics(True, "fake", "en-us", ("fake",), "override")

    def lookup_many(self, words, *, tag=None):
        self.words.extend(words)
        return tuple(
            LexiconPronunciation(self.values[word], "fake", matched_key=word)
            if word in self.values
            else None
            for word in words
        )


class FakeBackend:
    def __init__(self):
        self.calls: list[str] = []
        self.diagnostics = BackendDiagnostics(implementation="fake")

    def phonemize(self, text, *, voice):
        self.calls.append(text)
        return [[*text]] if text else []


def test_adjacent_hits_do_not_create_empty_fallback_calls():
    lookup = FakeLookup({"special": "Q", "name": "N"})
    backend = FakeBackend()
    groups = compose_lexicon_overlay(
        parse_raw_blocks("alpha special name beta"),
        lookup,
        lambda text: backend.phonemize(text, voice="en-us"),
    )
    assert backend.calls == ["alpha ", " beta"]
    assert groups == [[*"alpha ", "Q", " ", "N", *" beta"]]


def test_punctuation_remains_in_fallback_source_chunk():
    lookup = FakeLookup({"known": "Q"})
    backend = FakeBackend()
    groups = compose_lexicon_overlay(
        parse_raw_blocks("known, unknown."),
        lookup,
        lambda text: backend.phonemize(text, voice="en-us"),
    )
    assert backend.calls == [", unknown."]
    assert groups == [["Q", *", unknown."]]


def test_lexicon_pronunciation_is_normalized_to_nfd():
    lookup = FakeLookup({"known": "é"})
    groups = compose_lexicon_overlay(
        parse_raw_blocks("known"),
        lookup,
        lambda text: [],
    )
    assert groups == [["e", "\u0301"]]


def test_ipa3_lexicon_hit_preserves_raw_symbol_stream():
    class IPA3Lookup:
        @property
        def diagnostics(self):
            return LexiconDiagnostics(
                True, "fake", "en-us", ("fake",), "piper-espeak-frozen"
            )

        def lookup_many(self, words, *, tag=None):
            return tuple(
                LexiconPronunciation(
                    "é", "fake", matched_key=word, source_encoding="espeak-ipa3"
                )
                for word in words
            )

    groups = compose_lexicon_overlay(
        parse_raw_blocks("known"),
        IPA3Lookup(),
        lambda text: [],
    )
    assert groups == [["é"]]


def test_vowel_clusters_merge_after_raw_and_lexicon_composition():
    lookup = FakeLookup({"known": "a"})
    groups = compose_lexicon_overlay(
        parse_raw_blocks("known[[b]]"),
        lookup,
        lambda text: [],
        vowel_clusters=frozenset({("a", "b")}),
    )
    assert groups == [["ab"]]
