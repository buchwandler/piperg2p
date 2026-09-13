"""Source-span override pipeline for the Piper facade."""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from typing import Any

from .language_routing import coerce_routing, route_language
from .stress import apply_stress
from .types import (
    LanguageRoute,
    LanguageRoutingConfig,
    OverrideSpan,
    OverrideSpanLike,
    PhonemeSentence,
    PhonemizeResult,
    TokenAnnotation,
    TokenAnnotationLike,
    TokenSpan,
)


def _as_override(value: OverrideSpanLike) -> OverrideSpan:
    if isinstance(value, OverrideSpan):
        return value
    if isinstance(value, Mapping):
        start = value.get("char_start", value.get("start"))
        end = value.get("char_end", value.get("end"))
        attrs = value.get("attrs", {})
        if start is None or end is None:
            raise ValueError("override mapping requires start and end")
        if not attrs:
            attrs = {key: item for key, item in value.items() if key not in {"start", "end", "char_start", "char_end"}}
        return OverrideSpan(int(start), int(end), attrs)
    if isinstance(value, Sequence) and len(value) == 3:
        return OverrideSpan(int(value[0]), int(value[1]), value[2])
    raise TypeError("override must be OverrideSpan, mapping, or (start, end, attrs)")


def _as_annotation(value: TokenAnnotationLike) -> TokenAnnotation:
    if isinstance(value, TokenAnnotation):
        return value
    if isinstance(value, Mapping):
        return TokenAnnotation(
            int(value.get("start", value.get("char_start"))),
            int(value.get("end", value.get("char_end"))),
            value.get("text"),
            value.get("pos"),
            value.get("tag"),
            value.get("lemma"),
            value.get("language"),
        )
    raise TypeError("annotation must be TokenAnnotation or mapping")


def _snap_overrides(
    text: str,
    values: Sequence[OverrideSpanLike],
    overlap: str,
) -> tuple[list[OverrideSpan], list[str]]:
    tokens = _tokenize(text)
    boundaries = {0, len(text)} | {token.char_start for token in tokens} | {
        token.char_end for token in tokens
    }
    result: list[OverrideSpan] = []
    warnings: list[str] = []
    for raw in values:
        value = _as_override(raw)
        start, end = value.char_start, value.char_end
        if end > len(text):
            raise ValueError(f"override span ({start}, {end}) is outside source text")
        snapped_start, snapped_end = start, end
        if overlap == "snap":
            for token in tokens:
                if token.char_start < start < token.char_end:
                    snapped_start = token.char_start
                if token.char_start < end < token.char_end:
                    snapped_end = token.char_end
            if (snapped_start, snapped_end) != (start, end):
                warnings.append(
                    f"override span ({start}, {end}) snapped to ({snapped_start}, {snapped_end})"
                )
        elif overlap == "strict" and (start not in boundaries or end not in boundaries):
            warnings.append(f"override span ({start}, {end}) partially overlaps a token; skipped")
            continue
        elif overlap not in {"split", "strict", "snap"}:
            raise ValueError("overlap must be 'snap', 'strict', or 'split'")
        result.append(OverrideSpan(snapped_start, snapped_end, value.attrs))
    result.sort(key=lambda item: (item.char_start, item.char_end))
    accepted: list[OverrideSpan] = []
    for value in result:
        if accepted and value.char_start < accepted[-1].char_end:
            warnings.append(
                f"overlapping override spans ({value.char_start}, {value.char_end}) and "
                f"({accepted[-1].char_start}, {accepted[-1].char_end})"
            )
            if overlap == "strict":
                continue
            raise ValueError("overlapping override spans are not supported")
        accepted.append(value)
    return accepted, warnings


def _tokenize(text: str) -> list[TokenSpan]:
    from .api import tokenize

    return tokenize(text)


def _symbols(value: str, id_map: Mapping[str, Sequence[int]]) -> list[str]:
    value = unicodedata.normalize("NFD", value)
    keys = sorted((key for key in id_map if key not in {"^", "_", "$"}), key=len, reverse=True)
    output: list[str] = []
    position = 0
    while position < len(value):
        match = next((key for key in keys if value.startswith(key, position)), None)
        if match is None:
            output.append(value[position])
            position += 1
        else:
            output.append(match)
            position += len(match)
    return output


def _phonemize_text(g2p: Any, text: str, language: str) -> list[list[str]]:
    if not text:
        return []
    return g2p.frontend.backend.phonemize(text, voice=language)


