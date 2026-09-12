# eSpeak backends

Auto mode rejects a native library without `espeak_TextToPhonemesWithTerminator` and falls back to CLI with a distinct `terminator API unavailable` diagnostic. This prevents an old native library from silently losing Piper clause boundaries.
`EspeakBackend` supports `auto`, `native`, and `cli` modes. Auto mode attempts the native shared library first and falls back to the CLI with a `BackendFallbackWarning`. Native mode fails clearly when the library or exact clause API is unavailable. CLI mode is explicitly `best-effort`.

Native conversion uses the public eSpeak NG functions `espeak_Initialize`, `espeak_SetVoiceByName`, and `espeak_TextToPhonemesWithTerminator`. The process-wide native manager holds an `RLock` across voice selection and complete clause conversion because eSpeak has mutable global state.

Discovery prefers explicit overrides, the optional modern eSpeak loader, system eSpeak NG, and legacy eSpeak. The selected source is exposed as `BackendDiagnostics.discovery_source`.
`BackendDiagnostics` reports the requested mode, implementation, executable, library, data path, version, exact clause support, fallback reason, and parity label. eSpeak data discovery never imports Piper.

Clause transformations are pure Python around a clause provider. They remove language-switch markers, retain comma, colon, and semicolon punctuation with a following space, preserve sentence punctuation, apply NFD after assembly, merge configured vowel clusters longest-first, and emit residual final text.
