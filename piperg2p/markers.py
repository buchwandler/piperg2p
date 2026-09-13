"""Marker parsing helpers for source-aligned pronunciation overrides."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .types import OverrideSpan


def parse_delimited(
    text: str, marker: str = "@", escape: str = "\\"
) -> tuple[str, list[tuple[int, int]], list[str]]:
    """Remove paired markers and return clean-text offsets and warnings."""
    if not marker or not escape:
        raise ValueError("marker and escape must not be empty")
    output: list[str] = []
    ranges: list[tuple[int, int]] = []
    warnings: list[str] = []
    position = 0
    marked_start: int | None = None
    source_marker_start: int | None = None
    while position < len(text):
        if text.startswith(escape, position) and position + len(escape) < len(text):
            escaped = text[position + len(escape)]
            if escaped in {marker, escape}:
                output.append(escaped)
                position += len(escape) + 1
                continue
        if text.startswith(marker, position):
            if marked_start is None:
                marked_start = len(output)
                source_marker_start = position
            else:
                ranges.append((marked_start, len(output)))
                marked_start = None
                source_marker_start = None
            position += len(marker)
            continue
        output.append(text[position])
        position += 1
    if marked_start is not None:
        warnings.append(f"Unmatched opening marker at position {source_marker_start}")
        output.insert(marked_start, marker)
    return "".join(output), ranges, warnings


def apply_marker_overrides(
    clean_text: str,
    marked_ranges: Sequence[tuple[int, int]],
    assignments: Sequence[Mapping[str, str]] | Mapping[int, Mapping[str, str]],
) -> list[OverrideSpan]:
    """Apply ordinal or sequence assignments to ranges from parse_delimited."""
    if isinstance(assignments, Mapping):
        result: list[OverrideSpan] = []
        for ordinal, attrs in assignments.items():
            if not isinstance(ordinal, int) or ordinal < 1 or ordinal > len(marked_ranges):
                raise ValueError(f"assignment index {ordinal!r} is out of range")
            start, end = marked_ranges[ordinal - 1]
            result.append(OverrideSpan(start, end, attrs))
        return result
    if len(assignments) != len(marked_ranges):
        raise ValueError("assignment sequence length must match marked ranges")
    return [
        OverrideSpan(start, end, attrs)
        for (start, end), attrs in zip(marked_ranges, assignments, strict=True)
        if attrs
    ]