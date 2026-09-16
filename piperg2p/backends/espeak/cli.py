from __future__ import annotations

from dataclasses import dataclass

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
from .clauses import Clause, compose_clauses, split_cli_clauses


@dataclass
class EspeakCliBackend:
    """Compatibility facade for Piper's historical CLI backend."""

    executable: str | None = None
    vowel_clusters: frozenset[tuple[str, ...]] = frozenset()
    timeout: float | None = None
    data_path: str | None = None

    def __post_init__(self) -> None:
        executable, _, data = _runtime_paths(
            executable=self.executable,
            library=None,
            data=self.data_path,
        )
        try:
            self._runtime = EspeakRuntime(
                mode="cli",
                executable=executable,
                data=data,
                timeout=self.timeout,
            )
        except (EspeakUnavailableError, EspeakConflictError) as exc:
            raise BackendUnavailableError(str(exc)) from exc
        info = self._runtime.info
        self.executable = info.executable
        self.data_path = info.data
        self._diagnostics = _diagnostics_from_runtime(info)

    @property
    def diagnostics(self) -> BackendDiagnostics:
        return self._diagnostics

    def phonemize(self, text: str, *, voice: str) -> list[list[str]]:
        if not text:
            return []
        try:
            clauses = [
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
        return compose_clauses(clauses, self.vowel_clusters)

    def close(self) -> None:
        self._runtime.close()
