from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReferenceOutput:
    text: str
    raw: str
    canonical: str
    voice: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class CaseComparison:
    case_id: str
    passed: bool
    reference_raw: str
    reference_symbols: str
    candidate_symbols: str
    first_difference: int | None = None
    error: str | None = None
