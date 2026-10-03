# piperg2p documentation

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
quickstart
voice-config
encoding
espeak
lexicons
raw-phonemes
phoneme-types
compatibility
provenance
reference-benchmark
contributing
changelog
api/core
api/backends
api/config
api/diagnostics
```

The project is an independent phoneme and ID frontend. It accepts prepared, speakable text and does not synthesize audio or own written-to-spoken semantic normalization.

Applications that need number, unit, currency, date, abbreviation, or other semantic expansion may prepare text with a separate package such as Spokenform before calling `phonemize_prepared()`. Spokenform is not a PiperG2P dependency.
