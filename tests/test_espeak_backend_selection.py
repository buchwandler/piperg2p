from __future__ import annotations

import types
import warnings
from typing import ClassVar

import pytest

from piperg2p import BackendFallbackWarning, BackendUnavailableError, EspeakBackend
from piperg2p.backends.espeak import backend as backend_module


def _info(*, mode: str, implementation: str, fallback_reason: str | None = None):
    return types.SimpleNamespace(
        requested_mode=mode,
        implementation=implementation,
        executable="espeak-ng",
        library="libespeak-ng.so" if implementation == "native" else None,
        data="espeak-ng-data",
        source="espeakng-loader" if implementation == "native" else "cli",
        version="1.0",
        exact_clause_api=implementation == "native",
        fallback_reason=fallback_reason,
        fallback_code="exact-clause-api-unavailable" if fallback_reason else None,
        parity="exact" if implementation == "native" else "best-effort",
        phoneme_output_api="native-trace" if implementation == "native" else "cli",
        phoneme_parity="exact" if implementation == "native" else "best-effort",
    )


class FakeRuntime:
    instances: ClassVar[list[FakeRuntime]] = []
    info_value = _info(mode="auto", implementation="native")
    error: Exception | None = None

    def __init__(self, **kwargs: object) -> None:
        if self.error:
            raise self.error
        self.kwargs = kwargs
        self.info = self.info_value
        self.clause_calls: list[tuple[str, str, bool]] = []
        self.phoneme_calls: list[tuple[str, str]] = []
        self.closed = False
        self.instances.append(self)

    def clauses(self, text: str, *, voice: str, exact: bool = False):
        self.clause_calls.append((text, voice, exact))
        return []

    def phonemize(self, text: str, *, voice: str) -> str:
        self.phoneme_calls.append((text, voice))
        return text

    @property
    def native_probes(self) -> tuple[object, ...]:
        return self.native_probes_value

    def close(self) -> None:
        self.closed = True


@pytest.fixture(autouse=True)
def reset_fake_runtime(monkeypatch: pytest.MonkeyPatch):
    FakeRuntime.instances = []
    FakeRuntime.error = None
    FakeRuntime.native_probes_value = ()
    monkeypatch.setattr(backend_module, "EspeakRuntime", FakeRuntime)


def test_auto_uses_runtime_native_without_warning():
    FakeRuntime.info_value = _info(mode="auto", implementation="native")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        backend = EspeakBackend(mode="auto")

    assert not [
        item for item in caught if issubclass(item.category, BackendFallbackWarning)
    ]
    assert FakeRuntime.instances[0].kwargs["prefer_exact_clauses"] is True
    assert backend.diagnostics.implementation == "native"
    assert backend.diagnostics.discovery_source == "modern-loader"
    backend.close()


def test_auto_uses_runtime_cli_and_emits_one_fallback_warning():
    FakeRuntime.info_value = _info(
        mode="auto",
        implementation="cli",
        fallback_reason="no exact clause API",
    )

    with pytest.warns(
        BackendFallbackWarning, match="exact Piper eSpeak clause API"
    ) as caught:
        backend = EspeakBackend(mode="auto")

    assert len(caught) == 1
    assert backend.diagnostics.implementation == "cli"
    assert backend.diagnostics.fallback_reason == "no exact clause API"
    assert backend.diagnostics.warnings[0].startswith("exact Piper")
    backend.close()


def test_native_runtime_failure_maps_to_backend_unavailable():
    FakeRuntime.error = backend_module.EspeakUnavailableError("library unavailable")

    with pytest.raises(BackendUnavailableError, match="library unavailable"):
        EspeakBackend(mode="native")


def test_cli_uses_runtime_cli_without_native_inspection_or_warning():
    FakeRuntime.info_value = _info(mode="cli", implementation="cli")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        backend = EspeakBackend(mode="cli")

    assert not [
        item for item in caught if issubclass(item.category, BackendFallbackWarning)
    ]
    assert FakeRuntime.instances[0].kwargs["prefer_exact_clauses"] is False
    assert backend.diagnostics.native_candidates == ()
    backend.close()


