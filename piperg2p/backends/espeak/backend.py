from __future__ import annotations

import os
from dataclasses import dataclass

from espeakng_runtime import EspeakRuntime, RuntimeInfo, inspect_espeak
from espeakng_runtime.errors import (
    CapabilityError,
    EspeakConflictError,
    EspeakUnavailableError,
    VoiceNotFoundError,
)
from espeakng_runtime.errors import PhonemizationError as RuntimePhonemizationError

from ..._warnings import warn_external
from ...diagnostics import BackendDiagnostics
from ...errors import (
    BackendFallbackWarning,
    BackendUnavailableError,
    PhonemizationError,
)
from .clauses import (
    Clause,
    compose_clauses,
    from_runtime_clause,
    split_cli_clauses,
)


def _runtime_paths(
    *,
    executable: str | None,
    library: str | None,
    data: str | None,
) -> tuple[str | None, str | None, str | None]:
    return (
        executable
        if executable is not None
        else os.getenv("PIPERG2P_ESPEAK_EXECUTABLE"),
        library if library is not None else os.getenv("PIPERG2P_ESPEAK_LIBRARY"),
        data if data is not None else os.getenv("PIPERG2P_ESPEAK_DATA"),
    )


def _legacy_source(source: str | None) -> str | None:
    return "modern-loader" if source == "espeakng-loader" else source


def _diagnostics_from_runtime(
    info: RuntimeInfo,
    *,
    native_candidates: tuple[object, ...] = (),
    warnings: tuple[str, ...] = (),
) -> BackendDiagnostics:
    from .discovery import EspeakLibraryProbe

    candidates = tuple(
        EspeakLibraryProbe(
            library=value.library,
            source=_legacy_source(value.source) or "unknown",
            data=value.data,
            loadable=value.loadable,
            exact_clause_api=value.exact_clause_api,
            error=value.error,
        )
        for value in native_candidates
    )
    return BackendDiagnostics(
        requested_mode=info.requested_mode,
        implementation=info.implementation,
        executable=info.executable,
        library_path=info.library,
        data_path=info.data,
        discovery_source=_legacy_source(info.source),
        version=info.version,
        exact_clause_api=info.exact_clause_api,
        fallback_reason=info.fallback_reason,
        parity=info.parity,
        warnings=warnings,
        native_candidates=candidates,
    )


def _piper_fallback_message(info: RuntimeInfo) -> str:
    reason = info.fallback_reason or "runtime selected CLI best-effort mode"
    if info.fallback_code == "exact-clause-api-unavailable":
        prefix = "exact Piper eSpeak clause API unavailable; using CLI best-effort fallback: "
    else:
        prefix = "native eSpeak library unavailable; using CLI best-effort fallback: "
    return prefix + reason


def _raise_backend_unavailable(exc: Exception) -> None:
    raise BackendUnavailableError(str(exc)) from exc


def _raise_phonemization_error(exc: Exception) -> None:
    raise PhonemizationError(str(exc)) from exc


@dataclass
class EspeakBackend:
    mode: str = "auto"
    executable: str | None = None
    library: str | None = None
    data: str | None = None
    vowel_clusters: frozenset[tuple[str, ...]] = frozenset()
    merge_vowel_clusters: bool = True
    timeout: float | None = None

    def __post_init__(self) -> None:
        if self.mode not in {"auto", "native", "cli"}:
            raise ValueError("eSpeak mode must be 'auto', 'native', or 'cli'")
        executable, library, data = _runtime_paths(
            executable=self.executable,
            library=self.library,
            data=self.data,
        )
        try:
            self._runtime = EspeakRuntime(
                mode=self.mode,
                executable=executable,
                library=library,
                data=data,
                timeout=self.timeout,
                prefer_exact_clauses=(self.mode != "cli"),
            )
        except (EspeakUnavailableError, EspeakConflictError) as exc:
            _raise_backend_unavailable(exc)

        info = self._runtime.info
        if self.mode == "native" and (
            info.implementation != "native" or not info.exact_clause_api
        ):
            self._runtime.close()
            raise BackendUnavailableError(
                "native eSpeak runtime lacks Piper's exact clause capability"
            )
        native_candidates: tuple[object, ...] = ()
        if self.mode != "cli":
            inspection = inspect_espeak(
                executable=executable,
                library=library,
                data=data,
                require_exact_clauses=True,
            )
            native_candidates = inspection.candidates
        fallback_reason = info.fallback_reason
        warnings: tuple[str, ...] = ()
        if self.mode == "auto" and info.implementation == "cli" and fallback_reason:
            message = _piper_fallback_message(info)
            warn_external(message, BackendFallbackWarning)
            warnings = (message,)
        self._diagnostics = _diagnostics_from_runtime(
            info,
            native_candidates=native_candidates,
            warnings=warnings,
        )

    @property
    def diagnostics(self) -> BackendDiagnostics:
        return self._diagnostics

    def phonemize(self, text: str, *, voice: str) -> list[list[str]]:
        if not text:
            return []
        clusters = self.vowel_clusters if self.merge_vowel_clusters else frozenset()
        info = self._runtime.info
        try:
            if info.implementation == "native" and info.exact_clause_api:
                clauses = [
                    from_runtime_clause(value)
                    for value in self._runtime.clauses(text, voice=voice, exact=True)
                ]
            else:
                if self.mode == "native":
                    raise BackendUnavailableError(
                        "native eSpeak runtime lacks Piper's exact clause capability"
                    )
                clauses = [
                    Clause(
                        phonemes=self._runtime.phonemize(body, voice=voice),
                        terminator=terminator,
                        sentence_end=sentence_end,
                    )
                    for body, terminator, sentence_end in split_cli_clauses(text)
                ]
        except BackendUnavailableError:
            raise
        except (VoiceNotFoundError, RuntimePhonemizationError) as exc:
            _raise_phonemization_error(exc)
        except CapabilityError as exc:
            _raise_backend_unavailable(exc)
        except EspeakConflictError as exc:
            _raise_backend_unavailable(exc)
        return compose_clauses(clauses, clusters)

    def close(self) -> None:
        self._runtime.close()

    def __enter__(self) -> EspeakBackend:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
