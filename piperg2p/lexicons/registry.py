"""Local Lexphon pronunciation asset discovery and evidence helpers."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from ..language_routing import normalize_language
from ..types import LexiconEvidence


def _store(store: Any = None) -> Any:
    if store is not None:
        return store
    try:
        import lexphon  # type: ignore[import-not-found]
    except ImportError as exc:
        from ..errors import LexiconDependencyError

        raise LexiconDependencyError(
            "Lexicon discovery requires the optional 'lexphon' extra. Install piperg2p[lexphon]."
        ) from exc
    return lexphon.DataStore()


def _metadata_items(store: Any) -> list[dict[str, Any]]:
    installed = getattr(store, "installed", None)
    if installed is None:
        return []
    values = installed()
    return [dict(value) for value in values if isinstance(value, Mapping)]


def _is_pronunciation(item: Mapping[str, Any]) -> bool:
    return str(item.get("kind", "pronunciation")).casefold() == "pronunciation"


def _language_matches(item: Mapping[str, Any], language: str) -> bool:
    declared = item.get("language", item.get("locale"))
    return declared is None or normalize_language(str(declared)).startswith(
        normalize_language(language)
    )


def _public_name(item: Mapping[str, Any]) -> str:
    identifier = str(item.get("id", item.get("lexicon_id", "")))
    return identifier.rsplit(":", 1)[-1]


def available_lexicons(language: str, *, store: Any = None) -> tuple[str, ...]:
    """Return installed pronunciation asset short names in stable order."""
    values = [
        _public_name(item)
        for item in _metadata_items(_store(store))
        if _is_pronunciation(item) and _language_matches(item, language)
    ]
    return tuple(sorted(set(values)))


def lexicon_info(language: str, name: str, *, store: Any = None) -> Mapping[str, Any]:
    """Return read-only metadata for an installed pronunciation asset."""
    data_store = _store(store)
    requested = str(name)
    candidates = [
        item
        for item in _metadata_items(data_store)
        if _is_pronunciation(item)
        and _language_matches(item, language)
        and (str(item.get("id", "")) == requested or _public_name(item) == requested)
    ]
    if not candidates:
        raise KeyError(f"lexicon {name!r} is not installed for {language!r}")
    item = candidates[0]
    identifier = str(item.get("id", item.get("lexicon_id", requested)))
    result = {
        "id": identifier,
        "language": item.get("language", item.get("locale", language)),
        "kind": item.get("kind", "pronunciation"),
        "phoneme_encoding": item.get(
            "phoneme_encoding", item.get("pronunciation_alphabet", "ipa")
        ),
        "data_version": item.get("data_version", item.get("version")),
        "release_tag": item.get("release_tag"),
        "asset_path": str(data_store.path(identifier))
        if hasattr(data_store, "path")
        else item.get("asset_path"),
    }
    return MappingProxyType(result)


def evidence_for_lookup(
    frontend: Any, word: str, *, tag: str | None = None
) -> LexiconEvidence | None:
    lookup = getattr(frontend, "_lexicon_backend", None)
    if lookup is None and getattr(frontend, "_lexicon_enabled", False):
        lookup = frontend._ensure_lexicon_backend()
    if lookup is None:
        return None
    pronunciation = lookup.lookup(word, tag=tag)
    if pronunciation is None:
        return None
    provenance = pronunciation.provenance
    return LexiconEvidence(
        lexicon_id=pronunciation.lexicon_id
        or (provenance.lexicon_id if provenance else None),
        lexicon_name=(pronunciation.lexicon_id or pronunciation.source),
        matched_key=pronunciation.matched_key or word,
        source_encoding=pronunciation.source_encoding,
        pronunciation=pronunciation.pronunciation,
        provenance=provenance,
    )
