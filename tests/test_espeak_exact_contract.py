from __future__ import annotations

import types
from typing import ClassVar

import pytest
from espeakng_runtime import Clause as RuntimeClause
from espeakng_runtime.errors import (
    CapabilityError,
    EspeakConflictError,
    EspeakUnavailableError,
    VoiceNotFoundError,
)
from espeakng_runtime.errors import PhonemizationError as RuntimePhonemizationError

from piperg2p import (
    BackendUnavailableError,
    EspeakBackend,
    PhonemizationError,
)
from piperg2p.backends.espeak import backend as backend_module


def _info(*, mode: str = "native", exact: bool = True):
    return types.SimpleNamespace(
        requested_mode=mode,
        implementation="native" if mode != "cli" else "cli",
        executable="espeak-ng",
        library="libespeak-ng.so" if mode != "cli" else None,
        data="data",
        source="system-espeak-ng",
        version="1.0",
        exact_clause_api=exact,
        fallback_reason=None,
        fallback_code=None,
        parity="exact" if exact else "best-effort",
    )


class Runtime:
    info_value = _info()
    error: Exception | None = None
    clauses_value: ClassVar[list[RuntimeClause]] = [
        RuntimeClause(
            phonemes="a",
            terminator=",",
            terminator_code=0x41014,
            sentence_end=False,
        ),
        RuntimeClause(
            phonemes="e",
            terminator=".",
            terminator_code=0x80028,
            sentence_end=True,
        ),
    ]

    def __init__(self, **kwargs: object) -> None:
        if self.error:
            raise self.error
        self.kwargs = kwargs
        self.info = self.info_value
        self.calls: list[tuple[str, object]] = []

    def clauses(self, text: str, *, voice: str, exact: bool = False):
        self.calls.append(("clauses", (text, voice, exact)))
        return self.clauses_value

    def phonemize(self, text: str, *, voice: str) -> str:
        self.calls.append(("phonemize", (text, voice)))
        return text

    def close(self) -> None:
        pass


@pytest.fixture(autouse=True)
def patch_runtime(monkeypatch: pytest.MonkeyPatch):
    Runtime.error = None
    Runtime.info_value = _info()
    monkeypatch.setattr(backend_module, "EspeakRuntime", Runtime)
    monkeypatch.setattr(
        backend_module,
        "inspect_espeak",
        lambda **kwargs: types.SimpleNamespace(candidates=()),
    )


def test_native_exact_conversion_uses_runtime_clause_codes_only_at_runtime_boundary():
    backend = EspeakBackend(mode="native")

    assert backend.phonemize("ignored", voice="en-us") == [["a", ",", " ", "e", "."]]
    assert backend._runtime.calls == [("clauses", ("ignored", "en-us", True))]
    backend.close()


def test_cli_policy_uses_local_splitter_and_not_runtime_clauses():
    Runtime.info_value = _info(mode="cli", exact=False)
    backend = EspeakBackend(mode="cli")

    assert backend.phonemize("Hello... World?!", voice="en-us") == [
        ["H", "e", "l", "l", "o", "."],
        ["."],
        ["."],
        [" ", "W", "o", "r", "l", "d", "?"],
        ["!"],
    ]
    assert all(call[0] == "phonemize" for call in backend._runtime.calls)
    backend.close()


def test_native_runtime_failure_maps_to_backend_unavailable():
    Runtime.error = EspeakUnavailableError("missing native")
    with pytest.raises(BackendUnavailableError, match="missing native"):
        EspeakBackend(mode="native")


@pytest.mark.parametrize(
    "error, expected",
    [
        (RuntimePhonemizationError("phoneme failure"), PhonemizationError),
        (VoiceNotFoundError("voice failure"), PhonemizationError),
    ],
)
def test_runtime_phonemization_errors_map_to_piper_errors(error, expected):
    Runtime.info_value = _info(mode="cli", exact=False)
    backend = EspeakBackend(mode="cli")

    def fail(*args: object, **kwargs: object):
        raise error

    backend._runtime.phonemize = fail
    with pytest.raises(expected, match="failure"):
        backend.phonemize("hello", voice="en-us")
    backend.close()


def test_runtime_capability_and_conflict_errors_map_to_backend_unavailable():
    Runtime.info_value = _info(mode="cli", exact=False)
    backend = EspeakBackend(mode="cli")
    for error in (CapabilityError("capability"), EspeakConflictError("conflict")):
        backend._runtime.phonemize = lambda *args, error=error, **kwargs: (
            _ for _ in ()
        ).throw(error)
        with pytest.raises(BackendUnavailableError, match="capability|conflict"):
            backend.phonemize("hello", voice="en-us")
    backend.close()


def test_empty_text_is_preserved():
    backend = EspeakBackend(mode="cli")
    assert backend.phonemize("", voice="en-us") == []
    backend.close()
