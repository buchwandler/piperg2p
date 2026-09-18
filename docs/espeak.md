# eSpeak backends

`EspeakBackend` supports `auto`, `native`, and `cli` modes. PiperG2P delegates eSpeak discovery, native execution, CLI execution, voice selection, and lifetime management to `espeakng-runtime`. Piper retains its local clause composition and phoneme policy. Native output is labeled `exact` only when the runtime exposes the terminator-capable clause API. CLI output is always labeled `best-effort`.

**Important distinction:** The exact clause API provides exact clause boundaries, but the phoneme semantics in the exact-clause path may differ from CLI for isolated weak words. The `phoneme_parity` diagnostic field reports the runtime's raw phoneme semantic parity, while the `parity` field remains Piper's historical clause/composition compatibility label.

## Runtime ownership and mode policy

`espeakng-runtime` owns executable, shared-library, and data discovery, optional `espeakng-loader` integration, native ctypes calls, process-global locking, and subprocess invocation. PiperG2P does not duplicate those mechanics.

Piper's mode policy is:

- `auto` requests exact native capability from the runtime and falls back to CLI when it is unavailable. Piper emits one `BackendFallbackWarning` for that automatic fallback.
- `native` requires an exact-capable native runtime and never falls back.
- `cli` requests CLI directly, never probes native through Piper policy, and emits no fallback warning.

The runtime's generic clause splitter is not used for Piper CLI composition. Piper keeps `split_cli_clauses()` so punctuation clusters such as `Hello... World?!` retain existing Piper grouping behavior. Piper also retains NFD normalization, language-switch and joiner cleanup, punctuation spacing, vowel-cluster merging, raw blocks, and lexicon overlays.

Piper's local CLI splitter may produce clause bodies containing source line breaks, for example when a prepared segment begins after a paragraph break. `espeakng-runtime` therefore must support multiline elements in `phonemize_many()`. PiperG2P does not strip these line breaks to accommodate CLI batching; safe CLI transport is owned by the runtime. The minimum runtime version for this behavior is `0.1.5`.

## Configuration compatibility

Runtime variables are `ESPEAKNG_RUNTIME_EXECUTABLE`, `ESPEAKNG_RUNTIME_LIBRARY`, and `ESPEAKNG_RUNTIME_DATA`. PiperG2P continues to support `PIPERG2P_ESPEAK_EXECUTABLE`, `PIPERG2P_ESPEAK_LIBRARY`, and `PIPERG2P_ESPEAK_DATA` as compatibility variables. Precedence is an explicit Piper constructor argument, a legacy Piper variable, a runtime variable, then runtime automatic discovery.

For bundled loader support:

```bash
pip install "piperg2p[espeak-direct]"
```

## Capability inspection

`inspect_espeak()` remains available as a Piper compatibility facade over runtime inspection. It does not initialize eSpeak or emit fallback warnings:

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

`BackendDiagnostics` maps runtime information to Piper's stable fields, including implementation, parity, exact clause support, fallback reason/code, selected paths, discovery source, version, and native candidate probes. New fields include `phoneme_output_api` (the runtime's phoneme generation mechanism), `phoneme_parity` (the runtime's raw phoneme semantic parity), and `fallback_code` (the runtime's fallback cause identifier). The runtime source name `espeakng-loader` is exposed as Piper's historical `modern-loader` compatibility name.

## Public compatibility classes

`EspeakCliBackend` and `NativeEspeakProvider` remain available as thin wrappers for downstream code. They preserve their constructor shapes, use the runtime for eSpeak operations, and return Piper-local `Clause` records. Runtime clauses are converted explicitly, so runtime `terminator_code` does not alter Piper's three-field public `Clause`.

## IPA3 benchmark identity

For pronunciation correctness, `benchmarks/benchmark_espeak.py` invokes the external executable directly with `-q --ipa=3 -v <voice> --stdin`. The reference never calls PiperG2P's backend or the runtime package. Select `--candidate native`, `--candidate cli`, or `--candidate auto`; native fallback is reported in diagnostics. Use `--reference-source golden` only with an explicitly captured golden file.
