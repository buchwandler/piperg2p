"""Immutable backend and frontend diagnostics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackendDiagnostics:
    requested_mode: str = "text"
    implementation: str = "text"
    executable: str | None = None
    library_path: str | None = None
    data_path: str | None = None
    version: str | None = None
    exact_clause_api: bool = False
    fallback_reason: str | None = None
    parity: str = "exact"
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class FrontendDiagnostics:
    phoneme_type: str
    backend: str
    compatibility_profile: str = "piper-python"
    warnings: tuple[str, ...] = ()
    backend_diagnostics: BackendDiagnostics | None = None
