# Practical usage

PiperG2P's high-level API is the recommended entry point for application code. Pass prepared, speakable text, a source/routing language label, and a Piper voice configuration.

## One-shot calls

Use `phonemize_prepared()` when you need the structured result:

```python
from piperg2p import phonemize_prepared

result = phonemize_prepared(
    "Hello world",
    language="en-us",
    config="voice.onnx.json",
)
print(result.phonemes)
print(result.token_ids)
for sentence in result.sentences:
    print(sentence.phoneme_string)
    print(sentence.ids)
```

For only a plain phoneme string or a flattened ID list, use `phonemes()` or `phoneme_ids()`:

```python
from piperg2p import phoneme_ids, phonemes

plain = phonemes("Hello world", language="en-us", config="voice.onnx.json")
ids = phoneme_ids("Hello world", language="en-us", config="voice.onnx.json")
```

| Call                                                      | Return value      |
| --------------------------------------------------------- | ----------------- |
| `PiperG2P.phonemize(text)`                                | `str`             |
| `PiperG2P.phonemize_prepared(text, ...)`                  | `PhonemizeResult` |
| Module-level `phonemize_prepared(...)` / `phonemize(...)` | `PhonemizeResult` |
| Module-level `phonemes(...)`                              | `str`             |
| Module-level `phoneme_ids(...)`                           | `list[int]`       |

The similarly named APIs intentionally differ: module-level `phonemize()` is an alias of `phonemize_prepared()` and returns a structured result, while `PiperG2P.phonemize()` returns a string.

`phonemize_prepared()` retains the public `return_ids` and `return_phonemes` compatibility parameters, but currently ignores them; they do not change the result type or omit result fields.

## Reuse and caching

`get_g2p()` returns a reusable `PiperG2P`. Equivalent construction requests may reuse an object from the bounded cache:

```python
from piperg2p import get_g2p

with get_g2p("en-us", config="voice.onnx.json") as g2p:
    result = g2p.phonemize_prepared("First sentence. Second sentence.")
```

The context manager closes the facade when the block exits. `cache_info()` reports cache status, and `clear_cache()` closes and removes cached values. Use these when the application controls an explicit lifecycle or needs to reset cached objects.

## Configuration and policy

The `config` argument accepts a `.onnx.json` path, a `VoiceConfig`, or a mapping. `strict=False` selects compatibility-mode config parsing; strict parsing is the default. The configured voice data, especially its `phoneme_id_map`, remains authoritative for ID encoding.

`espeak_mode` selects `"auto"`, `"native"`, or `"cli"` for eSpeak-backed voices. Auto mode uses native eSpeak when the required capability is available and otherwise falls back to CLI; inspect [eSpeak modes and diagnostics](espeak.md) for details. Text voices do not invoke eSpeak.

The `missing` option accepts `MissingPhonemePolicy.ERROR`, `WARN`, or `IGNORE`. These policies control what happens when a produced symbol is absent from the voice map; missing symbols remain represented in result reporting when processing continues. See [encoding and missing phonemes](encoding.md).

## Sentence IDs

`result.token_ids` and `result.ids` are convenient flattened views. Piper inference normally consumes each `sentence.ids` as a separate sequence, so retain `result.sentences` when preparing model input.

For result fields and span coordinates, see [API result types](api/types.md). For source-aligned overrides, annotations, markers, and language routing, see [overrides](overrides.md) and [language routing](language-routing.md).
