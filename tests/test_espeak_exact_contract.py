from __future__ import annotations

import sys
import types

import pytest

from piperg2p import BackendFallbackWarning, EspeakBackend
from piperg2p.backends.espeak import backend as backend_module
from piperg2p.backends.espeak.discovery import discover
from piperg2p.backends.espeak.native import AUDIO_OUTPUT_SYNCHRONOUS


def test_public_synchronous_output_constant_matches_espeak_api():
    assert AUDIO_OUTPUT_SYNCHRONOUS == 2


def test_discovery_prefers_packaged_loader(monkeypatch, tmp_path):
    library = tmp_path / "libespeak-ng.so"
    data = tmp_path / "espeak-ng-data"
    library.write_bytes(b"")
    data.mkdir()
    loader = types.SimpleNamespace(
        get_library_path=lambda: str(library),
        get_data_path=lambda: str(data),
    )
    monkeypatch.setitem(sys.modules, "espeakng_loader", loader)
    monkeypatch.setattr("piperg2p.backends.espeak.discovery.find_executable", lambda explicit=None: "espeak-ng")

    paths = discover()

    assert paths.library == str(library)
    assert paths.data == str(data)
    assert paths.source == "modern-loader"


def test_auto_rejects_native_provider_without_exact_clause_api(monkeypatch):
    calls: list[bool] = []

    class Native:
        def __init__(self, **kwargs):
            calls.append(kwargs["strict"])
            raise backend_module.BackendUnavailableError(
                "loaded eSpeak library lacks espeak_TextToPhonemesWithTerminator"
            )

    class Cli:
        diagnostics = types.SimpleNamespace(
            implementation="cli",
            executable="espeak-ng",
            library_path=None,
            data_path=None,
            discovery_source="system-espeak-ng",
            version=None,
            exact_clause_api=False,
            fallback_reason=None,
            parity="best-effort",
            warnings=(),
        )

        def __init__(self, **kwargs):
            del kwargs

        def close(self):
            pass

    monkeypatch.setattr(backend_module, "NativeEspeakProvider", Native)
    monkeypatch.setattr(backend_module, "EspeakCliBackend", Cli)
    monkeypatch.setattr(backend_module, "discover", lambda **kwargs: types.SimpleNamespace(
        library="old", data=None, executable="espeak-ng", source="system-espeak"
    ))

    with pytest.warns(BackendFallbackWarning, match="terminator API unavailable"):
        backend = EspeakBackend(mode="auto")

    assert calls == [True]
    assert backend.diagnostics.implementation == "cli"
    assert backend.diagnostics.fallback_reason == "terminator API unavailable"
    backend.close()
