from .backend import EspeakBackend
from .clauses import Clause, compose_clauses, merge_vowel_clusters
from .cli import EspeakCliBackend
from .discovery import EspeakPaths, discover, find_data, find_executable, find_library
from .native import NativeEspeakProvider

__all__ = [
    "Clause",
    "EspeakBackend",
    "EspeakCliBackend",
    "EspeakPaths",
    "NativeEspeakProvider",
    "compose_clauses",
    "discover",
    "find_data",
    "find_executable",
    "find_library",
    "merge_vowel_clusters",
]
