# piperg2p

`piperg2p` is an independent, voice-config-driven Piper-compatible frontend. It produces phoneme sequences and model IDs from Piper ONNX voice configurations. It does not synthesize audio, require Piper, or include Piper source or model data.

## Delivered scope

- `text` phoneme voices with no eSpeak dependency.
- `espeak` voices through a native eSpeak NG public API binding or an explicit CLI fallback.
- Unicode NFD normalization and voice-specific ID maps.
- Sentence-grouped results and raw `[[ ... ]]` phoneme blocks in eSpeak mode.
- Immutable diagnostics, typed configuration, errors, and missing-phoneme reporting.

The native clause API is labeled `exact` only when it is available. The CLI path is always labeled `best-effort`. Pinyin, Japanese, Thai, Hebrew, and Arabic adapters are planned but are not part of this release.

## Install

```bash
pip install .
```

Install eSpeak NG separately for eSpeak voices. Text voices need no optional runtime package.

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

## Compatibility

Compatibility is measured against pinned reference profiles, not a moving upstream branch. See [docs/compatibility.md](docs/compatibility.md), [docs/espeak.md](docs/espeak.md), and [docs/provenance.md](docs/provenance.md).

## Independence

The runtime package has no Piper dependency, does not import Piper, and does not bundle Piper GPL assets. Reference corpus metadata is development evidence only.
