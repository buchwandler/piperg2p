[![PyPI - Version](https://img.shields.io/pypi/v/piperg2p)](https://pypi.org/project/piperg2p/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/piperg2p)
![PyPI - Downloads](https://img.shields.io/pypi/dm/piperg2p)
[![codecov](https://codecov.io/gh/buchwandler/piperg2p/graph/badge.svg?token=eMF0pdgARs)](https://codecov.io/gh/buchwandler/piperg2p)

# piperg2p

`piperg2p` is an independent, voice-config-driven Piper-compatible frontend. It produces phoneme sequences and model IDs from Piper ONNX voice configurations. It does not synthesize audio, require Piper, or include Piper source or model data.

## Delivered scope

- `text` phoneme voices with no eSpeak dependency.
- `espeak` voices through `espeakng-runtime`, which provides native eSpeak NG access and CLI fallback while PiperG2P retains Piper-specific phoneme composition.
- Unicode NFD normalization and voice-specific ID maps.
- Sentence-grouped results and raw `[[ ... ]]` phoneme blocks in eSpeak mode.
- Immutable diagnostics, typed configuration, errors, and missing-phoneme reporting.

The native clause API is labeled `exact` only when it is available. The CLI path is always labeled `best-effort`. This release supports the named Piper Python `text` and ordinary `espeak` profile only. Pinyin, Hebrew, Japanese, and Thai are recognized configuration values but unavailable. Arabic eSpeak voices are rejected until Piper-compatible preprocessing is implemented.

## Install

```bash
pip install .
```

PiperG2P consumes **prepared, speakable text**. It does not verbalize numbers, abbreviations, units, currencies, dates, times, URLs, versions, or other written semantics. Prepare those forms in the calling application, then pass the result to `phonemize_prepared()`.

PiperG2P has no runtime dependency on Spokenform or Numeralform. Installing either package does not change core PiperG2P behavior.

This boundary does not change eSpeak compatibility: PiperG2P passes prepared text to the selected backend, and backend-specific pronunciation behavior remains unchanged.

Install PiperG2P normally. It depends on `espeakng-runtime`, which owns eSpeak discovery and execution. Text voices do not invoke eSpeak. For a bundled loader and data support, install `piperg2p[espeak-direct]`.

`PIPERG2P_ESPEAK_EXECUTABLE`, `PIPERG2P_ESPEAK_LIBRARY`, and `PIPERG2P_ESPEAK_DATA` remain supported compatibility variables. Explicit Piper constructor arguments take precedence over these variables, which take precedence over `ESPEAKNG_RUNTIME_*` variables and runtime discovery.

## Semantic preparation composition

Use a separate preparation package only when written semantics need expansion:

```python
from spokenform import prepare_for_piperg2p
from piperg2p import phonemize_prepared

prepared = prepare_for_piperg2p(
    "Pay $12.50 for 2 kg.",
    language="en",
).spoken_text

result = phonemize_prepared(
    prepared,
    language="en-us",
    config="voice.onnx.json",
)

print(result.phonemes)
print(result.token_ids)
```

Install Spokenform separately. It is not required for PiperG2P core installation or core tests.

## Usage

```python
from piperg2p import PiperFrontend

frontend = PiperFrontend.from_config("voice.onnx.json")
result = frontend.phonemize("Hello, world.")
for sentence in result.sentences:
    print(sentence.phoneme_string)
    print(sentence.ids)
    print(sentence.missing_phonemes)
```

The configured `phoneme_id_map` is authoritative. `result.ids` is a convenience flattening of sentence IDs. Model inference should normally consume each `sentence.ids` separately.

## Lexicon-first mode

Lexicon support is an opt-in overlay on the existing eSpeak frontend. Install `piperg2p[lexphon]` for managed Lexphon identifiers or `piperg2p[g2lex]` for explicit local `.g2lex` files. Raw `[[...]]` blocks have precedence, lexicon misses use PiperG2P's eSpeak backend, and no dictionary downloads occur implicitly. See [docs/lexicons.md](docs/lexicons.md).

Use `*:espeak` assets for generic IPA pronunciation overrides. Use `*:espeak-piper` assets for Piper raw phoneme behavior with `phoneme_encoding="espeak-ipa3"`. Lexphon installs and verifies data externally, while PiperG2P owns interpretation, precedence, and voice-map ID encoding.

## Compatibility

Compatibility is measured against pinned reference profiles, not a moving upstream branch. See [docs/compatibility.md](docs/compatibility.md), [docs/espeak.md](docs/espeak.md), and [docs/provenance.md](docs/provenance.md).

## Independence

The runtime package has no Piper dependency, does not import Piper, and does not bundle Piper GPL assets. Reference corpus metadata is development evidence only.

## Diagnostics

PiperG2P exposes detailed diagnostics for eSpeak backends through `BackendDiagnostics`. Key fields include:

- `implementation`: The backend implementation type (`native`, `cli`, `text`)
- `parity`: Piper's historical clause/composition compatibility label (`exact`, `best-effort`)
- `exact_clause_api`: Whether the runtime exposes the terminator-capable clause API
- `phoneme_output_api`: The runtime's phoneme generation mechanism (`native-trace`, `cli`)
- `phoneme_parity`: The runtime's raw phoneme semantic parity (`exact`, `best-effort`)
- `fallback_code`: The runtime's fallback cause identifier
- `fallback_reason`: Human-readable fallback reason

**Important:** The exact clause API provides exact clause boundaries, but the phoneme semantics in the exact-clause path may differ from CLI for isolated weak words. The `phoneme_parity` field reports the runtime's raw phoneme semantic parity, while the `parity` field remains Piper's historical clause/composition compatibility label.

## Sibling-style API

The high-level API keeps Piper voice configuration explicit while matching the shared development vocabulary used by sibling frontends:

```python
from piperg2p import phonemize_prepared

result = phonemize_prepared("Hello world", language="en-us", config="voice.onnx.json")
print(result.phonemes)
print(result.token_ids)
```

Use `get_g2p(language, config=...)` for reuse. `tokenize`, `OverrideSpan`, `TokenAnnotation`, marker helpers, bounded `cache_info`, and `ids_to_phonemes` are also exported. The API never downloads models or lexicons. See `examples/README.md` for the twelve executable examples.
