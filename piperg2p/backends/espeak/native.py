from __future__ import annotations

from espeakng_runtime import EspeakRuntime
from espeakng_runtime.errors import (
    CapabilityError,
    EspeakConflictError,
    EspeakUnavailableError,
    VoiceNotFoundError,
)
from espeakng_runtime.errors import PhonemizationError as RuntimePhonemizationError

from ...diagnostics import BackendDiagnostics
from ...errors import BackendUnavailableError, PhonemizationError
from .backend import _diagnostics_from_runtime, _runtime_paths
from .clauses import Clause, from_runtime_clause, split_cli_clauses


class NativeEspeakProvider:
    """Compatibility facade for Piper's historical native provider."""

    def __init__(
        self,
        *,
        library: str | None = None,
        data: str | None = None,
        executable: str | None = None,
        discovery_source: str | None = None,
        strict: bool = False,
    ) -> None:
        del discovery_source
        executable, library, data = _runtime_paths(
            executable=executable,
            library=library,
            data=data,
        )
        try:
            self._runtime = EspeakRuntime(
                mode="native",
                executable=executable,
                library=library,
                data=data,
                prefer_exact_clauses=strict,
            )
        except (EspeakUnavailableError, EspeakConflictError) as exc:
            raise BackendUnavailableError(str(exc)) from exc
        info = self._runtime.info
        self.library_path = info.library
        self.data_path = info.data
        self.executable = info.executable
        self.discovery_source = info.source
        self.exact_clause_api = info.exact_clause_api
        self.version = info.version
        self._diagnostics = _diagnostics_from_runtime(info)

    @property
    def diagnostics(self) -> BackendDiagnostics:
        return self._diagnostics

    def clauses(self, text: str, voice: str) -> list[Clause]:
        if not text:
            return []
        try:
            if self.exact_clause_api:
                return [
                    from_runtime_clause(value)
                    for value in self._runtime.clauses(text, voice=voice, exact=True)
                ]
            return [
                Clause(
                    phonemes=self._runtime.phonemize(body, voice=voice),
                    terminator=terminator,
                    sentence_end=sentence_end,
                )
                for body, terminator, sentence_end in split_cli_clauses(text)
            ]
        except (VoiceNotFoundError, RuntimePhonemizationError) as exc:
            raise PhonemizationError(str(exc)) from exc
        except CapabilityError as exc:
            raise BackendUnavailableError(str(exc)) from exc
        except EspeakConflictError as exc:
            raise BackendUnavailableError(str(exc)) from exc

    def close(self) -> None:
        self._runtime.close()

    def __enter__(self) -> NativeEspeakProvider:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
