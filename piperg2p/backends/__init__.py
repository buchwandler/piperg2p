"""Backend implementations and compatibility exports."""

from .base import PhonemeBackend
from .espeak import (
    EspeakBackend,
    EspeakCliBackend,
    EspeakLibraryCandidate,
    EspeakLibraryProbe,
    NativeEspeakProvider,
    inspect_espeak,
)
from .text import TextBackend

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
