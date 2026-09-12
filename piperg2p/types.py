"""Public immutable result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .diagnostics import FrontendDiagnostics


@dataclass(frozen=True)
class EncodeResult:
    ids: tuple[int, ...]
    missing_phonemes: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class PhonemeSentence:
    phonemes: tuple[str, ...]
    ids: tuple[int, ...]
    missing_phonemes: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    metadata: tuple[tuple[str, Any], ...] = ()

    @property
    def phoneme_string(self) -> str:
        return "".join(self.phonemes)


@dataclass(frozen=True)
class PhonemizeResult:
    text: str
    sentences: tuple[PhonemeSentence, ...]
    diagnostics: FrontendDiagnostics | None = None
    warnings: tuple[str, ...] = ()

    @property
    def phonemes(self) -> tuple[str, ...]:
        return tuple(
            phone for sentence in self.sentences for phone in sentence.phonemes
        )

    @property
    def ids(self) -> tuple[int, ...]:
        return tuple(
            identifier for sentence in self.sentences for identifier in sentence.ids
        )
