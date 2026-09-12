from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class TextSegment:
    text: str
    source_start: int = field(default=0, compare=False)
    source_end: int | None = field(default=None, compare=False)


@dataclass(frozen=True)
class RawPhonemeSegment:
    text: str
    source_start: int = field(default=0, compare=False)
    source_end: int | None = field(default=None, compare=False)


Segment = TextSegment | RawPhonemeSegment


@dataclass(frozen=True)
class PreparedSegment:
    kind: Literal["text", "phonemes"]
    value: str
    source_start: int
    source_end: int
    provenance: str = "source"


def _text_segment(text: str, start: int, end: int) -> TextSegment:
    return TextSegment(text, start, end)


def _raw_segment(text: str, start: int, end: int) -> RawPhonemeSegment:
    return RawPhonemeSegment(text, start, end)


def parse_raw_blocks(text: str) -> list[Segment]:
    """Parse eSpeak-style raw blocks without interpreting their contents."""
    segments: list[Segment] = []
    position = 0
    text_start = 0
    while position < len(text):
        opening = text.find("[[", position)
        closing = text.find("]]", position)
        if opening < 0 and closing < 0:
            break
        if closing >= 0 and (opening < 0 or closing < opening):
            position = closing + 2
            continue
        if opening > text_start:
            segments.append(
                _text_segment(text[text_start:opening], text_start, opening)
            )
        end = text.find("]]", opening + 2)
        if end < 0:
            remainder = text[opening:]
            if segments and isinstance(segments[-1], TextSegment):
                previous = segments[-1]
                segments[-1] = _text_segment(
                    previous.text + remainder,
                    previous.source_start,
                    len(text),
                )
            else:
                segments.append(_text_segment(remainder, opening, len(text)))
            return [
                segment
                for segment in segments
                if not isinstance(segment, TextSegment) or segment.text
            ]
        raw = text[opening + 2 : end].strip()
        segments.append(_raw_segment(raw, opening, end + 2))
        position = end + 2
        text_start = position
    if text_start < len(text):
        segments.append(_text_segment(text[text_start:], text_start, len(text)))
    elif not segments and text:
        segments.append(_text_segment(text, 0, len(text)))
    return [
        segment
        for segment in segments
        if not isinstance(segment, TextSegment) or segment.text
    ]


def prepare_segments(segments: Iterable[Segment]) -> tuple[PreparedSegment, ...]:
    """Convert source and raw segments into the shared compositor representation."""
    prepared: list[PreparedSegment] = []
    for segment in segments:
        end = (
            segment.source_end
            if segment.source_end is not None
            else segment.source_start + len(segment.text)
        )
        if isinstance(segment, RawPhonemeSegment):
            prepared.append(
                PreparedSegment(
                    "phonemes", segment.text, segment.source_start, end, "raw-block"
                )
            )
        else:
            prepared.append(
                PreparedSegment(
                    "text", segment.text, segment.source_start, end, "source"
                )
            )
    return tuple(prepared)


def needs_left_boundary_space(left: str, right: str) -> bool:
    """Return whether source text explicitly places whitespace at the join."""
    return bool(left and right and (left[-1].isspace() or right[0].isspace()))


def needs_right_boundary_space(left: str, right: str) -> bool:
    """Return whether source text explicitly places whitespace at the join."""
    return needs_left_boundary_space(left, right)


def compose_prepared_segments(
    segments: Iterable[PreparedSegment],
    phonemize_text: Callable[[str], list[list[str]]],
) -> list[list[str]]:
    """Compose text and direct phoneme segments in source order."""
    output: list[list[str]] = []
    join_next = False
    for segment in segments:
        if segment.kind == "phonemes":
            if not segment.value:
                join_next = True
                continue
            if output:
                output[-1].extend(segment.value)
            else:
                output.append(list(segment.value))
            join_next = True
            continue
        groups = [list(group) for group in phonemize_text(segment.value)]
        if not groups:
            continue
        if join_next and output:
            output[-1].extend(groups.pop(0))
            join_next = False
        output.extend(groups)
    return [group for group in output if group]


def compose_raw_segments(
    segments: Iterable[Segment], phonemize_text: Callable[[str], list[list[str]]]
) -> list[list[str]]:
    """Compose backend sentence groups and raw codepoints in source order."""
    return compose_prepared_segments(prepare_segments(segments), phonemize_text)
