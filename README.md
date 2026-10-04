[![PyPI - Version](https://img.shields.io/pypi/v/piperg2p)](https://pypi.org/project/piperg2p/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/piperg2p)
[![codecov](https://codecov.io/gh/buchwandler/piperg2p/graph/badge.svg?token=eMF0pdgARs)](https://codecov.io/gh/buchwandler/piperg2p)

# PiperG2P

`piperg2p` is an independent, voice-config-driven frontend for Piper ONNX voice configurations. It converts prepared text to phonemes and model IDs; it does not synthesize audio or require Piper at runtime.

- Piper `text` and `espeak` phoneme types with voice-specific ID maps
- Sentence-scoped results for model inference
- Raw `[[ ... ]]` phoneme blocks
- Optional Lexphon and G2Lex pronunciation overlays
- Explicit backend modes and diagnostics
- A reusable sibling-style high-level API

## Install

```bash
python -m pip install piperg2p
```

| Extra                     | Purpose                                                    |
| ------------------------- | ---------------------------------------------------------- |
| `piperg2p[lexphon]`       | Managed installed pronunciation assets                     |
| `piperg2p[lexicons]`      | Compatibility/convenience alias for `lexphon`              |
| `piperg2p[g2lex]`         | Direct local `.g2lex` assets                               |
| `piperg2p[espeak-direct]` | Bundled-loader support through `espeakng-runtime[bundled]` |
| `piperg2p[reference]`     | Reference/phonetic benchmark tooling                       |
| `piperg2p[docs]`          | Documentation build dependencies                           |

## Quick start

Use `phonemize_prepared()` for the structured high-level result:

```python
from piperg2p import phonemize_prepared

result = phonemize_prepared(
    "Hello world",
    language="en-us",
    config="voice.onnx.json",
)

print(result.phonemes)
print(result.token_ids)
```

For repeated use, construct a reusable cached facade:

```python
from piperg2p import get_g2p

with get_g2p("en-us", config="voice.onnx.json") as g2p:
    result = g2p.phonemize_prepared("Hello world")
```

The `language` argument is a source/routing language label. The `config` selects the Piper voice and its `phoneme_id_map`; `espeak.voice` in that config sets the base eSpeak voice. A language label does not select or replace the Piper model or configured base voice.

## Results

`result.phonemes` and `result.token_ids` are convenient flattened views. For Piper inference, normally process each sentence independently:

```python
for sentence in result.sentences:
    print(sentence.phoneme_string)
    print(sentence.ids)
```

The module-level `phonemize_prepared()` (also exported as `phonemize()`) returns a `PhonemizeResult`. `phonemes()` returns a plain string and `phoneme_ids()` returns a list of IDs. `PiperG2P.phonemize()` also returns a string; use `PiperG2P.phonemize_prepared()` when you need the structured result.

## Prepared text

PiperG2P consumes prepared, speakable text; it does not verbalize written numbers, dates, units, or other semantic forms. An application may compose it with a separate preparation layer, but that layer is not a PiperG2P dependency. See the [prepared-text guide](docs/prepared-text.md).

## eSpeak and lexicons

eSpeak backend behavior and capability modes are described in the [eSpeak guide](docs/espeak.md). Lexicon installation and selection are covered in the [lexicon guide](docs/lexicons.md); assets are never downloaded implicitly.

## Compatibility

Compatibility claims are tied to concrete backend capabilities and pinned reference profiles. See [compatibility](docs/compatibility.md), [provenance](docs/provenance.md), and the [reference benchmark guide](docs/reference-benchmark.md).

## Documentation and examples

- [Full documentation](docs/index.md)
- [Executable examples](examples/README.md)
- [Contributing](docs/contributing.md)

PiperG2P does not bundle Piper source or model data and has no runtime dependency on Piper, Spokenform, or Numeralform.
