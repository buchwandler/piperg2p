from __future__ import annotations

import sys
import types
import warnings

from piperg2p import EspeakLibraryCandidate, inspect_espeak
from piperg2p.backends.espeak import discovery


def test_inspection_selects_exact_later_candidate_without_initializing(
    monkeypatch, tmp_path
):
    loader_library = tmp_path / "loader.so"
    loader_library.write_bytes(b"")
    monkeypatch.setitem(
        sys.modules,
        "espeakng_loader",
        types.SimpleNamespace(
            get_library_path=lambda: str(loader_library),
            get_data_path=lambda: None,
        ),
    )
    monkeypatch.setattr(
        discovery.ctypes.util,
        "find_library",
        lambda name: {"espeak-ng": "system-ng", "espeak": "system"}.get(name),
    )
    calls: list[str] = []

    class OldLibrary:
        pass

    class ExactLibrary:
        espeak_TextToPhonemesWithTerminator = object()

    def load(value: str):
        calls.append(value)
        return ExactLibrary() if value == "system-ng" else OldLibrary()

    monkeypatch.setattr(discovery.ctypes, "CDLL", load)
    monkeypatch.setattr(discovery, "maybe_find_executable", lambda explicit=None: None)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        info = inspect_espeak()

    assert not caught
    assert calls == [str(loader_library), "system-ng"]
    assert info.selected_exact_library == "system-ng"
    assert info.selected_source == "system-espeak-ng"
    assert info.exact_native_available
    assert not info.cli_available
    assert [probe.source for probe in info.candidates] == [
        "modern-loader",
        "system-espeak-ng",
        "system-espeak",
    ][: len(info.candidates)]


def test_inspection_explicit_library_is_authoritative(monkeypatch):
    monkeypatch.setenv("PIPERG2P_ESPEAK_LIBRARY", "explicit-old")
    monkeypatch.setattr(
        discovery.ctypes.util, "find_library", lambda name: "system-exact"
    )
    calls: list[str] = []

    class OldLibrary:
        pass

    def load(value: str):
        calls.append(value)
        return OldLibrary()

    monkeypatch.setattr(discovery.ctypes, "CDLL", load)
    monkeypatch.setattr(
        discovery, "maybe_find_executable", lambda explicit=None: "espeak"
    )

    info = inspect_espeak()

    assert calls == ["explicit-old"]
    assert info.selected_exact_library is None
    assert not info.exact_native_available
    assert len(info.candidates) == 1
    assert info.candidates[0].source == "explicit"
    assert info.candidates[0].loadable
    assert not info.candidates[0].exact_clause_api


def test_candidate_type_is_immutable():
    candidate = EspeakLibraryCandidate("libespeak-ng.so", "system-espeak-ng")

    try:
        candidate.library = "other"
    except AttributeError:
        pass
    else:
        raise AssertionError("candidate should be immutable")
