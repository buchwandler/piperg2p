from __future__ import annotations

import types

import phrasplit
from espeakng_runtime import Clause as RuntimeClause

from piperg2p import EspeakCliBackend, NativeEspeakProvider
from piperg2p.backends.espeak import cli as cli_module
from piperg2p.backends.espeak import native as native_module
from piperg2p.backends.espeak.clauses import (
    Clause,
    best_effort_clauses,
    compose_clauses,
    merge_vowel_clusters,
    split_cli_clauses,
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
        phoneme_output_api="native-trace" if mode == "native" else "cli",
        phoneme_parity="exact" if exact else "best-effort",
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

    def phonemize_many(self, texts: list[str], *, voice: str) -> list[str]:
        self.calls.append(("phonemize_many", (texts, voice)))
        return [self.phonemize(text, voice=voice) for text in texts]

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
    assert any(call[0] == "phonemize_many" for call in backend._runtime.calls)
    backend.close()


def test_native_compatibility_wrapper_converts_runtime_clauses(monkeypatch):
    monkeypatch.setattr(native_module, "EspeakRuntime", FakeRuntime)
    provider = NativeEspeakProvider(library="libespeak-ng.so", strict=True)

    assert provider.clauses("Hello.", "en-us") == [Clause("hɛlə", ".", True)]
    assert provider._runtime.calls == [("clauses", ("Hello.", "en-us", True))]
    provider.close()


def test_cli_splitter_preserves_leading_paragraph_breaks():
    from piperg2p.backends.espeak.clauses import split_cli_clauses

    text = '\n\n"But wait..." she asked, "are you sure?"'
    parts = split_cli_clauses(text)

    assert parts[0][0].startswith("\n\n")
    assert "".join(body + (terminator or "") for body, terminator, _ in parts) == text
    assert sum(sentence_end for _, _, sentence_end in parts) == 1


def test_cli_compatibility_wrapper_accepts_multiline_clause_body(monkeypatch):
    monkeypatch.setattr(cli_module, "EspeakRuntime", FakeRuntime)
    backend = EspeakCliBackend(executable="espeak-ng")

    result = backend.phonemize(
        '\n\n"But wait..." she asked, "are you sure?"',
        voice="en-us",
    )

    assert result
    batch_calls = [
        call for call in backend._runtime.calls if call[0] == "phonemize_many"
    ]
    assert batch_calls
    texts, selected_voice = batch_calls[0][1]
    assert selected_voice == "en-us"
    assert texts[0].startswith("\n\n")

    backend.close()


def _cli_sentence_groups(text: str, *, language: str = "en") -> list[str]:
    groups: list[str] = []
    current = ""
    for body, terminator, sentence_end in split_cli_clauses(text, language=language):
        current += body + (terminator or "")
        if sentence_end:
            groups.append(current)
            current = ""
    if current:
        groups.append(current)
    return groups


def test_cli_sentence_boundaries_cover_abbreviations_urls_and_punctuation() -> None:
    cases = (
        ("en", "Dr. Smith left. Next.", ["Dr. Smith left.", "Next."]),
        ("en", "3.14 is pi. Next.", ["3.14 is pi.", "Next."]),
        ("en", "The U.S. team won. Next.", ["The U.S. team won.", "Next."]),
        ("en", "e.g. this continues. Next.", ["e.g. this continues.", "Next."]),
        (
            "en",
            "Visit https://example.com/docs. Next.",
            ["Visit https://example.com/docs.", "Next."],
        ),
        (
            "en",
            '"Really?" she asked. Then she left.',
            ['"Really?" she asked.', "Then she left."],
        ),
        ("en", "Hello... World?!", ["Hello...", "World?!"]),
        ("en", "Mr. Jones, however, stayed.", ["Mr. Jones, however, stayed."]),
        (
            "en",
            "Version 1.2.3 is installed. Continue.",
            ["Version 1.2.3 is installed.", "Continue."],
        ),
        (
            "de-de",
            "Dr. Müller kam. Dann ging er.",
            ["Dr. Müller kam.", "Dann ging er."],
        ),
        (
            "fr-fr",
            "M. Dupont est arrivé. Il est parti.",
            ["M. Dupont est arrivé.", "Il est parti."],
        ),
        (
            "es-es",
            "Sr. García llegó. Luego salió.",
            ["Sr. García llegó.", "Luego salió."],
        ),
    )
    for language, text, expected in cases:
        groups = _cli_sentence_groups(text, language=language)
        assert [group.strip() for group in groups] == expected
        assert "".join(group for group in groups) == text


def test_cli_sentence_split_forces_regex_and_passes_voice_language(monkeypatch) -> None:
    original_split = phrasplit.split_with_offsets_with_diagnostics
    calls: list[dict[str, object]] = []

    def record_split(text: str, **options):
        calls.append(options)
        return original_split(text, **options)

    monkeypatch.setattr(phrasplit, "split_with_offsets_with_diagnostics", record_split)
    clauses = best_effort_clauses(
        FakeRuntime(mode="cli"), "Dr. Smith left. Next.", voice="fr-fr"
    )

    assert clauses
    assert calls == [{"mode": "sentence", "use_spacy": False, "language": "fr-fr"}]


def test_composition_retains_each_punctuation_in_a_sentence_cluster() -> None:
    assert compose_clauses([Clause("hello", "...?!", True)]) == [
        ["h", "e", "l", "l", "o", ".", ".", ".", "?", "!"]
    ]
