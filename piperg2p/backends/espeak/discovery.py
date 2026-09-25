from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from espeakng_runtime import inspect_espeak as runtime_inspect_espeak
from espeakng_runtime.discovery import LibraryCandidate as RuntimeLibraryCandidate
from espeakng_runtime.discovery import discover as runtime_discover
from espeakng_runtime.discovery import find_data as runtime_find_data
from espeakng_runtime.discovery import find_executable as runtime_find_executable
from espeakng_runtime.discovery import (
    iter_library_candidates as runtime_iter_library_candidates,
)
from espeakng_runtime.discovery import (
    maybe_find_executable as runtime_maybe_find_executable,
)
from espeakng_runtime.discovery import probe_library as runtime_probe_library
from espeakng_runtime.discovery import select_native as runtime_select_native
from espeakng_runtime.errors import EspeakUnavailableError

from ...diagnostics import EspeakCapabilities
from ...errors import BackendUnavailableError
from .backend import _runtime_paths


@dataclass(frozen=True)
class EspeakPaths:
    executable: str | None = None
    library: str | None = None
    data: str | None = None
    source: str = "unknown"


@dataclass(frozen=True, slots=True)
class EspeakLibraryCandidate:
    library: str
    source: str
    data: str | None = None
    explicit: bool = False


@dataclass(frozen=True, slots=True)
class EspeakLibraryProbe:
    library: str
    source: str
    data: str | None
    loadable: bool
    exact_clause_api: bool
    phoneme_trace_api: bool = False
    error: str | None = None


@dataclass(frozen=True)
class EspeakNativeSelection:
    candidate: EspeakLibraryCandidate | None
    probes: tuple[EspeakLibraryProbe, ...]
    explicit: bool


def _legacy_source(source: str | None) -> str | None:
    return "modern-loader" if source == "espeakng-loader" else source


def _candidate(value: Any) -> EspeakLibraryCandidate:
    return EspeakLibraryCandidate(
        library=str(value.library),
        source=_legacy_source(value.source) or "unknown",
        data=value.data,
        explicit=bool(value.explicit),
    )


def _probe(value: Any) -> EspeakLibraryProbe:
    return EspeakLibraryProbe(
        library=str(value.library),
        source=_legacy_source(value.source) or "unknown",
        data=value.data,
        loadable=bool(value.loadable),
        exact_clause_api=bool(value.exact_clause_api),
        phoneme_trace_api=bool(getattr(value, "phoneme_trace_api", False)),
        error=value.error,
    )


def _runtime_args(
    *,
    executable: str | None,
    library: str | None,
    data: str | None,
) -> tuple[str | None, str | None, str | None]:
    return _runtime_paths(executable=executable, library=library, data=data)


def maybe_find_executable(explicit: str | None = None) -> str | None:
    executable, _, _ = _runtime_args(executable=explicit, library=None, data=None)
    return runtime_maybe_find_executable(executable)


def find_executable(explicit: str | None = None) -> str:
    executable, _, _ = _runtime_args(executable=explicit, library=None, data=None)
    try:
        return runtime_find_executable(executable)
    except EspeakUnavailableError as exc:
        raise BackendUnavailableError(str(exc)) from exc


def find_data(
    explicit: str | None = None,
    executable: str | None = None,
    library: str | None = None,
) -> str | None:
    effective_executable, effective_library, effective_data = _runtime_args(
        executable=executable,
        library=library,
        data=explicit,
    )
    try:
        return runtime_find_data(
            effective_data,
            executable=effective_executable,
            library=effective_library,
        )
    except EspeakUnavailableError as exc:
        raise BackendUnavailableError(str(exc)) from exc


def iter_library_candidates(
    explicit: str | None = None,
    *,
    executable: str | None = None,
    data: str | None = None,
) -> tuple[EspeakLibraryCandidate, ...]:
    effective_executable, effective_library, effective_data = _runtime_args(
        executable=executable,
        library=explicit,
        data=data,
    )
    try:
        values = runtime_iter_library_candidates(
            effective_library,
            executable=effective_executable,
            data=effective_data,
        )
    except EspeakUnavailableError as exc:
        raise BackendUnavailableError(str(exc)) from exc
    return tuple(_candidate(value) for value in values)


def find_library(
    explicit: str | None = None,
    executable: str | None = None,
) -> str | None:
    candidates = iter_library_candidates(explicit, executable=executable)
    return candidates[0].library if candidates else None


def probe_library_candidate(
    candidate: EspeakLibraryCandidate,
) -> EspeakLibraryProbe:
    try:
        return _probe(
            runtime_probe_library(
                RuntimeLibraryCandidate(
                    library=candidate.library,
                    source=candidate.source,
                    data=candidate.data,
                    explicit=candidate.explicit,
                )
            )
        )
    except EspeakUnavailableError as exc:
        raise BackendUnavailableError(str(exc)) from exc


def select_exact_native(
    *,
    library: str | None = None,
    executable: str | None = None,
    data: str | None = None,
) -> EspeakNativeSelection:
    effective_executable, effective_library, effective_data = _runtime_args(
        executable=executable,
        library=library,
        data=data,
    )
    try:
        candidate, probes = runtime_select_native(
            library=effective_library,
            executable=effective_executable,
            data=effective_data,
            require_exact_clauses=True,
        )
    except EspeakUnavailableError as exc:
        raise BackendUnavailableError(str(exc)) from exc
    return EspeakNativeSelection(
        _candidate(candidate) if candidate is not None else None,
        tuple(_probe(value) for value in probes),
        candidate.explicit if candidate is not None else bool(effective_library),
    )


def inspect_espeak(
    *,
    executable: str | None = None,
    library: str | None = None,
    data: str | None = None,
) -> EspeakCapabilities:
    effective_executable, effective_library, effective_data = _runtime_args(
        executable=executable,
        library=library,
        data=data,
    )
    try:
        info = runtime_inspect_espeak(
            executable=effective_executable,
            library=effective_library,
            data=effective_data,
            require_exact_clauses=True,
        )
    except EspeakUnavailableError as exc:
        raise BackendUnavailableError(str(exc)) from exc
    return EspeakCapabilities(
        executable=info.executable,
        cli_available=info.cli_available,
        selected_exact_library=info.selected_library,
        selected_source=_legacy_source(info.selected_source),
        selected_data=info.selected_data,
        candidates=tuple(_probe(value) for value in info.candidates),
    )


def discover(
    *,
    executable: str | None = None,
    library: str | None = None,
    data: str | None = None,
    require_executable: bool = True,
) -> EspeakPaths:
    effective_executable, effective_library, effective_data = _runtime_args(
        executable=executable,
        library=library,
        data=data,
    )
    try:
        paths = runtime_discover(
            executable=effective_executable,
            library=effective_library,
            data=effective_data,
            require_executable=require_executable,
        )
    except EspeakUnavailableError as exc:
        raise BackendUnavailableError(str(exc)) from exc
    return EspeakPaths(
        executable=paths.executable,
        library=paths.library,
        data=paths.data,
        source=_legacy_source(paths.source) or "unknown",
    )
