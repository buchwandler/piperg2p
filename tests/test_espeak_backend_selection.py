from __future__ import annotations

import types

import pytest

from piperg2p import BackendFallbackWarning, EspeakBackend
from piperg2p.backends.espeak import backend as backend_module


def _patch_providers(monkeypatch, *, native_error: Exception | None = None):
    calls = {"native": 0, "cli": 0}

    class Native:
        def __init__(self, **kwargs):
            calls["native"] += 1
            if native_error is not None:
                raise native_error
            self.diagnostics = types.SimpleNamespace(
                implementation="native",
                executable="espeak-ng",
                library_path="libespeak-ng.so",
                data_path="espeak-ng-data",
                discovery_source="test",
                version="test",
                exact_clause_api=True,
                fallback_reason=None,
                parity="exact",
                warnings=(),
            )

        def close(self):
            pass

    class Cli:
        def __init__(self, **kwargs):
            calls["cli"] += 1
            self.diagnostics = types.SimpleNamespace(
                implementation="cli",
                executable="espeak-ng",
                library_path=None,
                data_path=None,
                discovery_source="test",
                version=None,
                exact_clause_api=False,
                fallback_reason=None,
                parity="best-effort",
                warnings=(),
            )

        def close(self):
            pass

    monkeypatch.setattr(backend_module, "NativeEspeakProvider", Native)
    monkeypatch.setattr(backend_module, "EspeakCliBackend", Cli)
    monkeypatch.setattr(
        backend_module,
        "discover",
        lambda **kwargs: types.SimpleNamespace(
            library="libespeak-ng.so",
            data="espeak-ng-data",
            executable="espeak-ng",
            source="test",
        ),
    )
    return calls


def test_auto_keeps_successful_native_provider(monkeypatch):
    calls = _patch_providers(monkeypatch)

    backend = EspeakBackend(mode="auto")

    assert calls == {"native": 1, "cli": 0}
    assert backend.diagnostics.implementation == "native"
    backend.close()


def test_auto_falls_back_to_cli_after_native_failure(monkeypatch):
    calls = _patch_providers(
        monkeypatch,
        native_error=backend_module.BackendUnavailableError("library unavailable"),
    )

    with pytest.warns(BackendFallbackWarning, match="library unavailable"):
        backend = EspeakBackend(mode="auto")

    assert calls == {"native": 1, "cli": 1}
    assert backend.diagnostics.implementation == "cli"
    assert backend.diagnostics.fallback_reason == "BackendUnavailableError: library unavailable"
    backend.close()


def test_native_mode_keeps_successful_native_provider(monkeypatch):
    calls = _patch_providers(monkeypatch)

    backend = EspeakBackend(mode="native")

    assert calls == {"native": 1, "cli": 0}
    assert backend.diagnostics.implementation == "native"
    backend.close()


def test_native_mode_raises_after_native_failure(monkeypatch):
    calls = _patch_providers(
        monkeypatch,
        native_error=backend_module.BackendUnavailableError("library unavailable"),
    )

    with pytest.raises(backend_module.BackendUnavailableError, match="library unavailable"):
        EspeakBackend(mode="native")

    assert calls == {"native": 1, "cli": 0}


def test_cli_mode_never_attempts_native(monkeypatch):
    calls = _patch_providers(monkeypatch)

    backend = EspeakBackend(mode="cli")

    assert calls == {"native": 0, "cli": 1}
    assert backend.diagnostics.implementation == "cli"
    backend.close()
