from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ..errors import LexiconDependencyError, LexiconResourceError
from .base import LexiconDiagnostics, LexiconPronunciation


class G2LexLookup:
    """Lazy exact-key lookup over explicitly supplied G2Lex assets."""

    def __init__(self, paths: Sequence[str | Path], *, language: str | None = None) -> None:
        self.paths = tuple(str(path) for path in paths)
        self.language = language
        self._assets: tuple[Any, ...] | None = None
        self._closed = False

    @property
    def diagnostics(self) -> LexiconDiagnostics:
        return LexiconDiagnostics(
            enabled=True,
            implementation="g2lex",
            language=self.language,
            identifiers=self.paths,
            compatibility="override",
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

    def _validate_asset(self, asset: Any, path: str) -> None:
        metadata = self._metadata(asset)
        declared_language = metadata.get("language") or metadata.get("locale")
        if self.language and declared_language and not str(declared_language).lower().startswith(self.language.lower()):
            raise LexiconResourceError(
                f"G2Lex asset {path!r} declares language {declared_language!r}, "
                f"not requested {self.language!r}"
            )
        alphabet = metadata.get("pronunciation_alphabet") or metadata.get("alphabet")
        if alphabet and str(alphabet).lower().replace("_", "-") not in {"ipa", "unicode-ipa", "ipa-unicode"}:
            raise LexiconResourceError(
                f"G2Lex asset {path!r} uses unsupported pronunciation alphabet {alphabet!r}; "
                "direct lookup supports IPA/Unicode IPA assets"
            )

    def _ensure_assets(self) -> tuple[Any, ...]:
        if self._closed:
            raise LexiconResourceError("G2Lex lookup adapter is closed")
        if self._assets is not None:
            return self._assets
        try:
            import g2lex
        except ImportError as exc:
            raise LexiconDependencyError(
                "Direct G2Lex support requires the optional 'g2lex' extra. Install piperg2p[g2lex]."
            ) from exc
        assets: list[Any] = []
        try:
            for path in self.paths:
                if not Path(path).is_file():
                    raise LexiconResourceError(f"G2Lex asset does not exist: {path}")
                asset = g2lex.open(path)
                self._validate_asset(asset, path)
                assets.append(asset)
        except LexiconResourceError:
            for asset in assets:
                asset.close()
            raise
        except Exception as exc:
            for asset in assets:
                asset.close()
            raise LexiconResourceError(f"Could not open G2Lex asset {path!r}") from exc
        self._assets = tuple(assets)
        return self._assets

    def lookup(self, word: str, *, tag: str | None = None) -> LexiconPronunciation | None:
        assets = self._ensure_assets()
        try:
            for asset, path in zip(assets, self.paths):
                value = asset.lookup(word, tag=tag)
                if value is not None:
                    pronunciation = str(value)
                    return LexiconPronunciation(
                        pronunciation=pronunciation,
                        source=f"g2lex:{path}",
                        lexicon_id=path,
                        matched_key=word,
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
