"""Public immutable result and source-aligned API types."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, TypeAlias

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


@dataclass
class TokenSpan:
    """A source-preserving token using half-open character offsets."""

    text: str
    char_start: int
    char_end: int
    lang: str | None = None
    extended_text: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def start(self) -> int:
        return self.char_start

    @property
    def end(self) -> int:
        return self.char_end


@dataclass(frozen=True)
class TokenAnnotation:
    start: int
    end: int
    text: str | None = None
    pos: str | None = None
    tag: str | None = None
    lemma: str | None = None
    language: str | None = None

    @property
    def char_start(self) -> int:
        return self.start

    @property
    def char_end(self) -> int:
        return self.end


TokenAnnotationLike: TypeAlias = TokenAnnotation | Mapping[str, Any]


@dataclass(frozen=True)
class OverrideSpan:
    char_start: int
    char_end: int
    attrs: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.char_start < 0 or self.char_end < self.char_start:
            raise ValueError("override span offsets must be a non-negative half-open range")
        object.__setattr__(self, "attrs", MappingProxyType(dict(self.attrs)))

    @property
    def start(self) -> int:
        return self.char_start

    @property
    def end(self) -> int:
        return self.char_end


OverrideSpanLike: TypeAlias = OverrideSpan | Mapping[str, Any] | Sequence[Any]


@dataclass(frozen=True)
class LanguageRoute:
    char_start: int
    char_end: int
    language: str
    requested_language: str | None = None
    reason: str | None = None
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class LanguageRoutingConfig:
    mode: str = "explicit"
    languages: tuple[str, ...] = ()
    lexicons: Mapping[str, Sequence[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.mode not in {"explicit", "auto"}:
            raise ValueError("language routing mode must be 'explicit' or 'auto'")
        object.__setattr__(self, "languages", tuple(self.languages))
        object.__setattr__(self, "lexicons", MappingProxyType(dict(self.lexicons)))


@dataclass(frozen=True)
class LexiconEvidence:
    lexicon_id: str | None = None
    lexicon_name: str | None = None
    matched_key: str | None = None
    source_encoding: str | None = None
    pronunciation: str | None = None
    provenance: Any = None
    rating: Any = None


@dataclass
class PhonemizeResult:
    """High-level result with flattened convenience views and Piper sentence data."""

    clean_text: str = ""
    tokens: list[TokenSpan] = field(default_factory=list)
    extended_text: str = ""
    phonemes: str = ""
    token_ids: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    language_routes: list[LanguageRoute] = field(default_factory=list)
    sentences: tuple[PhonemeSentence, ...] = ()
    diagnostics: FrontendDiagnostics | None = None
    missing_phonemes: tuple[str, ...] = ()

    @property
    def text(self) -> str:
        return self.clean_text

    @property
    def ids(self) -> tuple[int, ...]:
        return tuple(self.token_ids)

    @property
    def phoneme_symbols(self) -> tuple[str, ...]:
        return tuple(self.phonemes)

    def __post_init__(self) -> None:
        self.tokens = list(self.tokens)
        self.token_ids = list(self.token_ids)
        self.warnings = list(self.warnings)
        self.language_routes = list(self.language_routes)
        self.sentences = tuple(self.sentences)
        if not self.phonemes and self.sentences:
            self.phonemes = "".join(sentence.phoneme_string for sentence in self.sentences)
        if not self.token_ids and self.sentences:
            self.token_ids = [identifier for sentence in self.sentences for identifier in sentence.ids]
        if not self.missing_phonemes and self.sentences:
            self.missing_phonemes = tuple(
                missing
                for sentence in self.sentences
                for missing in sentence.missing_phonemes
            )
        if not self.warnings and self.sentences:
            self.warnings = [
                warning for sentence in self.sentences for warning in sentence.warnings
            ]