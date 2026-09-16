# Backend API

`EspeakBackend(mode="auto")` is PiperG2P's adapter to `espeakng-runtime`. It requests an exact-capable native runtime when available and otherwise uses runtime CLI phonemization with Piper's local clause splitter and composition. Automatic fallback emits `BackendFallbackWarning`; explicit `mode="cli"` does not warn.

`mode="native"` requires exact native clause support and raises `BackendUnavailableError` when it is unavailable. `mode="cli"` does not probe native through Piper policy and always reports best-effort parity.

Piper owns the public three-field `Clause`, clause composition, NFD normalization, punctuation spacing, language-switch and joiner cleanup, vowel-cluster merging, raw blocks, and lexicon overlays. Runtime clauses are converted explicitly at the adapter boundary. Runtime terminator codes are not exposed through Piper's local `Clause`.

`BackendDiagnostics` preserves Piper's stable diagnostics fields while mapping `RuntimeInfo`, including implementation, selected executable/library/data paths, discovery source, version, exact clause capability, parity, fallback reason, warnings, and native candidate probes. The runtime source name `espeakng-loader` is mapped to Piper's historical `modern-loader` name.

The compatibility classes `EspeakCliBackend` and `NativeEspeakProvider` remain available. They retain their existing constructor shapes while delegating all eSpeak execution and lifetime management to `espeakng-runtime`.

Legacy configuration variables remain supported:

- `PIPERG2P_ESPEAK_EXECUTABLE`
- `PIPERG2P_ESPEAK_LIBRARY`
- `PIPERG2P_ESPEAK_DATA`

Explicit Piper constructor arguments take precedence over those variables, followed by the corresponding `ESPEAKNG_RUNTIME_*` variables and runtime discovery. `inspect_espeak()` is a non-initializing Piper compatibility facade over runtime inspection.
