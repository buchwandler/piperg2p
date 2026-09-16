"""Immutable backend and frontend diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .backends.espeak.discovery import EspeakLibraryProbe
    from .lexicons.base import LexiconDiagnostics


@dataclass(frozen=True, slots=True)
class EspeakCapabilities:
    executable: str | None
    cli_available: bool
    selected_exact_library: str | None
    selected_source: str | None
    selected_data: str | None
    candidates: tuple[EspeakLibraryProbe, ...] = ()

    @property
    def exact_native_available(self) -> bool:
        return self.selected_exact_library is not None


@dataclass(frozen=True)
class BackendDiagnostics:
    requested_mode: str = "text"
    implementation: str = "text"
    executable: str | None = None
    library_path: str | None = None
    data_path: str | None = None
    discovery_source: str | None = None
    version: str | None = None
    exact_clause_api: bool = False
    fallback_reason: str | None = None
    parity: str = "exact"
    warnings: tuple[str, ...] = ()
    native_candidates: tuple[EspeakLibraryProbe, ...] = ()


@dataclass(frozen=True)
class FrontendDiagnostics:
    phoneme_type: str
    backend: str
    compatibility_profile: str = "piper-python"
    warnings: tuple[str, ...] = ()
    backend_diagnostics: BackendDiagnostics | None = None
    lexicon: LexiconDiagnostics | None = None
