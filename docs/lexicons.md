# Pronunciation lexicons

`piperg2p` has two runtime modes for eSpeak voices:

- **eSpeak-only**, the default, preserves the normal Piper-compatible eSpeak route.
- **Lexicon-first**, an opt-in overlay that uses a pronunciation lexicon for source words and sends unresolved source intervals to PiperG2P's own `EspeakBackend`.

Lexicon-first is a PiperG2P extension. It intentionally overrides selected eSpeak pronunciations and is not upstream Piper exact parity.

## Managed Lexphon assets

Install the optional dependency:

```bash
pip install 'piperg2p[lexphon]'
```

Then select installed identifiers at runtime:

```python
from piperg2p import PiperFrontend

frontend = PiperFrontend.from_config(
    "voice.onnx.json",
    lexicons=("de-de:espeak-piper",),
)
```

Lexphon is used with `fallback=None`. It performs lexicon-only lookup. A miss is passed to PiperG2P's eSpeak backend, not to Lexphon's generic eSpeak provider. Data is never downloaded implicitly. Install and verify assets through Lexphon's data tooling before inference.

The lexicon language defaults to `VoiceConfig.espeak_voice`.

## Direct local G2Lex assets

Install the separate runtime and pass explicit files:

```bash
pip install 'piperg2p[g2lex]'
```

```python
from piperg2p import PiperFrontend
from piperg2p.lexicons import G2LexLookup

lookup = G2LexLookup(["./build/custom.g2lex"], language="de-DE")
frontend = PiperFrontend.from_config(
    "voice.onnx.json",
    lexicon_backend=lookup,
)
```

The direct adapter uses exact keys and configured path order. It is intended for local development before assets are installed into Lexphon. Built-in adapters read the modern `phoneme_encoding` metadata, accept generic IPA and `espeak-ipa3`, and reject unsupported kinds, languages, or encodings.
Injected adapters are owned by the caller. Adapters created internally from `lexicons=` are closed by `PiperFrontend`.

## Precedence and composition

The precedence order is:

1. Explicit `[[ raw phonemes ]]` blocks.
2. Configured lexicons, in order.
3. PiperG2P eSpeak fallback for unresolved source intervals.
4. The configured model missing-symbol policy during ID encoding.

Words are scanned without discarding punctuation or source whitespace. Lookup is batched per ordinary source segment. Unresolved intervals are coalesced so eSpeak retains context, while explicit raw and lexical segments remain in source order. Generic IPA hits use NFD normalization. `espeak-ipa3` hits are preserved as Piper raw phoneme content. Final IDs always use the voice-specific map and selected missing-symbol policy.

A lexicon hit containing a symbol absent from the voice map is not silently replaced by eSpeak. `error`, `warn`, and `ignore` follow the normal encoder policy.

## Diagnostics and reproducibility
`result.diagnostics.lexicon` reports whether the overlay is enabled, its implementation, language, identifiers, encodings, immutable asset provenance, and compatibility label. The labels distinguish generic IPA overrides from Piper frozen eSpeak assets. Asset provenance should include data version, producer, transform, and generator identity when supplied. A frozen eSpeak-derived dictionary combined with a different live eSpeak version can produce mixed-version output, so lexicon-first output is an extension rather than an unqualified exactness claim.

Lexicon lookup/resource failures are errors, not normal misses. Optional packages are imported only when an adapter is selected. Core imports and eSpeak-only frontends do not require Lexphon or G2Lex.

Mixed lexicon/eSpeak sentences can differ from pure eSpeak because selected source spans are intentionally converted independently. Do not claim bit-identical upstream Piper output for lexicon-first mode.
