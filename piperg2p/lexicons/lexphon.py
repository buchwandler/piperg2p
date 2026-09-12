from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ..errors import LexiconDependencyError, LexiconResourceError
from .base import LexiconDiagnostics, LexiconPronunciation


class LexphonLookup:
    """Lazy, lexicon-only adapter around Lexphon."""

    def __init__(
        self,
        language: str,
        identifiers: Sequence[str],
        *,
        store: Any = None,
    ) -> None:
        self.language = language
        self.identifiers = tuple(identifiers)
        self.store = store
        self._runtime: Any = None
        self._closed = False

    @property
    def diagnostics(self) -> LexiconDiagnostics:
        return LexiconDiagnostics(
            enabled=True,
            implementation="lexphon",
            language=self.language,
            identifiers=self.identifiers,
            compatibility="override",
        )

    def _ensure_runtime(self) -> Any:
        if self._closed:
            raise LexiconResourceError("Lexphon lookup adapter is closed")
        if self._runtime is not None:
            return self._runtime
        try:
            from lexphon import Phonemizer  # type: ignore[import-not-found]
        except ImportError as exc:
            raise LexiconDependencyError(
                "Lexphon support requires the optional 'lexphon' extra. Install piperg2p[lexphon]."
            ) from exc
        try:
            self._runtime = Phonemizer(
                self.language,
                lexicons=list(self.identifiers),
                store=self.store,
                fallback=None,
            )
        except Exception as exc:
            identifiers = ", ".join(repr(identifier) for identifier in self.identifiers)
            raise LexiconResourceError(
                f"Could not open Lexphon lexicon(s) {identifiers}. "
                "Install or verify the requested data, or pass a different DataStore."
            ) from exc
        return self._runtime

    @staticmethod
    def _convert(token: Any) -> LexiconPronunciation | None:
        if token is None:
            return None
        if isinstance(token, LexiconPronunciation):
            return token
        source = getattr(token, "source", "lexphon")
        source_name = getattr(source, "value", None) or str(source)
        pronunciation = getattr(token, "pronunciation", None) or getattr(token, "text", token)
        return LexiconPronunciation(
            pronunciation=str(pronunciation),
            source=source_name,
            lexicon_id=getattr(token, "lexicon_id", None),
            matched_key=getattr(token, "matched_key", None),
            source_encoding=getattr(token, "source_encoding", None),
        )

    def lookup(self, word: str, *, tag: str | None = None) -> LexiconPronunciation | None:
        runtime = self._ensure_runtime()
        try:
            token = runtime.lookup_lexicon(word, tag=tag)
        except Exception as exc:
            raise LexiconResourceError(f"Lexphon lookup failed for {word!r}") from exc
        return self._convert(token)

    def lookup_many(
        self, words: Sequence[str], *, tag: str | None = None
    ) -> tuple[LexiconPronunciation | None, ...]:
        runtime = self._ensure_runtime()
        try:
            tokens = runtime.lookup_many(tuple(words), tag=tag)
        except AttributeError:
            return tuple(self.lookup(word, tag=tag) for word in words)
        except Exception as exc:
            raise LexiconResourceError("Lexphon batch lookup failed") from exc
        return tuple(self._convert(token) for token in tokens)

    def close(self) -> None:
        if not self._closed and self._runtime is not None:
            self._runtime.close()
        self._closed = True

    def __enter__(self) -> "LexphonLookup":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
