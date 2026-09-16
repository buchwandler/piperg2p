from __future__ import annotations

import types

from espeakng_runtime import Clause as RuntimeClause

from piperg2p import EspeakCliBackend, NativeEspeakProvider
from piperg2p.backends.espeak import cli as cli_module
from piperg2p.backends.espeak import native as native_module
from piperg2p.backends.espeak.clauses import (
    Clause,
    compose_clauses,
    merge_vowel_clusters,
)


def _info(mode: str, *, exact: bool):
    return types.SimpleNamespace(
        requested_mode=mode,
        implementation=mode,
        executable="espeak-ng",
        library="libespeak-ng.so" if mode == "native" else None,
        data="data",
        source="system-espeak-ng" if mode == "native" else "cli",
        version="1.0",
        exact_clause_api=exact,
        fallback_reason=None,
        fallback_code=None,
        parity="exact" if exact else "best-effort",
    )


class FakeRuntime:
    def __init__(self, **kwargs: object) -> None:
        self.mode = str(kwargs["mode"])
        self.info = _info(self.mode, exact=self.mode == "native")
        self.calls: list[tuple[str, object]] = []

    def phonemize(self, text: str, *, voice: str) -> str:
        self.calls.append(("phonemize", (text, voice)))
        return "hɛlə" if text == "hé" else text

    def clauses(self, text: str, *, voice: str, exact: bool = False):
        self.calls.append(("clauses", (text, voice, exact)))
        return [
            RuntimeClause(
                phonemes="hɛlə",
                terminator=".",
                terminator_code=0x80028,
                sentence_end=True,
            )
        ]

    def close(self) -> None:
        pass


def test_clause_composition_preserves_punctuation_and_normalizes():
    clauses = [
        Clause("a", ",", False),
        Clause("e", ".", True),
        Clause("?", None, True),
    ]
    assert compose_clauses(clauses) == [["a", ",", " ", "e", "."], ["?"]]


def test_clause_composition_removes_switches_and_merges_longest():
    assert merge_vowel_clusters(
        ["a", "b", "c"], frozenset({("a", "b"), ("a", "b", "c")})
    ) == ["abc"]
    assert compose_clauses([Clause("a(b)\u0301", None, False)], frozenset()) == [
        ["a", "\u0301"]
    ]


def test_cli_compatibility_wrapper_uses_runtime_and_local_splitter(monkeypatch):
    monkeypatch.setattr(cli_module, "EspeakRuntime", FakeRuntime)
    backend = EspeakCliBackend(executable="espeak-ng")

    assert backend.phonemize("hé", voice="en-us") == [["h", "ɛ", "l", "ə"]]
    assert backend.diagnostics.parity == "best-effort"
    assert backend._runtime.calls == [("phonemize", ("hé", "en-us"))]
    backend.close()


def test_native_compatibility_wrapper_converts_runtime_clauses(monkeypatch):
    monkeypatch.setattr(native_module, "EspeakRuntime", FakeRuntime)
    provider = NativeEspeakProvider(library="libespeak-ng.so", strict=True)

    assert provider.clauses("Hello.", "en-us") == [Clause("hɛlə", ".", True)]
    assert provider._runtime.calls == [("clauses", ("Hello.", "en-us", True))]
    provider.close()
