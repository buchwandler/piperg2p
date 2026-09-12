from __future__ import annotations

import ctypes.util
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from ...errors import BackendUnavailableError


@dataclass(frozen=True)
class EspeakPaths:
    executable: str | None = None
    library: str | None = None
    data: str | None = None


def find_executable(explicit: str | None = None) -> str:
    candidate = explicit or os.environ.get("PIPERG2P_ESPEAK_EXECUTABLE")
    if candidate:
        if Path(candidate).is_file() or shutil.which(candidate):
            return str(Path(candidate)) if Path(candidate).is_file() else str(shutil.which(candidate))
        raise BackendUnavailableError(f"configured eSpeak executable does not exist: {candidate}")
    found = shutil.which("espeak-ng") or shutil.which("espeak")
    if not found:
        raise BackendUnavailableError("eSpeak was not found; install eSpeak NG or configure PIPERG2P_ESPEAK_EXECUTABLE")
    return found


def find_library(explicit: str | None = None, executable: str | None = None) -> str | None:
    candidate = explicit or os.environ.get("PIPERG2P_ESPEAK_LIBRARY")
    if candidate:
        if Path(candidate).is_file() or shutil.which(candidate):
            return candidate
        raise BackendUnavailableError(f"configured eSpeak library does not exist: {candidate}")
    for name in ("espeak-ng", "espeak"):
        found = ctypes.util.find_library(name)
        if found:
            return found
    if executable:
        root = Path(executable).resolve().parent.parent
        candidates = list((root / "lib").glob("libespeak*.so*")) + list((root / "bin").glob("libespeak*.dll"))
        if candidates:
            return str(candidates[0])
    return None


def find_data(explicit: str | None = None, executable: str | None = None, library: str | None = None) -> str | None:
    candidate = explicit or os.environ.get("PIPERG2P_ESPEAK_DATA")
    if candidate:
        path = Path(candidate)
        if path.is_dir():
            return str(path)
        raise BackendUnavailableError(f"configured eSpeak data directory does not exist: {candidate}")
    candidates: list[Path] = []
    for value in (executable, library):
        if value and "/" in value:
            path = Path(value).resolve()
            roots = [path.parent, path.parent.parent]
            candidates.extend(root / "share" / "espeak-ng-data" for root in roots)
            candidates.extend(root / "espeak-ng-data" for root in roots)
    for path in candidates:
        if path.is_dir():
            return str(path)
    return None


def discover(
    *,
    executable: str | None = None,
    library: str | None = None,
    data: str | None = None,
    require_executable: bool = True,
) -> EspeakPaths:
    exe = find_executable(executable) if require_executable or executable else None
    lib = find_library(library, exe)
    data_path = find_data(data, exe, lib)
    return EspeakPaths(exe, lib, data_path)
