"""Backend implementations and compatibility exports."""

from typing import TYPE_CHECKING

from .base import PhonemeBackend
from .text import TextBackend

if TYPE_CHECKING:
    from .espeak import (
        EspeakBackend,
        EspeakCliBackend,
        EspeakLibraryCandidate,
        EspeakLibraryProbe,
        NativeEspeakProvider,
        inspect_espeak,
    )

__all__ = [
    "EspeakBackend",
    "EspeakCliBackend",
    "EspeakLibraryCandidate",
    "EspeakLibraryProbe",
    "NativeEspeakProvider",
    "PhonemeBackend",
    "TextBackend",
    "inspect_espeak",
]

_ESPEAK_EXPORTS = frozenset(__all__) - {"PhonemeBackend", "TextBackend"}


def __getattr__(name: str) -> object:
    if name in _ESPEAK_EXPORTS:
        from . import espeak

        value = getattr(espeak, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
