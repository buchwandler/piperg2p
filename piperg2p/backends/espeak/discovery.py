from __future__ import annotations

import ctypes
import ctypes.util
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from ...diagnostics import EspeakCapabilities
from ...errors import BackendUnavailableError


@dataclass(frozen=True)
class EspeakPaths:
    executable: str | None = None
    library: str | None = None
    data: str | None = None
    source: str = "system"


@dataclass(frozen=True, slots=True)
class EspeakLibraryCandidate:
    library: str
    source: str
    data: str | None = None
    explicit: bool = False


@dataclass(frozen=True, slots=True)
class EspeakLibraryProbe:
    library: str
    source: str
    data: str | None
    loadable: bool
    exact_clause_api: bool
    error: str | None = None


@dataclass(frozen=True, slots=True)
class EspeakNativeSelection:
    candidate: EspeakLibraryCandidate | None
    probes: tuple[EspeakLibraryProbe, ...]
    explicit: bool


def _modern_loader_paths() -> tuple[str | None, str | None] | None:
    try:
        import espeakng_loader  # type: ignore[import-untyped]
    except ImportError:
        return None
    library = espeakng_loader.get_library_path()
    data = espeakng_loader.get_data_path()
    if library and Path(library).is_file():
        return str(library), str(data) if data else None
    return None


def _candidate_identity(value: str) -> str:
    path = Path(value)
    if path.is_absolute() or path.exists():
        try:
            return str(path.resolve())
        except OSError:
            return str(path)
    return value


def maybe_find_executable(explicit: str | None = None) -> str | None:
    candidate = explicit or os.environ.get("PIPERG2P_ESPEAK_EXECUTABLE")
    if candidate:
        if Path(candidate).is_file():
            return str(Path(candidate))
        found = shutil.which(candidate)
        return str(found) if found else None
    return shutil.which("espeak-ng") or shutil.which("espeak")


def find_executable(explicit: str | None = None) -> str:
    candidate = explicit or os.environ.get("PIPERG2P_ESPEAK_EXECUTABLE")
    if candidate:
        if Path(candidate).is_file() or shutil.which(candidate):
            return (
                str(Path(candidate))
                if Path(candidate).is_file()
                else str(shutil.which(candidate))
            )
        raise BackendUnavailableError(
            f"configured eSpeak executable does not exist: {candidate}"
        )
    found = shutil.which("espeak-ng") or shutil.which("espeak")
    if not found:
        raise BackendUnavailableError(
            "eSpeak was not found; install eSpeak NG or configure PIPERG2P_ESPEAK_EXECUTABLE"
        )
    return found


def find_library(
    explicit: str | None = None, executable: str | None = None
) -> str | None:
    candidate = explicit or os.environ.get("PIPERG2P_ESPEAK_LIBRARY")
    if candidate:
        if Path(candidate).is_file() or shutil.which(candidate):
            return candidate
        raise BackendUnavailableError(
            f"configured eSpeak library does not exist: {candidate}"
        )
    packaged = _modern_loader_paths()
    if packaged is not None:
        return packaged[0]
    for name in ("espeak-ng", "espeak"):
        found = ctypes.util.find_library(name)
        if found:
            return found
    if executable:
        candidates = _near_executable_candidates(executable)
        if candidates:
            return str(candidates[0])
    return None


def _near_executable_candidates(executable: str | None) -> tuple[Path, ...]:
    if not executable or "/" not in executable and "\\" not in executable:
        return ()
    path = Path(executable).resolve()
    root = path.parent.parent
    candidates = list((root / "lib").glob("libespeak*.so*")) + list(
        (root / "bin").glob("libespeak*.dll")
    )
    return tuple(candidates)


def _derived_data(executable: str | None, library: str | None) -> str | None:
    candidates: list[Path] = []
    for value in (executable, library):
        if value and ("/" in value or "\\" in value):
            path = Path(value).resolve()
            roots = [path.parent, path.parent.parent]
            candidates.extend(root / "share" / "espeak-ng-data" for root in roots)
            candidates.extend(root / "espeak-ng-data" for root in roots)
    for path in candidates:
        if path.is_dir():
            return str(path)
    return None


def find_data(
    explicit: str | None = None,
    executable: str | None = None,
    library: str | None = None,
) -> str | None:
    candidate = explicit or os.environ.get("PIPERG2P_ESPEAK_DATA")
    if candidate:
        path = Path(candidate)
        if path.is_dir():
            return str(path)
        raise BackendUnavailableError(
            f"configured eSpeak data directory does not exist: {candidate}"
        )
    packaged = _modern_loader_paths()
    if packaged is not None and packaged[1] is not None:
        return packaged[1]
    return _derived_data(executable, library)


