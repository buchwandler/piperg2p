from __future__ import annotations

from typing import Protocol

from ..diagnostics import BackendDiagnostics


class PhonemeBackend(Protocol):
    @property
    def diagnostics(self) -> BackendDiagnostics: ...

    def phonemize(self, text: str, *, voice: str) -> list[list[str]]: ...

    def close(self) -> None: ...
