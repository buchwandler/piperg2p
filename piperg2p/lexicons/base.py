from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LexiconPronunciation:
    pronunciation: str
    source: str
    lexicon_id: str | None = None
    matched_key: str | None = None
    source_encoding: str | None = None


@dataclass(frozen=True)
class LexiconDiagnostics:
    enabled: bool
    implementation: str | None
    language: str | None
    identifiers: tuple[str, ...]
    compatibility: str
    detail: str | None = None


class PronunciationLookup(Protocol):
    def lookup(self, word: str, *, tag: str | None = None) -> LexiconPronunciation | None: ...

    def lookup_many(
        self, words: Sequence[str], *, tag: str | None = None
    ) -> tuple[LexiconPronunciation | None, ...]: ...

    @property
    def diagnostics(self) -> LexiconDiagnostics: ...

    def close(self) -> None: ...
