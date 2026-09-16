# eSpeak backends

`EspeakBackend` supports `auto`, `native`, and `cli` modes. Piper's native path is labeled `exact` only when the loaded library exports `espeak_TextToPhonemesWithTerminator`. The CLI path is always labeled `best-effort`.

## Native capability selection

Auto mode scans discovered native libraries in priority order and selects the first candidate that supports `espeak_TextToPhonemesWithTerminator`. The order is the optional `espeakng-loader`, system eSpeak NG, system eSpeak, and libraries near the configured or discovered executable. It falls back to the CLI only when no exact native candidate is available, and emits a `BackendFallbackWarning`.

Native mode requires an exact-capable native library and never silently falls back. CLI mode explicitly requests best-effort behavior, never probes native libraries, and does not emit a fallback warning. Exact native mode does not require a CLI executable.

`PIPERG2P_ESPEAK_LIBRARY` and the corresponding `library=` argument are authoritative. When either is configured, only that library is probed. If it is incompatible or unloadable, PiperG2P does not silently substitute another native library.

## Capability inspection

Use `inspect_espeak()` to inspect the same discovery path without constructing a backend, emitting warnings, or initializing eSpeak:

```python
from piperg2p import inspect_espeak

info = inspect_espeak()
print("CLI available:", info.cli_available)
print("exact native:", info.exact_native_available)
print("selected:", info.selected_exact_library)

for candidate in info.candidates:
    print(
        candidate.source,
        candidate.library,
        candidate.loadable,
        candidate.exact_clause_api,
        candidate.error,
    )
```

Runtime `BackendDiagnostics` reports implementation, parity, exact clause support, fallback reason, selected library details, and the native candidate probes. This distinguishes a missing native library from a loadable library that lacks Piper's exact clause API.

Native conversion uses the public eSpeak NG functions `espeak_Initialize`, `espeak_SetVoiceByName`, and `espeak_TextToPhonemesWithTerminator`. The process-wide native manager holds an `RLock` across voice selection and complete clause conversion because eSpeak has mutable global state.

## IPA3 benchmark identity

For pronunciation correctness, `benchmarks/benchmark_espeak.py` invokes the external executable directly with `-q --ipa=3 -v <voice> --stdin`. The reference never calls PiperG2P's CLI backend. Select `--candidate native`, `--candidate cli`, or `--candidate auto`; native fallback is reported in diagnostics. Use `--reference-source golden` only with an explicitly captured golden file.

Clause transformations are pure Python around a clause provider. They remove language-switch markers, retain comma, colon, and semicolon punctuation with a following space, preserve sentence punctuation, apply NFD after assembly, merge configured vowel clusters longest-first, and emit residual final text.
