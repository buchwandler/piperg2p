from typing import TYPE_CHECKING

from .clauses import Clause, compose_clauses, merge_vowel_clusters

if TYPE_CHECKING:
    from .backend import EspeakBackend
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

_LAZY_EXPORT_MODULES = {
    "EspeakBackend": ".backend",
    "EspeakCliBackend": ".cli",
    "EspeakLibraryCandidate": ".discovery",
    "EspeakLibraryProbe": ".discovery",
    "EspeakPaths": ".discovery",
    "NativeEspeakProvider": ".native",
    "discover": ".discovery",
    "find_data": ".discovery",
    "find_executable": ".discovery",
    "find_library": ".discovery",
    "inspect_espeak": ".discovery",
    "iter_library_candidates": ".discovery",
    "probe_library_candidate": ".discovery",
    "select_exact_native": ".discovery",
}


def __getattr__(name: str) -> object:
    module_name = _LAZY_EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib import import_module

    value = getattr(import_module(module_name, __name__), name)
    globals()[name] = value
    return value