def _candidate_data(
    candidate: EspeakLibraryCandidate,
    *,
    executable: str | None,
    data: str | None,
) -> str | None:
    if data is not None or os.environ.get("PIPERG2P_ESPEAK_DATA") is not None:
        return data or os.environ.get("PIPERG2P_ESPEAK_DATA")
    if candidate.data is not None:
        return candidate.data
    return _derived_data(executable, candidate.library)


def iter_library_candidates(
    explicit: str | None = None,
    *,
    executable: str | None = None,
    data: str | None = None,
) -> tuple[EspeakLibraryCandidate, ...]:
    configured = explicit or os.environ.get("PIPERG2P_ESPEAK_LIBRARY")
    if configured:
        candidate = EspeakLibraryCandidate(
            configured,
            "explicit",
            explicit=True,
        )
        return (
            EspeakLibraryCandidate(
                candidate.library,
                candidate.source,
                _candidate_data(candidate, executable=executable, data=data),
                candidate.explicit,
            ),
        )

    values: list[EspeakLibraryCandidate] = []
    packaged = _modern_loader_paths()
    if packaged is not None and packaged[0] is not None:
        values.append(EspeakLibraryCandidate(packaged[0], "modern-loader", packaged[1]))
    for name, source in (
        ("espeak-ng", "system-espeak-ng"),
        ("espeak", "system-espeak"),
    ):
        library = ctypes.util.find_library(name)
        if library:
            values.append(EspeakLibraryCandidate(library, source))
    executable_candidate = executable or maybe_find_executable()
    values.extend(
        EspeakLibraryCandidate(str(path), "near-executable")
        for path in _near_executable_candidates(executable_candidate)
    )
    result: list[EspeakLibraryCandidate] = []
    identities: set[str] = set()
    for candidate in values:
        identity = _candidate_identity(candidate.library)
        if identity in identities:
            continue
        identities.add(identity)
        result.append(
            EspeakLibraryCandidate(
                candidate.library,
                candidate.source,
                _candidate_data(
                    candidate,
                    executable=executable_candidate,
                    data=data,
                ),
            )
        )
    return tuple(result)


def probe_library_candidate(
    candidate: EspeakLibraryCandidate,
) -> EspeakLibraryProbe:
    try:
        library = ctypes.CDLL(candidate.library)
    except OSError as exc:
        return EspeakLibraryProbe(
            candidate.library,
            candidate.source,
            candidate.data,
            False,
            False,
            str(exc),
        )
    return EspeakLibraryProbe(
        candidate.library,
        candidate.source,
        candidate.data,
        True,
        hasattr(library, "espeak_TextToPhonemesWithTerminator"),
        None,
    )


def select_exact_native(
    *,
    library: str | None = None,
    executable: str | None = None,
    data: str | None = None,
) -> EspeakNativeSelection:
    candidates = iter_library_candidates(
        library,
        executable=executable,
        data=data,
    )
    probes: list[EspeakLibraryProbe] = []
    for candidate in candidates:
        probe = probe_library_candidate(candidate)
        probes.append(probe)
        if probe.exact_clause_api:
            return EspeakNativeSelection(candidate, tuple(probes), candidate.explicit)
    return EspeakNativeSelection(
        None,
        tuple(probes),
        bool(candidates and candidates[0].explicit),
    )


def inspect_espeak(
    *,
    executable: str | None = None,
    library: str | None = None,
    data: str | None = None,
) -> EspeakCapabilities:

    found_executable = maybe_find_executable(executable)
    selection = select_exact_native(
        library=library,
        executable=executable,
        data=data,
    )
    candidate = selection.candidate
    return EspeakCapabilities(
        executable=found_executable,
        cli_available=found_executable is not None,
        selected_exact_library=candidate.library if candidate else None,
        selected_source=candidate.source if candidate else None,
        selected_data=candidate.data if candidate else None,
        candidates=selection.probes,
    )


def discover(
    *,
    executable: str | None = None,
    library: str | None = None,
    data: str | None = None,
    require_executable: bool = True,
) -> EspeakPaths:
    configured = any(
        value is not None
        for value in (
            executable,
            library,
            data,
            os.environ.get("PIPERG2P_ESPEAK_EXECUTABLE"),
            os.environ.get("PIPERG2P_ESPEAK_LIBRARY"),
            os.environ.get("PIPERG2P_ESPEAK_DATA"),
        )
    )
    exe = find_executable(executable) if require_executable or executable else None
    lib = find_library(library, exe)
    data_path = find_data(data, exe, lib)
    packaged = _modern_loader_paths()
    if configured:
        source = "explicit"
    elif packaged is not None and lib == packaged[0]:
        source = "modern-loader"
    elif lib == ctypes.util.find_library("espeak-ng") and lib is not None:
        source = "system-espeak-ng"
    elif lib is not None:
        source = "system-espeak"
    else:
        source = "unknown"
    return EspeakPaths(exe, lib, data_path, source)
