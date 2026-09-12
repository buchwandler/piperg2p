from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

from ..errors import LexiconDependencyError, LexiconResourceError
from .base import (
    LexiconDiagnostics,
    LexiconPronunciation,
    normalize_phoneme_encoding,
)
from .g2lex import G2LexLookup


class LexphonLookup:
    """Resolve installed Lexphon assets and read them as Piper lexicons."""

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
        self._runtime: G2LexLookup | None = None
        self._metadata: tuple[dict[str, Any], ...] = ()
        self._closed = False

    @property
    def diagnostics(self) -> LexiconDiagnostics:
        runtime = self._runtime
        if runtime is None:
            return LexiconDiagnostics(
                enabled=True,
                implementation="lexphon",
                language=self.language,
                identifiers=self.identifiers,
                compatibility="override",
            )
        diagnostics = runtime.diagnostics
        return LexiconDiagnostics(
            enabled=True,
            implementation="lexphon",
            language=self.language,
            identifiers=self.identifiers,
            compatibility=diagnostics.compatibility,
            detail=diagnostics.detail,
            encodings=diagnostics.encodings,
            provenance=diagnostics.provenance,
        )

    @staticmethod
    def _optional_string(value: object | None) -> str | None:
        return None if value is None else str(value)

    def _ensure_runtime(self) -> G2LexLookup:
        if self._closed:
            raise LexiconResourceError("Lexphon lookup adapter is closed")
        if self._runtime is not None:
            return self._runtime
        try:
            import lexphon
        except ImportError as exc:
            raise LexiconDependencyError(
                "Lexphon support requires the optional 'lexphon' extra. "
                "Install piperg2p[lexphon]."
            ) from exc
        try:
            data_store = self.store
            if data_store is None:
                data_store = lexphon.DataStore()
            elif isinstance(data_store, (str, Path)):
                data_store = lexphon.DataStore(data_store)
            paths: list[str] = []
            metadata: list[dict[str, Any]] = []
            for identifier in self.identifiers:
                item = data_store.metadata(identifier)
                if not isinstance(item, dict):
                    raise LexiconResourceError(
                        f"Lexphon metadata for {identifier!r} is not an object"
                    )
                self._validate_catalog_metadata(identifier, item)
                paths.append(str(data_store.path(identifier)))
                metadata.append(item)
            runtime = G2LexLookup(paths, language=self.language)
            self._metadata = tuple(metadata)
            self._runtime = runtime
            return runtime
        except LexiconResourceError:
            raise
        except Exception as exc:
            identifiers = ", ".join(repr(identifier) for identifier in self.identifiers)
            raise LexiconResourceError(
                f"Could not resolve Lexphon lexicon(s) {identifiers}. "
                "Install or verify the requested data, or pass a different DataStore."
            ) from exc

    def _validate_catalog_metadata(
        self, identifier: str, metadata: dict[str, Any]
    ) -> None:
        kind = metadata.get("kind")
        if kind is not None and str(kind).casefold() != "pronunciation":
            raise LexiconResourceError(
                f"Lexphon asset {identifier!r} has unsupported kind {kind!r}; "
                "Piper lookup requires pronunciation assets"
            )
        language = metadata.get("language") or metadata.get("locale")
        if language and not str(language).lower().startswith(self.language.lower()):
            raise LexiconResourceError(
                f"Lexphon asset {identifier!r} declares language {language!r}, "
                f"not requested {self.language!r}"
            )
        encoding = metadata.get("phoneme_encoding") or metadata.get(
            "pronunciation_alphabet"
        )
        try:
            normalize_phoneme_encoding(encoding)
        except ValueError as exc:
            raise LexiconResourceError(
                f"Lexphon asset {identifier!r} uses unsupported phoneme encoding {encoding!r}"
            ) from exc

    def _convert(
        self, token: LexiconPronunciation | None
    ) -> LexiconPronunciation | None:
        if token is None:
            return None
        provenance = token.provenance
        identifier = token.lexicon_id
        if provenance is not None and self._runtime is not None:
            for index, runtime_path in enumerate(self._runtime.paths):
                if provenance.asset_path == runtime_path:
                    identifier = self.identifiers[index]
                    provenance = replace(provenance, lexicon_id=identifier)
                    break
        return replace(
            token,
            source=f"lexphon:{identifier}" if identifier else token.source,
            lexicon_id=identifier,
            provenance=provenance,
        )

    def lookup(
        self, word: str, *, tag: str | None = None
    ) -> LexiconPronunciation | None:
        runtime = self._ensure_runtime()
        try:
            return self._convert(runtime.lookup(word, tag=tag))
        except LexiconResourceError:
            raise
        except Exception as exc:
            raise LexiconResourceError(f"Lexphon lookup failed for {word!r}") from exc

    def lookup_many(
        self, words: Sequence[str], *, tag: str | None = None
    ) -> tuple[LexiconPronunciation | None, ...]:
        return tuple(self.lookup(word, tag=tag) for word in words)

    def close(self) -> None:
        if not self._closed and self._runtime is not None:
            self._runtime.close()
        self._closed = True

    def __enter__(self) -> LexphonLookup:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
