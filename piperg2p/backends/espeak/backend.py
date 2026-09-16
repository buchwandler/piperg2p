from __future__ import annotations

from dataclasses import dataclass

from ..._warnings import warn_external
from ...diagnostics import BackendDiagnostics
from ...errors import BackendFallbackWarning, BackendUnavailableError
from . import discovery as discovery_module
from .clauses import compose_clauses
from .cli import EspeakCliBackend
from .discovery import (
    EspeakLibraryProbe,
    EspeakNativeSelection,
    maybe_find_executable,
    select_exact_native,
)
from .native import NativeEspeakProvider

discover = discovery_module.discover


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
        selection: EspeakNativeSelection | None = None
        fallback_code: str | None = None
        fallback_detail: str | None = None

        if self.mode == "cli":
            self._provider = self._make_cli()
        else:
            selection = select_exact_native(
                library=self.library,
                executable=self.executable,
                data=self.data,
            )
            if selection.candidate is not None:
                try:
                    self._provider = NativeEspeakProvider(
                        library=selection.candidate.library,
                        data=selection.candidate.data,
                        executable=maybe_find_executable(self.executable),
                        discovery_source=selection.candidate.source,
                        strict=True,
                    )
                except (BackendUnavailableError, OSError) as exc:
                    if "espeak_TextToPhonemesWithTerminator" in str(exc):
                        fallback_code = "terminator API unavailable"
                        fallback_detail = "terminator API unavailable"
                    else:
                        fallback_code = f"{type(exc).__name__}: {exc}"
                        fallback_detail = str(exc)
                    if self.mode == "native":
                        raise
                    try:
                        self._provider = self._make_cli()
                    except BackendUnavailableError as cli_exc:
                        raise BackendUnavailableError(
                            "no exact native Piper eSpeak library found; "
                            "CLI fallback is unavailable"
                        ) from cli_exc
            elif self.mode == "native":
                raise BackendUnavailableError(self._native_error(selection.probes))
            else:
                fallback_code, fallback_detail = self._native_failure_reason(
                    selection.probes, selection.explicit
                )
                try:
                    self._provider = self._make_cli()
                except BackendUnavailableError as exc:
                    raise BackendUnavailableError(
                        "no exact native Piper eSpeak library found; "
                        "CLI fallback is unavailable"
                    ) from exc
        provider_diagnostics = self._provider.diagnostics
        native_candidates = selection.probes if selection is not None else ()
        fallback_reason: str | None
        if fallback_code is not None:
            fallback_reason = fallback_code
            message = self._fallback_warning(
                fallback_code, fallback_detail or "", selection
            )
            warn_external(message, BackendFallbackWarning)
        else:
            fallback_reason = provider_diagnostics.fallback_reason
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
            parity=provider_diagnostics.parity,
            warnings=(fallback_reason,)
            if fallback_reason
            else provider_diagnostics.warnings,
            native_candidates=native_candidates,
        )

    def _make_cli(self) -> EspeakCliBackend:
        return EspeakCliBackend(
            executable=self.executable,
            data_path=self.data,
            vowel_clusters=self.vowel_clusters
            if self.merge_vowel_clusters
            else frozenset(),
            timeout=self.timeout,
        )

    @staticmethod
    def _native_error(probes: tuple[EspeakLibraryProbe, ...]) -> str:
        if not probes or not any(probe.loadable for probe in probes):
            return "no usable eSpeak native library could be loaded"
        return (
            "no exact Piper-compatible eSpeak native library is available; "
            "the required symbol espeak_TextToPhonemesWithTerminator was not found"
        )

    @staticmethod
    def _native_failure_reason(
        probes: tuple[EspeakLibraryProbe, ...], explicit: bool
    ) -> tuple[str, str]:
        if not probes:
            return (
                "native-library-unavailable",
                "no discovered native library was found",
            )
        if not any(probe.loadable for probe in probes):
            detail = next(
                (probe.error for probe in probes if probe.error),
                "no discovered native library could be loaded",
            )
            return "native-library-load-error", detail
        if explicit:
            probe = probes[0]
            return (
                "terminator-api-unavailable",
                f"{probe.library} does not export espeak_TextToPhonemesWithTerminator",
            )
        return (
            "terminator-api-unavailable",
            "no discovered native library exports espeak_TextToPhonemesWithTerminator",
        )

    @staticmethod
    def _fallback_warning(
        code: str,
        detail: str,
        selection: EspeakNativeSelection | None,
    ) -> str:
        if code == "terminator-api-unavailable":
            if selection is not None and selection.explicit:
                prefix = (
                    "configured eSpeak library does not provide the exact "
                    "Piper clause API; using CLI best-effort fallback: "
                )
            else:
                prefix = (
                    "exact Piper eSpeak clause API unavailable; using CLI "
                    "best-effort fallback: "
                )
        else:
            prefix = (
                "native eSpeak library unavailable; using CLI best-effort fallback: "
            )
        return prefix + detail

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

    def __enter__(self) -> EspeakBackend:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
