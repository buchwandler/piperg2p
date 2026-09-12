from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class TextSegment:
    text: str


@dataclass(frozen=True)
class RawPhonemeSegment:
    text: str


Segment = TextSegment | RawPhonemeSegment


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
            segments.append(TextSegment(text[text_start:opening]))
        end = text.find("]]", opening + 2)
        if end < 0:
            remainder = text[opening:]
            if segments and isinstance(segments[-1], TextSegment):
                segments[-1] = TextSegment(segments[-1].text + remainder)
            else:
                segments.append(TextSegment(remainder))
            return [segment for segment in segments if not isinstance(segment, TextSegment) or segment.text]
        raw = text[opening + 2 : end].strip()
        segments.append(RawPhonemeSegment(raw))
        position = end + 2
        text_start = position
    if text_start < len(text):
        segments.append(TextSegment(text[text_start:]))
    elif not segments and text:
        segments.append(TextSegment(text))
    return [segment for segment in segments if not isinstance(segment, TextSegment) or segment.text]


def compose_raw_segments(
    segments: Iterable[Segment], phonemize_text: Callable[[str], list[list[str]]]
) -> list[list[str]]:
    """Compose backend sentence groups and raw codepoints in source order."""
    output: list[list[str]] = []
    join_next = False
    for segment in segments:
        if isinstance(segment, RawPhonemeSegment):
            if not segment.text:
                join_next = True
                continue
            if output:
                output[-1].extend(segment.text)
            else:
                output.append(list(segment.text))
            join_next = True
            continue
        groups = [list(group) for group in phonemize_text(segment.text)]
        if not groups:
            continue
        if join_next and output:
            output[-1].extend(groups.pop(0))
            join_next = False
        output.extend(groups)
    return [group for group in output if group]
