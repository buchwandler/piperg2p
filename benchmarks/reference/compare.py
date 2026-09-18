from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .phonodist import compare_phonetically
from .types import CaseComparison


def first_difference(left: str, right: str) -> int | None:
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    return min(len(left), len(right)) if left != right else None


def compare_case(
    case_id: str,
    reference: str,
    candidate: str,
    *,
    policy: str = "piper-ipa3",
    use_phonodist: bool = False,
) -> CaseComparison:
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

    phonodist_result = {}
    if use_phonodist:
        phonodist_result = compare_phonetically(reference, candidate)

    return CaseComparison(
        case_id,
        difference is None,
        reference,
        expected,
        actual,
        difference,
        candidate_raw=candidate,
        **phonodist_result,
    )


def metrics(
    comparisons: list[CaseComparison],
    *,
    ids: list[tuple[list[int], list[int]]] | None = None,
    reference_errors: int = 0,
    candidate_errors: int = 0,
    missing_symbol_cases: int = 0,
) -> dict[str, Any]:
    passed = sum(item.passed for item in comparisons)
    substitutions = insertions = deletions = 0
    for item in comparisons:
        width = min(len(item.reference_symbols), len(item.candidate_symbols))
        substitutions += sum(
            a != b
            for a, b in zip(
                item.reference_symbols[:width], item.candidate_symbols[:width]
            )
        )
        insertions += max(0, len(item.candidate_symbols) - len(item.reference_symbols))
        deletions += max(0, len(item.reference_symbols) - len(item.candidate_symbols))
    total = sum(len(item.reference_symbols) for item in comparisons)

    # Phonodist classification counts
    phonetic_classifications: dict[str, int] = {}
    stress_only_mismatches = 0
    segmental_mismatches = 0
    notation_only_policy_passes = 0
    for item in comparisons:
        if item.phonetic_classification:
            phonetic_classifications[item.phonetic_classification] = (
                phonetic_classifications.get(item.phonetic_classification, 0) + 1
            )
            if not item.passed and item.phonetic_classification == "stress_only":
                stress_only_mismatches += 1
            elif not item.passed and item.phonetic_classification == "segmental":
                segmental_mismatches += 1
            elif item.passed and item.phonetic_classification == "notation_only":
                notation_only_policy_passes += 1

    return {
        "cases_total": len(comparisons),
        "cases_passed": passed,
        "cases_failed": len(comparisons) - passed,
        "exact_match_rate": passed / len(comparisons) if comparisons else 1.0,
        "reference_errors": reference_errors,
        "candidate_errors": candidate_errors,
        "symbol_substitutions": substitutions,
        "symbol_insertions": insertions,
        "symbol_deletions": deletions,
        "symbol_edit_distance": substitutions + insertions + deletions,
        "symbol_error_rate": (substitutions + insertions + deletions) / total
        if total
        else 0.0,
        "id_exact_matches": sum(left == right for left, right in ids or []),
        "id_mismatches": sum(left != right for left, right in ids or []),
        "missing_symbol_cases": missing_symbol_cases,
        "phonetic_classifications": phonetic_classifications,
        "stress_only_mismatches": stress_only_mismatches,
        "segmental_mismatches": segmental_mismatches,
        "notation_only_policy_passes": notation_only_policy_passes,
    }


def comparison_dict(value: CaseComparison) -> dict[str, Any]:
    return asdict(value)
