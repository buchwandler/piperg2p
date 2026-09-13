"""Conservative, evidence-only language routing."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .types import LanguageRoute, LanguageRoutingConfig


def normalize_language(language: str) -> str:
    return language.strip().casefold().replace("_", "-")


def coerce_routing(value: LanguageRoutingConfig | Mapping[str, Any] | None) -> LanguageRoutingConfig | None:
    if value is None or isinstance(value, LanguageRoutingConfig):
        return value
    return LanguageRoutingConfig(
        mode=str(value.get("mode", "explicit")),
        languages=tuple(value.get("languages", ())),
        lexicons=value.get("lexicons", {}),
    )


def _has_evidence(source: Any, word: str) -> bool:
    if source is None:
        return False
    if isinstance(source, Mapping):
        return word in source or word.casefold() in source
    lookup = getattr(source, "lookup", None)
    if lookup is not None:
        return lookup(word) is not None
    if callable(source):
        return bool(source(word))
    return False


def route_language(
    word: str,
    default_language: str,
    routing: LanguageRoutingConfig,
    *,
    evidence: Callable[[str, str], bool] | None = None,
) -> LanguageRoute:
    """Choose a language only when exactly one configured candidate has evidence."""
    default = normalize_language(default_language)
    candidates = tuple(normalize_language(value) for value in routing.languages)
    matches = [
        language
        for language in candidates
        if language != default
        and (
            evidence(word, language)
            if evidence is not None
            else _has_evidence(routing.lexicons.get(language), word)
        )
    ]
    if len(matches) == 1:
        return LanguageRoute(0, len(word), matches[0], default, "lexicon-evidence", (word,))
    reason = "default-language" if not matches else "ambiguous-lexicon-evidence"
    return LanguageRoute(0, len(word), default, default, reason, tuple(matches))