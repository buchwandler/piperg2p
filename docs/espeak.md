# eSpeak backends

## User-visible modes

For eSpeak-backed Piper voices, `espeak_mode` selects `"auto"`, `"native"`, or `"cli"`:

| Mode     | Behavior                                                                                                    |
| -------- | ----------------------------------------------------------------------------------------------------------- |
| `auto`   | Request exact-capable native support; fall back to CLI if unavailable and emit one `BackendFallbackWarning` |
| `native` | Require exact-capable native support; never fall back                                                       |
| `cli`    | Use CLI directly; its compatibility label is best-effort                                                    |

Text voices do not invoke eSpeak. See [voice configuration](voice-config.md) for the distinction between the high-level `language` routing label and the configured base `espeak.voice`.

## Clause capability versus phoneme parity

Native output is labeled `exact` only when `espeakng-runtime` exposes the terminator-capable clause API. CLI output is always `best-effort`. Exact clause boundaries do not guarantee identical phoneme semantics: isolated weak words can differ between native and CLI. Piper's `parity` diagnostic is the historical clause/composition label; `phoneme_parity` reports the runtime's raw phoneme semantic parity.

## Inspect capabilities

`inspect_espeak()` is a Piper compatibility facade over runtime inspection. It does not initialize eSpeak or emit fallback warnings:

```python
from piperg2p import inspect_espeak

info = inspect_espeak()
print("CLI available:", info.cli_available)
print("exact native:", info.exact_native_available)
print("selected:", info.selected_exact_library)
for candidate in info.candidates:
    print(candidate.source, candidate.library, candidate.loadable,
          candidate.exact_clause_api, candidate.error)
```

## Configuration and environment precedence

Runtime variables are `ESPEAKNG_RUNTIME_EXECUTABLE`, `ESPEAKNG_RUNTIME_LIBRARY`, and `ESPEAKNG_RUNTIME_DATA`. PiperG2P retains `PIPERG2P_ESPEAK_EXECUTABLE`, `PIPERG2P_ESPEAK_LIBRARY`, and `PIPERG2P_ESPEAK_DATA` as compatibility variables. Precedence is explicit Piper constructor argument, legacy Piper variable, runtime variable, then runtime automatic discovery.

For bundled loader support on supported desktop/server platforms:

```bash
python -m pip install "piperg2p[espeak-direct]"
```

## Runtime ownership and Piper composition

`espeakng-runtime` owns executable, shared-library, and data discovery; optional `espeakng-loader` integration; native calls; process-global locking; and subprocess invocation. PiperG2P keeps Piper-specific clause composition and phoneme policy locally.

Phrasplit supplies best-effort sentence spans to the CLI path through its exact-offset API. Piper requests sentence mode with `use_spacy=False`, passing the eSpeak voice as the language; spaCy and its model-selection path are never loaded. Piper retains its local comma, semicolon, and colon clause composition, URL-punctuation protection, NFD normalization, language-switch and joiner cleanup, punctuation spacing, vowel-cluster merging, raw blocks, and lexicon overlays.

The local CLI splitter may produce clause bodies containing source line breaks, for example after a paragraph break. Piper passes these multiline elements to `espeakng-runtime`'s `phonemize_many()` rather than stripping the line breaks. This behavior requires `espeakng-runtime` 0.1.5 or later.

`BackendDiagnostics` maps runtime information to Piper's stable fields, including implementation, parity, exact clause support, fallback reason/code, selected paths, discovery source, version, and native probes. `phoneme_output_api` identifies the runtime's phoneme generation mechanism. Runtime source name `espeakng-loader` is exposed under Piper's historical `modern-loader` compatibility name.

`EspeakCliBackend` and `NativeEspeakProvider` remain thin compatibility wrappers for downstream code. They use the runtime for eSpeak operations and return Piper-local `Clause` records.

## Termux / Android

Install Termux's system eSpeak package; do not use the bundled desktop/server loader merely to obtain eSpeak on Android. Use `inspect_espeak()` to check whether the system library exposes exact native capability. `espeak_mode="auto"` falls back to CLI when that capability is unavailable. Capability discovery handles future Termux package upgrades without a hard-coded version claim. See [installation](installation.md).

## Benchmark

For pronunciation correctness, `benchmarks/benchmark_espeak.py` invokes the external executable directly with `-q --ipa=3 -v <voice> --stdin`; the reference does not call PiperG2P's backend or `espeakng-runtime`. Select native, CLI, or auto candidates and use explicitly captured goldens when needed. See the [reference benchmark guide](reference-benchmark.md).