def _update_token_metadata(
    tokens: list[TokenSpan],
    annotations: Sequence[TokenAnnotation],
    overrides: Sequence[OverrideSpan],
) -> None:
    for annotation in annotations:
        for token in tokens:
            if token.char_start >= annotation.start and token.char_end <= annotation.end:
                if annotation.pos is not None:
                    token.meta["pos"] = annotation.pos
                if annotation.tag is not None:
                    token.meta["tag"] = annotation.tag
                if annotation.lemma is not None:
                    token.meta["lemma"] = annotation.lemma
                if annotation.language is not None:
                    token.lang = annotation.language
    for override in overrides:
        for token in tokens:
            if token.char_start >= override.char_start and token.char_end <= override.char_end:
                token.meta["override"] = dict(override.attrs)
                if "lang" in override.attrs:
                    token.lang = str(override.attrs["lang"])


def apply_overrides(
    g2p: Any,
    base: PhonemizeResult,
    text: str,
    *,
    overrides: Sequence[OverrideSpanLike],
    annotations: Sequence[TokenAnnotationLike],
    overlap: str,
    strict_stress: bool,
    language_routing: LanguageRoutingConfig | Mapping[str, Any] | None,
) -> PhonemizeResult:
    normalized_annotations = [_as_annotation(value) for value in annotations]
    for annotation in normalized_annotations:
        if annotation.start < 0 or annotation.end > len(text) or annotation.end < annotation.start:
            raise ValueError("annotation offsets must be within source text")
        if annotation.text is not None and annotation.text != text[annotation.start : annotation.end]:
            raise ValueError("annotation text does not match its source span")
    normalized, warning_messages = _snap_overrides(text, overrides, overlap)
    routes: list[LanguageRoute] = []
    routing = coerce_routing(language_routing)
    if routing is not None and routing.mode == "auto":
        for token in _tokenize(text):
            if not token.text or not token.text[0].isalnum():
                continue
            route = route_language(token.text, g2p.language, routing)
            routes.append(
                LanguageRoute(
                    token.char_start,
                    token.char_end,
                    route.language,
                    route.requested_language,
                    route.reason,
                    route.evidence,
                )
            )
            if route.language != g2p.language:
                normalized.append(OverrideSpan(token.char_start, token.char_end, {"lang": route.language}))
        normalized.sort(key=lambda item: (item.char_start, item.char_end))
    tokens = _tokenize(text)
    _update_token_metadata(tokens, normalized_annotations, normalized)
    if not normalized and routing is None:
        base.clean_text = text
        base.extended_text = text
        base.tokens = tokens
        return base

    groups: list[list[str]] = []
    cursor = 0
    for override in normalized:
        if cursor < override.char_start:
            groups.extend(_phonemize_text(g2p, text[cursor : override.char_start], g2p.frontend.config.espeak_voice))
        attrs = override.attrs
        if "ph" in attrs:
            resolved = str(attrs["ph"])
            symbols = _symbols(resolved, g2p.config.phoneme_id_map)
            if "stress" in attrs and any(char.isspace() for char in resolved):
                warning_messages.append(
                    f"structured stress skipped for multi-word phoneme override ({override.char_start}, {override.char_end})"
                )
            elif "stress" in attrs:
                level = attrs["stress"]
                stressed = apply_stress(resolved, level, strict=strict_stress)
                symbols = _symbols(stressed, g2p.config.phoneme_id_map)
            groups.append(symbols)
        else:
            language = str(attrs.get("lang", g2p.frontend.config.espeak_voice))
            segment_groups = _phonemize_text(g2p, text[override.char_start : override.char_end], language)
            if "stress" in attrs:
                segment_groups = [
                    _symbols(apply_stress("".join(group), attrs["stress"], strict=strict_stress), g2p.config.phoneme_id_map)
                    for group in segment_groups
                ]
            groups.extend(segment_groups)
        cursor = override.char_end
    if cursor < len(text):
        groups.extend(_phonemize_text(g2p, text[cursor:], g2p.frontend.config.espeak_voice))

    sentences: list[PhonemeSentence] = []
    missing: list[str] = []
    warnings = list(base.warnings) + warning_messages
    for group in groups:
        encoded = g2p.frontend.encode(group)
        sentences.append(
            PhonemeSentence(tuple(group), encoded.ids, encoded.missing_phonemes, encoded.warnings)
        )
        missing.extend(encoded.missing_phonemes)
        warnings.extend(encoded.warnings)
    ids = [identifier for sentence in sentences for identifier in sentence.ids]
    phoneme_string = "".join(sentence.phoneme_string for sentence in sentences)
    return PhonemizeResult(
        clean_text=text,
        tokens=tokens,
        extended_text=text,
        phonemes=phoneme_string,
        token_ids=ids,
        warnings=warnings,
        language_routes=routes,
        sentences=tuple(sentences),
        diagnostics=base.diagnostics,
        missing_phonemes=tuple(missing),
    )