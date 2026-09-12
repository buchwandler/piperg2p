from __future__ import annotations

import warnings
from dataclasses import dataclass

from ...diagnostics import BackendDiagnostics
from ...errors import BackendFallbackWarning, BackendUnavailableError
from .clauses import compose_clauses
from .cli import EspeakCliBackend
from .discovery import discover
from .native import NativeEspeakProvider


@dataclass
class EspeakBackend:
    mode: str = "auto"
    executable: str | None = None
    library: str | None = None
    data: str | None = None
    vowel_clusters: frozenset[tuple[str, ...]] = frozenset()
    strict_native: bool = False
    merge_vowel_clusters: bool = True
    timeout: float | None = None

    def __post_init__(self) -> None:
        if self.mode not in {"auto", "native", "cli"}:
            raise ValueError("eSpeak mode must be 'auto', 'native', or 'cli'")
        self._provider: NativeEspeakProvider | EspeakCliBackend
        fallback_reason: str | None = None
        if self.mode in {"auto", "native"}:
            try:
                paths = discover(
                    executable=self.executable,
                    library=self.library,
                    data=self.data,
                    require_executable=self.mode == "auto" or self.executable is not None,
                )
                self._provider = NativeEspeakProvider(
                    library=paths.library,
                    data=paths.data,
                    executable=paths.executable,
                    discovery_source=paths.source,
                    strict=self.strict_native or self.mode in {"native", "auto"},
                )
            except (BackendUnavailableError, OSError) as exc:
                if self.mode == "native":
                    raise
                if "lacks espeak_TextToPhonemesWithTerminator" in str(exc):
                    fallback_reason = "terminator API unavailable"
                else:
                    fallback_reason = f"{type(exc).__name__}: {exc}"
            self._provider = EspeakCliBackend(
                executable=self.executable,
                data_path=self.data,
                vowel_clusters=self.vowel_clusters if self.merge_vowel_clusters else frozenset(),
                timeout=self.timeout,
            )
        provider_diagnostics = self._provider.diagnostics
        if fallback_reason:
            warnings.warn(
                f"native eSpeak unavailable, using CLI: {fallback_reason}",
                BackendFallbackWarning,
                stacklevel=2,
            )
            self._diagnostics = BackendDiagnostics(
                requested_mode=self.mode,
                implementation=provider_diagnostics.implementation,
                executable=provider_diagnostics.executable,
                library_path=provider_diagnostics.library_path,
                data_path=provider_diagnostics.data_path,
                discovery_source=provider_diagnostics.discovery_source,
                version=provider_diagnostics.version,
                exact_clause_api=provider_diagnostics.exact_clause_api,
                fallback_reason=fallback_reason,
                parity="best-effort",
                warnings=(fallback_reason,),
            )
        else:
            self._diagnostics = BackendDiagnostics(
                requested_mode=self.mode,
                implementation=provider_diagnostics.implementation,
                executable=provider_diagnostics.executable,
                library_path=provider_diagnostics.library_path,
                data_path=provider_diagnostics.data_path,
                discovery_source=provider_diagnostics.discovery_source,
                version=provider_diagnostics.version,
                exact_clause_api=provider_diagnostics.exact_clause_api,
                fallback_reason=provider_diagnostics.fallback_reason,
                parity=provider_diagnostics.parity,
                warnings=provider_diagnostics.warnings,
            )

    @property
    def diagnostics(self) -> BackendDiagnostics:
        return self._diagnostics

    def phonemize(self, text: str, *, voice: str) -> list[list[str]]:
        if isinstance(self._provider, NativeEspeakProvider):
            clusters = self.vowel_clusters if self.merge_vowel_clusters else frozenset()
            return compose_clauses(self._provider.clauses(text, voice), clusters)
        return self._provider.phonemize(text, voice=voice)

    def close(self) -> None:
        self._provider.close()

    def __enter__(self) -> "EspeakBackend":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
