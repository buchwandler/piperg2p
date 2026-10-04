# Quick start

## One-shot structured result

Use `phonemize_prepared()` for a structured result:

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

`language` is a source/routing label. The `config` selects the Piper voice, including its phoneme type, base eSpeak voice, and authoritative `phoneme_id_map`. A language argument does not switch the configured Piper model or base voice.

## Reusable facade

For repeated calls, `get_g2p()` provides a reusable, bounded-cache facade:

```python
from piperg2p import get_g2p

with get_g2p("en-us", config="voice.onnx.json") as g2p:
    result = g2p.phonemize_prepared("Hello world")
    for sentence in result.sentences:
        print(sentence.phoneme_string)
        print(sentence.ids)
```

## Result and advanced features

`PhonemizeResult` exposes the flattened phoneme string and token IDs as convenient views. For Piper inference, process each `sentence.ids` independently. See [practical usage](usage.md) for return types, caching, policies, and configuration inputs.

PiperG2P consumes prepared, speakable text and does not own number, unit, date, currency, or abbreviation verbalization. See the canonical [prepared-text guide](prepared-text.md) for semantic ownership and composition boundaries.

For source-aligned overrides, annotations, and marker helpers, see [overrides](overrides.md). For explicit and evidence-driven language selection, see [language routing](language-routing.md).
