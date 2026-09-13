"""Small Piper stress override utility."""

from __future__ import annotations

import unicodedata

from .errors import PiperG2PError

_PRIMARY = "ˈ"
_SECONDARY = "ˌ"


def apply_stress(phonemes: str, level: int, *, strict: bool = False) -> str:
    """Apply a structured stress level to resolved phoneme content."""
    if level not in {-2, -1, 1, 2}:
        if strict:
            raise PiperG2PError("stress must be one of -2, -1, +1, or +2")
        return phonemes
    values = list(unicodedata.normalize("NFD", phonemes))
    if level == -2:
        return "".join(value for value in values if value not in {_PRIMARY, _SECONDARY})
    if level == -1:
        return "".join(_SECONDARY if value == _PRIMARY else value for value in values)
    has_vowel = any(
        unicodedata.category(value).startswith("L")
        and value.casefold() in "aeiouəɛɪɔʊɑɒʌɜ"
        for value in values
    )
    if not has_vowel:
        return phonemes
    values = [value for value in values if value not in {_PRIMARY, _SECONDARY}]
    return (_SECONDARY if level == 1 else _PRIMARY) + "".join(values)
