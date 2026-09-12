from __future__ import annotations

import json

import pytest

from piperg2p import BackendUnavailableError, EspeakBackend, NativeEspeakProvider
from piperg2p.lexicons import G2LexLookup


def test_exact_native_epeak_clause_contract_if_provisioned():
    try:
        provider = NativeEspeakProvider(strict=True)
    except BackendUnavailableError:
        pytest.skip("terminator-capable eSpeak NG is not provisioned")
    try:
        clauses = provider.clauses("Hello, world.", "en-us")
        assert provider.diagnostics.exact_clause_api
        assert clauses[0].terminator == ","
        assert clauses[-1].sentence_end
    finally:
        provider.close()


def test_auto_backend_reports_exact_or_cli_fallback():
    backend = EspeakBackend(mode="auto")
    try:
        if backend.diagnostics.parity == "exact":
            assert backend.diagnostics.exact_clause_api
        else:
            assert backend.diagnostics.implementation == "cli"
            assert (
                backend.diagnostics.fallback_reason
                in {
                    "terminator API unavailable",
                }
                or backend.diagnostics.fallback_reason
            )
    finally:
        backend.close()


def test_direct_g2lex_reads_reproducible_temporary_asset(tmp_path):
    g2lex = pytest.importorskip("g2lex")
    source = tmp_path / "words.json"
    asset = tmp_path / "words.g2lex"
    source.write_text(json.dumps({"known": "noʊn"}), encoding="utf-8")
    g2lex.pack_file(
        source,
        asset,
        input_format="json-map",
        metadata={"language": "en-US", "pronunciation_alphabet": "ipa"},
    )

    with G2LexLookup((asset,), language="en-US") as lookup:
        assert lookup.lookup("known").pronunciation == "noʊn"
        assert lookup.lookup("unknown") is None
