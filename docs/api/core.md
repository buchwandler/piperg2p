# Core API

`PiperFrontend` accepts a validated `VoiceConfig` and optional runtime lexicon settings:

```python
PiperFrontend(
    config,
    backend=None,
    missing=MissingPhonemePolicy.WARN,
    lexicons=(),
    lexicon_store=None,
    lexicon_backend=None,
)
```

`lexicons` and `lexicon_backend` are mutually exclusive. Lexicon overlays currently apply only to `phoneme_type="espeak"`. `VoiceConfig` is not modified by runtime lexicon selection, and its `phoneme_id_map` remains authoritative.

Stable lexicon contracts are available from `piperg2p.lexicons`: `PronunciationLookup`, `LexiconPronunciation`, `LexiconDiagnostics`, `LexphonLookup`, and `G2LexLookup`.

`FrontendDiagnostics.lexicon` is `None` when disabled. When enabled it identifies the implementation, language, identifiers, and override compatibility label.

High-level `phonemize_prepared()` accepts already-prepared text. Semantic preparation is intentionally outside the API. Applications may compose `spokenform.prepare_for_piperg2p()` before this call, but PiperG2P does not import or depend on Spokenform.
