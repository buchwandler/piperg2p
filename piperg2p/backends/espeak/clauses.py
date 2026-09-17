from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from espeakng_runtime import Clause as RuntimeClause

_LANG_SWITCH_RE = re.compile(r"\([^)]+\)")


@dataclass(frozen=True)
class Clause:
    phonemes: str
    terminator: str | None = None
    sentence_end: bool = False


def from_runtime_clause(value: RuntimeClause) -> Clause:
    return Clause(
        phonemes=value.phonemes,
        terminator=value.terminator,
        sentence_end=value.sentence_end,
    )


def merge_vowel_clusters(
    phones: list[str], clusters: frozenset[tuple[str, ...]]
) -> list[str]:
    if not clusters:
        return phones
    max_length = max((len(cluster) for cluster in clusters), default=0)
    result: list[str] = []
    position = 0
    while position < len(phones):
        match: tuple[str, ...] | None = None
        for size in range(min(max_length, len(phones) - position), 1, -1):
            candidate = tuple(phones[position : position + size])
            if candidate in clusters:
                match = candidate
                break
        if match is None:
            result.append(phones[position])
            position += 1
        else:
            result.append("".join(match))
            position += len(match)
    return result


def _clean(phonemes: str) -> str:
    return _LANG_SWITCH_RE.sub("", phonemes).replace("\u200d", "")


def compose_clauses(
    clauses: Iterable[Clause], clusters: frozenset[tuple[str, ...]] = frozenset()
) -> list[list[str]]:
    sentences: list[list[str]] = []
    current: list[str] = []
    for clause in clauses:
        payload = unicodedata.normalize("NFD", _clean(clause.phonemes))
        if payload:
            current.extend(payload)
        if clause.terminator:
            current.append(clause.terminator)
            if clause.terminator in ",:;":
                current.append(" ")
        if clause.sentence_end and current:
            sentences.append(merge_vowel_clusters(current, clusters))
            current = []
    if current:
        sentences.append(merge_vowel_clusters(current, clusters))
    return sentences


def split_cli_clauses(text: str) -> list[tuple[str, str | None, bool]]:
    """Split CLI input into an explicitly best-effort clause stream."""
    clauses: list[tuple[str, str | None, bool]] = []
    position = 0
    for match in re.finditer(r"(.*?)([.!?]|[,;:]|$)", text, re.DOTALL):
        if match.start() != position:
            continue
        body, terminator = match.groups()
        if not body and not terminator:
            break
        clauses.append((body, terminator, bool(terminator and terminator in ".!?")))
        position = match.end()
        if position >= len(text):
            break
    return clauses


def best_effort_clauses(
    runtime: object,
    text: str,
    *,
    voice: str,
) -> list[Clause]:
    """Batch CLI clause phonemization through runtime.phonemize_many()."""
    parts = split_cli_clauses(text)
    if not parts:
        return []
    values: list[str] = runtime.phonemize_many(
        [body for body, _, _ in parts],
        voice=voice,
    )
    return [
        Clause(
            phonemes=value,
            terminator=terminator,
            sentence_end=sentence_end,
        )
        for value, (_, terminator, sentence_end) in zip(values, parts, strict=True)
    ]
