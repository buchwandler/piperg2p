from .backend import EspeakBackend
from .clauses import Clause, compose_clauses, merge_vowel_clusters
from .cli import EspeakCliBackend
from .discovery import (
    EspeakLibraryCandidate,
    EspeakLibraryProbe,
    EspeakPaths,
    discover,
    find_data,
    find_executable,
    find_library,
    inspect_espeak,
    iter_library_candidates,
    probe_library_candidate,
    select_exact_native,
)
from .native import NativeEspeakProvider

__all__ = [
    "Clause",
    "EspeakBackend",
    "EspeakCliBackend",
    "EspeakLibraryCandidate",
    "EspeakLibraryProbe",
    "EspeakPaths",
    "NativeEspeakProvider",
    "compose_clauses",
    "discover",
    "find_data",
    "find_executable",
    "find_library",
    "inspect_espeak",
    "iter_library_candidates",
    "merge_vowel_clusters",
    "probe_library_candidate",
    "select_exact_native",
]
