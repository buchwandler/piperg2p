from __future__ import annotations

import ctypes
import ctypes.util
import threading
from pathlib import Path

from ...diagnostics import BackendDiagnostics
from ...errors import BackendUnavailableError, PhonemizationError
from .clauses import Clause

# Values from the public eSpeak NG speech.h API.
AUDIO_OUTPUT_SYNCHRONOUS = 2
CHARS_UTF8 = 1
IPA_OUTPUT = 2
_TERMINATORS = {
    0x41000: (",", False),
    0x42000: (":", False),
    0x43000: (";", False),
    0x48000: (".", True),
    0x82000: ("?", True),
    0x83000: ("!", True),
}


class _NativeManager:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.library: ctypes.CDLL | None = None
        self.path: str | None = None
        self.data_path: str | None = None
        self.version: str | None = None
        self.users = 0

    def acquire(self, library_path: str | None, data_path: str | None) -> ctypes.CDLL:
        with self.lock:
            if library_path is None:
                library_path = ctypes.util.find_library("espeak-ng") or ctypes.util.find_library("espeak")
            if library_path is None:
                raise BackendUnavailableError("eSpeak shared library was not found; configure PIPERG2P_ESPEAK_LIBRARY")
            if self.library is not None and self.path != library_path:
                raise BackendUnavailableError("a different eSpeak library is already active in this process")
            if self.library is None:
                try:
                    self.library = ctypes.CDLL(library_path)
                except OSError as exc:
                    raise BackendUnavailableError(f"could not load eSpeak library {library_path!r}: {exc}") from exc
                self.path = library_path
                self._configure_functions(self.library)
                init_path = None
                if data_path:
                    path = Path(data_path)
                    init_path = str(path.parent if path.name == "espeak-ng-data" else path)
                result = self.library.espeak_Initialize(
                    AUDIO_OUTPUT_SYNCHRONOUS,
                    0,
                    init_path.encode() if init_path else None,
                    0,
                )
                if result < 0:
                    self.library = None
                    self.path = None
                    raise BackendUnavailableError(f"eSpeak initialization failed with code {result}")
                if hasattr(self.library, "espeak_Info"):
                    reported = ctypes.c_char_p()
                    self.library.espeak_Info.argtypes = [ctypes.POINTER(ctypes.c_char_p)]
                    self.library.espeak_Info.restype = ctypes.c_char_p
                    version = self.library.espeak_Info(ctypes.byref(reported))
                    self.data_path = reported.value.decode() if reported.value else data_path
                    self.version = version.decode() if version else None
                else:
                    self.data_path = data_path
            self.users += 1
            return self.library

    @staticmethod
    def _configure_functions(library: ctypes.CDLL) -> None:
        library.espeak_Initialize.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        library.espeak_Initialize.restype = ctypes.c_int
        library.espeak_SetVoiceByName.argtypes = [ctypes.c_char_p]
        library.espeak_SetVoiceByName.restype = ctypes.c_int
        library.espeak_Terminate.argtypes = []
        library.espeak_Terminate.restype = ctypes.c_int
        library.espeak_TextToPhonemes.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_int, ctypes.c_int]
        library.espeak_TextToPhonemes.restype = ctypes.c_char_p
        if hasattr(library, "espeak_TextToPhonemesWithTerminator"):
            function = library.espeak_TextToPhonemesWithTerminator
            function.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
            function.restype = ctypes.c_char_p

    def release(self) -> None:
        with self.lock:
            self.users = max(0, self.users - 1)
            if self.users == 0 and self.library is not None:
                self.library.espeak_Terminate()
                self.library = None
                self.path = None
                self.data_path = None
                self.version = None


_MANAGER = _NativeManager()


class NativeEspeakProvider:
    """Independent ctypes binding around eSpeak NG's public phoneme API."""

    def __init__(
        self,
        *,
        library: str | None = None,
        data: str | None = None,
        executable: str | None = None,
        discovery_source: str | None = None,
        strict: bool = False,
    ) -> None:
        self.library_path = library
        self.data_path = data
        self.executable = executable
        self.discovery_source = discovery_source
        self._closed = False
        self._library = _MANAGER.acquire(library, data)
        self.exact_clause_api = hasattr(self._library, "espeak_TextToPhonemesWithTerminator")
        if strict and not self.exact_clause_api:
            self.close()
            raise BackendUnavailableError("loaded eSpeak library lacks espeak_TextToPhonemesWithTerminator")
        self.version = _MANAGER.version
        self.data_path = _MANAGER.data_path or data

    @property
    def diagnostics(self) -> BackendDiagnostics:
        return BackendDiagnostics(
            requested_mode="native",
            implementation="native",
            executable=self.executable,
            library_path=_MANAGER.path or self.library_path,
            data_path=self.data_path,
            discovery_source=self.discovery_source,
            version=self.version,
            exact_clause_api=self.exact_clause_api,
            parity="exact" if self.exact_clause_api else "best-effort",
        )

    def clauses(self, text: str, voice: str) -> list[Clause]:
        if self._closed:
            raise PhonemizationError("native eSpeak provider is closed")
        if not text:
            return []
        with _MANAGER.lock:
            result = self._library.espeak_SetVoiceByName(voice.encode("utf-8"))
            if result != 0:
                raise PhonemizationError(f"eSpeak voice {voice!r} was not found (code {result})")
            buffer = ctypes.create_string_buffer(text.encode("utf-8") + b"\0")
            pointer = ctypes.c_void_p(ctypes.addressof(buffer))
            clauses: list[Clause] = []
            while pointer.value:
                previous = pointer.value
                terminator = ctypes.c_int(0)
                if self.exact_clause_api:
                    value = self._library.espeak_TextToPhonemesWithTerminator(
                        ctypes.byref(pointer), CHARS_UTF8, IPA_OUTPUT, ctypes.byref(terminator)
                    )
                else:
                    value = self._library.espeak_TextToPhonemes(ctypes.byref(pointer), CHARS_UTF8, IPA_OUTPUT)
                if pointer.value == previous:
                    raise PhonemizationError("eSpeak clause API made no progress")
                payload = value.decode("utf-8") if value else ""
                token, sentence_end = _TERMINATORS.get(terminator.value & 0xFFF000, (None, False))
                clauses.append(Clause(payload, token, sentence_end))
            return clauses

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            _MANAGER.release()

    def __enter__(self) -> "NativeEspeakProvider":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
