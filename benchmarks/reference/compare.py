from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .types import CaseComparison


def first_difference(left: str, right: str) -> int | None:
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    return min(len(left), len(right)) if left != right else None


def compare_case(case_id: str, reference: str, candidate: str, *, policy: str = "piper-ipa3") -> CaseComparison:
    if policy == "raw-exact":
        expected, actual = reference, candidate
    else:
        import unicodedata

        expected = unicodedata.normalize("NFD", reference)
        actual = unicodedata.normalize("NFD", candidate)
        if policy in {"piper-ipa3", "model-symbol", "model-id"}:
            expected = expected.replace("\u200d", "")
            actual = actual.replace("\u200d", "")
    difference = first_difference(expected, actual)
    return CaseComparison(case_id, difference is None, reference, expected, actual, difference)


def metrics(comparisons: list[CaseComparison], *, ids: list[tuple[list[int], list[int]]] | None = None) -> dict[str, Any]:
    passed = sum(item.passed for item in comparisons)
    substitutions = insertions = deletions = 0
    for item in comparisons:
        width = min(len(item.reference_symbols), len(item.candidate_symbols))
        substitutions += sum(a != b for a, b in zip(item.reference_symbols[:width], item.candidate_symbols[:width]))
        insertions += max(0, len(item.candidate_symbols) - len(item.reference_symbols))
        deletions += max(0, len(item.reference_symbols) - len(item.candidate_symbols))
    total = sum(len(item.reference_symbols) for item in comparisons)
    return {
        "cases_total": len(comparisons),
        "cases_passed": passed,
        "cases_failed": len(comparisons) - passed,
        "exact_match_rate": passed / len(comparisons) if comparisons else 1.0,
        "reference_errors": 0,
        "candidate_errors": 0,
        "symbol_substitutions": substitutions,
        "symbol_insertions": insertions,
        "symbol_deletions": deletions,
        "symbol_edit_distance": substitutions + insertions + deletions,
        "symbol_error_rate": (substitutions + insertions + deletions) / total if total else 0.0,
        "id_exact_matches": sum(left == right for left, right in ids or []),
        "id_mismatches": sum(left != right for left, right in ids or []),
        "missing_symbol_cases": 0,
    }


def comparison_dict(value: CaseComparison) -> dict[str, Any]:
    return asdict(value)