def test_warning_origin_is_external():
    FakeRuntime.info_value = _info(
        mode="auto",
        implementation="cli",
        fallback_reason="native unavailable",
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        backend = EspeakBackend(mode="auto")

    fallback = next(
        item for item in caught if issubclass(item.category, BackendFallbackWarning)
    )
    assert "/piperg2p/backends/" not in str(fallback.filename).replace("\\", "/")
    backend.close()


def test_constructor_paths_override_legacy_and_runtime_environment(monkeypatch):
    FakeRuntime.info_value = _info(mode="cli", implementation="cli")
    monkeypatch.setenv("PIPERG2P_ESPEAK_EXECUTABLE", "piper-exe")
    monkeypatch.setenv("PIPERG2P_ESPEAK_LIBRARY", "piper-lib")
    monkeypatch.setenv("PIPERG2P_ESPEAK_DATA", "piper-data")
    monkeypatch.setenv("ESPEAKNG_RUNTIME_EXECUTABLE", "runtime-exe")
    monkeypatch.setenv("ESPEAKNG_RUNTIME_LIBRARY", "runtime-lib")
    monkeypatch.setenv("ESPEAKNG_RUNTIME_DATA", "runtime-data")

    backend = EspeakBackend(
        mode="cli",
        executable="constructor-exe",
        library="constructor-lib",
        data="constructor-data",
    )

    assert FakeRuntime.instances[0].kwargs["executable"] == "constructor-exe"
    assert FakeRuntime.instances[0].kwargs["library"] == "constructor-lib"
    assert FakeRuntime.instances[0].kwargs["data"] == "constructor-data"
    backend.close()


def test_legacy_environment_overrides_runtime_environment(monkeypatch):
    FakeRuntime.info_value = _info(mode="cli", implementation="cli")
    monkeypatch.setenv("PIPERG2P_ESPEAK_EXECUTABLE", "piper-exe")
    monkeypatch.setenv("PIPERG2P_ESPEAK_DATA", "piper-data")
    monkeypatch.setenv("ESPEAKNG_RUNTIME_EXECUTABLE", "runtime-exe")
    monkeypatch.setenv("ESPEAKNG_RUNTIME_DATA", "runtime-data")

    backend = EspeakBackend(mode="cli")

    assert FakeRuntime.instances[0].kwargs["executable"] == "piper-exe"
    assert FakeRuntime.instances[0].kwargs["data"] == "piper-data"
    backend.close()


def test_diagnostics_map_runtime_info_and_native_candidates():
    FakeRuntime.info_value = types.SimpleNamespace(
        requested_mode="auto",
        implementation="native",
        executable="exe",
        library="lib",
        data="data",
        source="espeakng-loader",
        version="version",
        exact_clause_api=True,
        fallback_reason=None,
        fallback_code=None,
        parity="exact",
        phoneme_output_api="native-trace",
        phoneme_parity="exact",
    )
    probe = types.SimpleNamespace(
        library="candidate",
        source="espeakng-loader",
        data="candidate-data",
        loadable=True,
        exact_clause_api=True,
        phoneme_trace_api=True,
        error=None,
    )
    FakeRuntime.native_probes_value = (probe,)

    backend = EspeakBackend(mode="auto")
    diagnostics = backend.diagnostics

    assert diagnostics.requested_mode == "auto"
    assert diagnostics.implementation == "native"
    assert diagnostics.executable == "exe"
    assert diagnostics.library_path == "lib"
    assert diagnostics.data_path == "data"
    assert diagnostics.discovery_source == "modern-loader"
    assert diagnostics.version == "version"
    assert diagnostics.exact_clause_api
    assert diagnostics.fallback_reason is None
    assert diagnostics.fallback_code is None
    assert diagnostics.parity == "exact"
    assert diagnostics.phoneme_output_api == "native-trace"
    assert diagnostics.phoneme_parity == "exact"
    assert diagnostics.native_candidates[0].source == "modern-loader"
    assert diagnostics.native_candidates[0].phoneme_trace_api is True
    backend.close()
