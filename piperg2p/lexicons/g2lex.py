from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ..errors import LexiconDependencyError, LexiconResourceError
from .base import (
    LexiconDiagnostics,
    LexiconPronunciation,
    LexiconProvenance,
    compatibility_for_encodings,
    normalize_phoneme_encoding,
)


class G2LexLookup:
    """Lazy exact-key lookup over explicitly supplied G2Lex assets."""

    def __init__(self, paths: Sequence[str | Path], *, language: str | None = None) -> None:
        self.paths = tuple(str(path) for path in paths)
        self.language = language
        self._assets: tuple[Any, ...] | None = None
        self._provenance: tuple[LexiconProvenance, ...] = ()
        self._closed = False

    @property
    def diagnostics(self) -> LexiconDiagnostics:
        encodings = tuple(item.source_encoding for item in self._provenance)
        return LexiconDiagnostics(
            enabled=True,
            implementation="g2lex",
            language=self.language,
            identifiers=self.paths,
            compatibility=compatibility_for_encodings(encodings),
            encodings=encodings,
            provenance=self._provenance,
        )

    @staticmethod
    def _metadata(asset: Any) -> dict[str, Any]:
        metadata = getattr(asset, "metadata", None)
        if isinstance(metadata, dict):
            return metadata
        source = getattr(asset, "source", None)
        if source is not None:
            values = getattr(source, "__dict__", None)
            if isinstance(values, dict):
                return values
        return {}

    @staticmethod
    def _metadata_value(metadata: dict[str, Any], *keys: str) -> Any:
        source = metadata.get("source")
        sources = (source,) if isinstance(source, dict) else ()
        for key in keys:
            if key in metadata and metadata[key] is not None:
                return metadata[key]
            for source_values in sources:
                if source_values.get(key) is not None:
                    return source_values[key]
        return None

    def _validate_asset(self, asset: Any, path: str) -> LexiconProvenance:
        metadata = self._metadata(asset)
        declared_language = self._metadata_value(metadata, "language", "locale")
        if self.language and declared_language and not str(declared_language).lower().startswith(self.language.lower()):
            raise LexiconResourceError(
                f"G2Lex asset {path!r} declares language {declared_language!r}, "
                f"not requested {self.language!r}"
            )
        kind = self._metadata_value(metadata, "kind")
        if kind is not None and str(kind).casefold() != "pronunciation":
            raise LexiconResourceError(
                f"G2Lex asset {path!r} has unsupported kind {kind!r}; "
                "direct lookup requires pronunciation assets"
            )
        raw_encoding = self._metadata_value(
            metadata, "phoneme_encoding", "pronunciation_alphabet", "alphabet"
        )
        try:
            source_encoding = normalize_phoneme_encoding(raw_encoding)
        except ValueError as exc:
            raise LexiconResourceError(
                f"G2Lex asset {path!r} uses unsupported phoneme encoding {raw_encoding!r}; "
                "supported encodings are IPA and espeak-ipa3"
            ) from exc
        provenance = LexiconProvenance(
            lexicon_id=str(self._metadata_value(metadata, "id", "lexicon_id") or path),
            language=str(declared_language) if declared_language is not None else None,
            kind=str(kind) if kind is not None else None,
            source_encoding=source_encoding,
            data_version=self._optional_string(
                self._metadata_value(metadata, "data_version", "version")
            ),
            producer=self._optional_string(self._metadata_value(metadata, "producer")),
            transform=self._optional_string(
                self._metadata_value(metadata, "transform_id", "transform")
            ),
            generator=self._optional_string(
                self._metadata_value(metadata, "generator", "generator_id")
            ),
            asset_path=path,
        )
        return provenance

    @staticmethod
    def _optional_string(value: object | None) -> str | None:
        return None if value is None else str(value)

    def _ensure_assets(self) -> tuple[Any, ...]:
        if self._closed:
            raise LexiconResourceError("G2Lex lookup adapter is closed")
        if self._assets is not None:
            return self._assets
        for path in self.paths:
            if not Path(path).is_file():
                raise LexiconResourceError(f"G2Lex asset does not exist: {path}")
        try:
            import g2lex
        except ImportError as exc:
            raise LexiconDependencyError(
                "Direct G2Lex support requires the optional 'g2lex' extra. "
                "Install piperg2p[g2lex]."
            ) from exc
        assets: list[Any] = []
        provenance: list[LexiconProvenance] = []
        try:
            for path in self.paths:
                asset = g2lex.open(path)
                assets.append(asset)
                provenance.append(self._validate_asset(asset, path))
        except LexiconResourceError:
            for asset in assets:
                asset.close()
            raise
        except Exception as exc:
            for asset in assets:
                asset.close()
            failed_path = path if "path" in locals() else self.paths[0] if self.paths else ""
            raise LexiconResourceError(f"Could not open G2Lex asset {failed_path!r}") from exc
        self._assets = tuple(assets)
        self._provenance = tuple(provenance)
        return self._assets

    def lookup(self, word: str, *, tag: str | None = None) -> LexiconPronunciation | None:
        assets = self._ensure_assets()
        try:
            for asset, path, provenance in zip(assets, self.paths, self._provenance):
                value = asset.lookup(word, tag=tag)
                if value is not None:
                    return LexiconPronunciation(
                        pronunciation=str(value),
                        source=f"g2lex:{path}",
                        lexicon_id=provenance.lexicon_id,
                        matched_key=word,
                        source_encoding=provenance.source_encoding,
                        provenance=provenance,
                    )
        except Exception as exc:
            if isinstance(exc, LexiconResourceError):
                raise
            raise LexiconResourceError(f"G2Lex lookup failed for {word!r}") from exc
        return None

    def lookup_many(
        self, words: Sequence[str], *, tag: str | None = None
    ) -> tuple[LexiconPronunciation | None, ...]:
        return tuple(self.lookup(word, tag=tag) for word in words)

    def close(self) -> None:
        if self._assets is not None:
            for asset in self._assets:
                asset.close()
        self._assets = None
        self._closed = True

    def __enter__(self) -> "G2LexLookup":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
