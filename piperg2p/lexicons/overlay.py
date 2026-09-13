from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterable, Sequence

from ..backends.espeak.clauses import merge_vowel_clusters
from ..errors import LexiconResourceError
from ..raw_blocks import (
    PreparedSegment,
    Segment,
    compose_prepared_segments,
    prepare_segments,
)
from .base import PronunciationLookup
from .spans import scan_source_spans


def _tag_for_span(annotations: Sequence[object], start: int, end: int) -> str | None:
    for annotation in annotations:
        if isinstance(annotation, dict):
            annotation_start = annotation.get("start", annotation.get("char_start"))
            annotation_end = annotation.get("end", annotation.get("char_end"))
            tag = annotation.get("tag")
        else:
            annotation_start = getattr(annotation, "start", getattr(annotation, "char_start", None))
            annotation_end = getattr(annotation, "end", getattr(annotation, "char_end", None))
            tag = getattr(annotation, "tag", None)
        if (
            tag is not None
            and isinstance(annotation_start, int)
            and isinstance(annotation_end, int)
            and annotation_start <= start
            and annotation_end >= end
        ):
            return str(tag)
    return None


def _coalesce_text_segments(
    segments: Iterable[PreparedSegment],
) -> tuple[PreparedSegment, ...]:
    result: list[PreparedSegment] = []
    for segment in segments:
        if (
            result
            and segment.kind == "text"
            and result[-1].kind == "text"
            and result[-1].source_end == segment.source_start
        ):
            previous = result[-1]
            result[-1] = PreparedSegment(
                "text",
                previous.value + segment.value,
                previous.source_start,
                segment.source_end,
                "source",
            )
        else:
            result.append(segment)
    return tuple(result)


def _prepare_lexicon_pronunciation(pronunciation) -> str:
    """Prepare a lexicon hit according to its declared source encoding."""
    encoding = pronunciation.source_encoding or "ipa"
    if encoding == "espeak-ipa3":
        return pronunciation.pronunciation
    if encoding == "ipa":
        return unicodedata.normalize("NFD", pronunciation.pronunciation)
    raise LexiconResourceError(
        f"unsupported lexicon pronunciation encoding {encoding!r}"
    )


def overlay_text_segment(
    segment: PreparedSegment,
    lookup: PronunciationLookup,
    *,
    tag: str | None = None,
    fallback: bool = True,
    annotations: Sequence[object] = (),
) -> tuple[PreparedSegment, ...]:
    spans = scan_source_spans(segment.value)
    words = tuple(span.text for span in spans if span.kind == "word")
    if not words:
        return (segment,)
    if annotations:
        hits = tuple(
            lookup.lookup(
                word,
                tag=_tag_for_span(
                    annotations, segment.source_start + span.start, segment.source_start + span.end
                ),
            )
            for span, word in zip((span for span in spans if span.kind == "word"), words, strict=True)
        )
    else:
        hits = lookup.lookup_many(words, tag=tag)
    if len(hits) != len(words):
        raise LexiconResourceError("lexicon lookup returned an invalid batch length")
    hit_index = 0
    prepared: list[PreparedSegment] = []
    for span in spans:
        start = segment.source_start + span.start
        end = segment.source_start + span.end
        if span.kind == "other":
            prepared.append(PreparedSegment("text", span.text, start, end, "source"))
            continue
        pronunciation = hits[hit_index]
        hit_index += 1
        if pronunciation is None:
            if not fallback:
                raise LexiconResourceError(
                    f"lexicon miss for {span.text!r} and eSpeak fallback is disabled"
                )
            prepared.append(PreparedSegment("text", span.text, start, end, "source"))
        else:
            prepared.append(
                PreparedSegment(
                    "phonemes",
                    _prepare_lexicon_pronunciation(pronunciation),
                    start,
                    end,
                    pronunciation.source,
                )
            )
    return _coalesce_text_segments(prepared)


def prepare_lexicon_segments(
    segments: Iterable[Segment],
    lookup: PronunciationLookup,
    *,
    tag: str | None = None,
    fallback: bool = True,
    annotations: Sequence[object] = (),
 ) -> tuple[PreparedSegment, ...]:
    prepared = prepare_segments(segments)
    output: list[PreparedSegment] = []
    for segment in prepared:
        if segment.kind == "phonemes":
            output.append(segment)
        else:
            overlayed = overlay_text_segment(
                segment,
                lookup,
                tag=tag,
                fallback=fallback,
                annotations=annotations,
            )
            for item in overlayed:
                if item.kind == "text" and item.value.isspace():
                    output.append(
                        PreparedSegment(
                            "phonemes",
                            item.value,
                            item.source_start,
                            item.source_end,
                            "source-space",
                        )
                    )
                else:
                    output.append(item)
    return tuple(output)


def compose_lexicon_overlay(
    segments: Iterable[Segment],
    lookup: PronunciationLookup,
    phonemize_text: Callable[[str], list[list[str]]],
    *,
    vowel_clusters: frozenset[tuple[str, ...]] = frozenset(),
    tag: str | None = None,
    fallback: bool = True,
    annotations: Sequence[object] = (),
 ) -> list[list[str]]:
    prepared = prepare_lexicon_segments(
        segments,
        lookup,
        tag=tag,
        fallback=fallback,
        annotations=annotations,
    )
    groups = compose_prepared_segments(prepared, phonemize_text)
    return [merge_vowel_clusters(list(group), vowel_clusters) for group in groups]
