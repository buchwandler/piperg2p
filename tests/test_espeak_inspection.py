from __future__ import annotations

import types

from espeakng_runtime.discovery import LibraryProbe

from piperg2p import EspeakLibraryCandidate, inspect_espeak
from piperg2p.backends.espeak import discovery


def _runtime_probe(
    library: str,
    source: str,
    *,
    exact: bool,
    phoneme_trace: bool = False,
    error: str | None = None,
) -> LibraryProbe:
    return LibraryProbe(
        library=library,
        source=source,
        data="data",
        loadable=True,
        exact_clause_api=exact,
        phoneme_trace_api=phoneme_trace,
        error=error,
    )


def test_inspection_maps_runtime_fields_and_legacy_source(monkeypatch):
    probes = (
        _runtime_probe("loader", "espeakng-loader", exact=False),
        _runtime_probe("system", "system-espeak-ng", exact=True),
    )
    monkeypatch.setattr(
        discovery,
        "runtime_inspect_espeak",
        lambda **kwargs: types.SimpleNamespace(
            executable="espeak-ng",
            cli_available=True,
            selected_library="system",
            selected_source="system-espeak-ng",
            selected_data="data",
            candidates=probes,
        ),
    )

    info = inspect_espeak()

    assert info.executable == "espeak-ng"
    assert info.cli_available
    assert info.selected_exact_library == "system"
    assert info.selected_source == "system-espeak-ng"
    assert info.selected_data == "data"
    assert [probe.source for probe in info.candidates] == [
        "modern-loader",
        "system-espeak-ng",
    ]
    assert info.exact_native_available


def test_inspection_passes_legacy_environment_values(monkeypatch):
    calls: list[dict[str, object]] = []
    monkeypatch.setenv("PIPERG2P_ESPEAK_EXECUTABLE", "piper-exe")
    monkeypatch.setenv("PIPERG2P_ESPEAK_LIBRARY", "piper-lib")
    monkeypatch.setenv("PIPERG2P_ESPEAK_DATA", "piper-data")
    monkeypatch.setattr(
        discovery,
        "runtime_inspect_espeak",
        lambda **kwargs: (
            calls.append(kwargs)
            or types.SimpleNamespace(
                executable="piper-exe",
                cli_available=True,
                selected_library="piper-lib",
                selected_source="explicit",
                selected_data="piper-data",
                candidates=(),
            )
        ),
    )

    inspect_espeak()

    assert calls == [
        {
            "executable": "piper-exe",
            "library": "piper-lib",
            "data": "piper-data",
            "require_exact_clauses": True,
        }
    ]


def test_candidate_type_is_immutable():
    candidate = EspeakLibraryCandidate("libespeak-ng.so", "system-espeak-ng")

    try:
        candidate.library = "other"
    except AttributeError:
        pass
    else:
        raise AssertionError("candidate should be immutable")


def test_discovery_wrappers_delegate_and_adapt_runtime_records(monkeypatch):
    candidate = types.SimpleNamespace(
        library="lib",
        source="espeakng-loader",
        data="data",
        explicit=True,
    )
    probe = types.SimpleNamespace(
        library="lib",
        source="espeakng-loader",
        data="data",
        loadable=True,
        exact_clause_api=True,
        error=None,
    )
    monkeypatch.setattr(
        discovery,
        "runtime_iter_library_candidates",
        lambda *args, **kwargs: (candidate,),
    )
    monkeypatch.setattr(discovery, "runtime_probe_library", lambda value: probe)

    candidates = discovery.iter_library_candidates("lib")
    converted = discovery.probe_library_candidate(candidates[0])

    assert candidates == (EspeakLibraryCandidate("lib", "modern-loader", "data", True),)
    assert converted.library == "lib"
    assert converted.source == "modern-loader"
    assert converted.exact_clause_api
    assert discovery.find_library("lib") == "lib"


def test_select_and_discover_adapt_runtime_results(monkeypatch):
    candidate = types.SimpleNamespace(
        library="lib",
        source="espeakng-loader",
        data="data",
        explicit=False,
    )
    probe = types.SimpleNamespace(
        library="lib",
        source="espeakng-loader",
        data="data",
        loadable=True,
        exact_clause_api=True,
        error=None,
    )
    select_calls: list[dict[str, object]] = []
    monkeypatch.setattr(
        discovery,
        "runtime_select_native",
        lambda **kwargs: select_calls.append(kwargs) or (candidate, (probe,)),
    )
    monkeypatch.setattr(
        discovery,
        "runtime_discover",
        lambda **kwargs: types.SimpleNamespace(
            executable="exe", library="lib", data="data", source="espeakng-loader"
        ),
    )

    selection = discovery.select_exact_native()
    paths = discovery.discover(require_executable=False)

    assert selection.candidate == EspeakLibraryCandidate(
        "lib", "modern-loader", "data", False
    )
    assert selection.probes[0].source == "modern-loader"
    assert select_calls[0]["require_exact_clauses"] is True
    assert paths == discovery.EspeakPaths("exe", "lib", "data", "modern-loader")
