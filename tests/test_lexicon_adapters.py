from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import ClassVar

import pytest

from piperg2p.errors import LexiconDependencyError, LexiconResourceError
from piperg2p.lexicons import G2LexLookup, LexphonLookup


def test_lexphon_resolves_installed_assets_and_uses_g2lex(monkeypatch, tmp_path):
    paths = {
        identifier: tmp_path / f"{identifier.replace(':', '-')}.g2lex"
        for identifier in ("de-de:first", "de-de:second")
    }
    for path in paths.values():
        path.write_bytes(b"placeholder")
    calls: list[tuple[str, str | None]] = []
    store_calls: list[str] = []

    class DataStore:
        def metadata(self, identifier):
            store_calls.append(f"metadata:{identifier}")
            return {
                "id": identifier,
                "language": "de-DE",
                "kind": "pronunciation",
                "phoneme_encoding": "espeak-ipa3",
            }

        def path(self, identifier):
            store_calls.append(f"path:{identifier}")
            return paths[identifier]

    class Asset:
        def __init__(self, path):
            self.path = path
            self.metadata = {
                "id": next(
                    identifier
                    for identifier, value in paths.items()
                    if str(value) == path
                ),
                "language": "de-DE",
                "kind": "pronunciation",
                "phoneme_encoding": "espeak-ipa3",
            }

        def lookup(self, word, *, tag=None):
            calls.append((self.path, tag))
            if self.path == str(paths["de-de:second"]) and word == "known":
                return "kˈnoʊn"
            return None

        def close(self):
            pass

    fake_lexphon = types.SimpleNamespace(DataStore=lambda: DataStore())
    fake_g2lex = types.SimpleNamespace(open=lambda path: Asset(str(path)))
    monkeypatch.setitem(sys.modules, "lexphon", fake_lexphon)
    monkeypatch.setitem(sys.modules, "g2lex", fake_g2lex)

    lookup = LexphonLookup("de-DE", tuple(paths), store=DataStore())
    assert lookup.diagnostics.identifiers == tuple(paths)
    result = lookup.lookup("known", tag="proper")
    assert result is not None
    assert result.pronunciation == "kˈnoʊn"
    assert result.lexicon_id == "de-de:second"
    assert result.source_encoding == "espeak-ipa3"
    assert store_calls == [
        "metadata:de-de:first",
        "path:de-de:first",
        "metadata:de-de:second",
        "path:de-de:second",
    ]
    assert calls == [
        (str(paths["de-de:first"]), "proper"),
        (str(paths["de-de:second"]), "proper"),
    ]
    lookup.close()
    lookup.close()


def test_lexphon_missing_dependency_is_actionable(monkeypatch):
    monkeypatch.setitem(sys.modules, "lexphon", None)
    with pytest.raises(LexiconDependencyError, match=r"piperg2p\[lexphon\]"):
        LexphonLookup("en-us", ("en-us:espeak",)).lookup("word")


def test_lexphon_resource_errors_are_not_misses(monkeypatch):
    class DataStore:
        def metadata(self, identifier):
            raise RuntimeError("not installed")

    monkeypatch.setitem(
        sys.modules, "lexphon", types.SimpleNamespace(DataStore=DataStore)
    )
    with pytest.raises(LexiconResourceError, match="Could not resolve Lexphon"):
        LexphonLookup("en-us", ("missing",), store=DataStore()).lookup("word")


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


def test_g2lex_existing_asset_without_dependency_has_dependency_error(
    monkeypatch, tmp_path
):
    asset = tmp_path / "existing.g2lex"
    asset.write_bytes(b"placeholder")
    monkeypatch.setitem(sys.modules, "g2lex", None)
    with pytest.raises(LexiconDependencyError, match=r"piperg2p\[g2lex\]"):
        G2LexLookup((asset,)).lookup("word")


def test_g2lex_recognizes_modern_encoding_and_provenance(monkeypatch, tmp_path):
    asset_path = tmp_path / "modern.g2lex"
    asset_path.write_bytes(b"placeholder")

    class Asset:
        metadata: ClassVar[dict[str, str]] = {
            "id": "en-us:espeak-piper",
            "language": "en-US",
            "kind": "pronunciation",
            "phoneme_encoding": "espeak-ipa3",
            "data_version": "2026.1",
            "producer": "g2lex-data",
            "transform_id": "piper-ipa3",
            "generator": "espeak-ng-1",
        }

        def lookup(self, word, *, tag=None):
            return "tʃ" if word == "church" else None

        def close(self):
            pass

    monkeypatch.setitem(
        sys.modules, "g2lex", types.SimpleNamespace(open=lambda path: Asset())
    )
    with G2LexLookup((asset_path,), language="en-us") as lookup:
        pronunciation = lookup.lookup("church")
        assert pronunciation is not None
        assert pronunciation.source_encoding == "espeak-ipa3"
        assert pronunciation.provenance is not None
        assert pronunciation.provenance.data_version == "2026.1"
        assert pronunciation.provenance.transform == "piper-ipa3"


def test_g2lex_rejects_unsupported_modern_encoding(monkeypatch, tmp_path):
    asset_path = tmp_path / "unsupported.g2lex"
    asset_path.write_bytes(b"placeholder")

    class Asset:
        metadata: ClassVar[dict[str, str]] = {
            "kind": "pronunciation",
            "phoneme_encoding": "arpabet",
        }

        def close(self):
            pass

    monkeypatch.setitem(
        sys.modules, "g2lex", types.SimpleNamespace(open=lambda path: Asset())
    )
    with pytest.raises(LexiconResourceError, match="unsupported phoneme encoding"):
        G2LexLookup((asset_path,)).lookup("word")


def test_g2lex_missing_asset_has_focused_error():
    with pytest.raises(LexiconResourceError, match="does not exist"):
        G2LexLookup(("missing.g2lex",)).lookup("word")
