from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from ..diagnostics import BackendDiagnostics


@dataclass
class TextBackend:
    """Backend for voices whose phonemes are input codepoints."""

    @property
    def diagnostics(self) -> BackendDiagnostics:
        return BackendDiagnostics(implementation="text", parity="exact")

    def phonemize(self, text: str, *, voice: str = "") -> list[list[str]]:
        del voice
        return [list(unicodedata.normalize("NFD", text))] if text else []

    def close(self) -> None:
        return None
