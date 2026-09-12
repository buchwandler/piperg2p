from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

from piperg2p.errors import LexiconDependencyError, LexiconResourceError
from piperg2p.lexicons import G2LexLookup, LexphonLookup


def test_lexphon_is_lazy_and_uses_lexicon_only_batch_lookup(monkeypatch):
    calls: list[tuple[str, object]] = []

    class Runtime:
        def __init__(self, language, *, lexicons, store, fallback):
            calls.append((language, (tuple(lexicons), store, fallback)))

        def lookup_lexicon(self, word, *, tag=None):
            if word == "known":
                return types.SimpleNamespace(text="noʊn", source="lexphon", matched_key=word)
            return None

        def lookup_many(self, words, *, tag=None):
            return tuple(self.lookup_lexicon(word, tag=tag) for word in words)

        def close(self):
            calls.append(("close", None))

    monkeypatch.setitem(sys.modules, "lexphon", types.SimpleNamespace(Phonemizer=Runtime))
    lookup = LexphonLookup("de-DE", ("first", "second"), store="store")
    assert calls == []

    assert lookup.lookup("known").pronunciation == "noʊn"
    assert calls == [("de-DE", (("first", "second"), "store", None))]
    result = lookup.lookup_many(("known", "missing"))
    assert result[0].matched_key == "known"
    assert result[1] is None
    lookup.close()
    lookup.close()
    assert calls[-1] == ("close", None)


def test_lexphon_missing_dependency_is_actionable(monkeypatch):
    monkeypatch.setitem(sys.modules, "lexphon", None)
    with pytest.raises(LexiconDependencyError, match=r"piperg2p\[lexphon\]"):
        LexphonLookup("en-us", ("en-us:espeak",)).lookup("word")


def test_lexphon_resource_errors_are_not_misses(monkeypatch):
    class Runtime:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("not installed")

    monkeypatch.setitem(sys.modules, "lexphon", types.SimpleNamespace(Phonemizer=Runtime))
    with pytest.raises(LexiconResourceError, match="Could not open Lexphon"):
        LexphonLookup("en-us", ("missing",)).lookup("word")


def test_g2lex_preserves_asset_order_and_forwards_tag(monkeypatch, tmp_path):
    first = tmp_path / "first.g2lex"
    second = tmp_path / "second.g2lex"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    calls: list[tuple[str, str | None]] = []

    class Asset:
        def __init__(self, name):
            self.name = name
            self.closed = False

        def lookup(self, word, *, tag=None):
            calls.append((self.name, tag))
            if self.name == "second.g2lex" and word == "known":
                return "kˈnoʊn"
            return None

        def close(self):
            self.closed = True

    assets = {first.name: Asset(first.name), second.name: Asset(second.name)}
    fake = types.SimpleNamespace(open=lambda path: assets[Path(path).name])
    monkeypatch.setitem(sys.modules, "g2lex", fake)

    lookup = G2LexLookup((first, second), language="en-US")
    assert lookup.lookup("known", tag="proper").pronunciation == "kˈnoʊn"
    assert calls == [(first.name, "proper"), (second.name, "proper")]
    assert lookup.lookup("missing") is None
    lookup.close()
    lookup.close()
    assert assets[first.name].closed
    assert assets[second.name].closed


def test_g2lex_missing_asset_has_focused_error():
    with pytest.raises(LexiconResourceError, match="does not exist"):
        G2LexLookup(("missing.g2lex",)).lookup("word")
