"""Optional Phonodist adapter for structural IPA comparison."""

from __future__ import annotations

from typing import Any


def compare_phonetically(
    reference: str,
    candidate: str,
) -> dict[str, Any]:
    """Compare two IPA strings using Phonodist for structural classification.

    Returns a dict with classification, segment relation/distance, and stress equality.
    If Phonodist is not installed or cannot parse the input, returns a dict with
    phonodist_error set.
    """
    try:
        from phonodist import PhonodistError, compare_pronunciations
    except ImportError:
        return {
            "phonetic_classification": None,
            "segment_relation": None,
            "segment_distance": None,
            "stress_equal": None,
            "phonodist_error": "phonodist not installed",
        }

    try:
        result = compare_pronunciations(reference, candidate)
        return {
            "phonetic_classification": result.classification,
            "segment_relation": result.segment_relation,
            "segment_distance": result.segmental.distance if result.segmental else None,
            "stress_equal": result.stress_equal,
            "phonodist_error": None,
        }
    except PhonodistError as exc:
        return {
            "phonetic_classification": None,
            "segment_relation": None,
            "segment_distance": None,
            "stress_equal": None,
            "phonodist_error": str(exc),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "phonetic_classification": None,
            "segment_relation": None,
            "segment_distance": None,
            "stress_equal": None,
            "phonodist_error": f"unexpected error: {exc}",
        }
