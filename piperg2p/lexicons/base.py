from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

SUPPORTED_PHONEME_ENCODINGS = frozenset({"ipa", "espeak-ipa3"})


def normalize_phoneme_encoding(value: object | None) -> str:
    """Return the canonical runtime name for a lexicon pronunciation encoding."""
    if value is None:
        return "ipa"
    normalized = str(value).strip().casefold().replace("_", "-")
    if normalized in {"ipa", "unicode-ipa", "ipa-unicode", "generic-ipa"}:
        return "ipa"
    if normalized in {"espeak-ipa3", "e-speak-ipa3", "piper-ipa3"}:
        return "espeak-ipa3"
    raise ValueError(f"unsupported phoneme encoding {value!r}")


def compatibility_for_encodings(encodings: Sequence[str]) -> str:
    """Return the public compatibility label for active lexicon encodings."""
    values = frozenset(encodings)
    if values == {"ipa"}:
        return "override-generic-ipa"
    if values == {"espeak-ipa3"}:
        return "piper-espeak-frozen"
    if values:
        return "mixed-lexicon-encodings"
    return "override"


@dataclass(frozen=True)
class LexiconProvenance:
    """Immutable identity and provenance for a pronunciation asset."""

    lexicon_id: str | None = None
    language: str | None = None
    kind: str | None = None
    source_encoding: str = "ipa"
    data_version: str | None = None
    producer: str | None = None
    transform: str | None = None
    generator: str | None = None
    asset_path: str | None = None


@dataclass(frozen=True)
class LexiconPronunciation:
    pronunciation: str
    source: str
    lexicon_id: str | None = None
    matched_key: str | None = None
    source_encoding: str | None = None
    provenance: LexiconProvenance | None = None

    def __post_init__(self) -> None:
        if self.source_encoding is not None:
            object.__setattr__(
                self,
                "source_encoding",
                normalize_phoneme_encoding(self.source_encoding),
            )
        if self.provenance is not None and self.source_encoding is None:
            object.__setattr__(self, "source_encoding", self.provenance.source_encoding)


@dataclass(frozen=True)
class LexiconDiagnostics:
    enabled: bool
    implementation: str | None
    language: str | None
    identifiers: tuple[str, ...]
    compatibility: str
    detail: str | None = None
    encodings: tuple[str, ...] = ()
    provenance: tuple[LexiconProvenance, ...] = ()


class PronunciationLookup(Protocol):
    def lookup(
        self, word: str, *, tag: str | None = None
    ) -> LexiconPronunciation | None: ...

    def lookup_many(
        self, words: Sequence[str], *, tag: str | None = None
    ) -> tuple[LexiconPronunciation | None, ...]: ...

    @property
    def diagnostics(self) -> LexiconDiagnostics: ...

    def close(self) -> None: ...
