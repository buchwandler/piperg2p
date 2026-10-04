# Encoding

Ordinary encoding uses the configured voice map and preserves Piper's framing:

```text
BOS, PAD, (phoneme IDs, PAD)*, EOS
```

A map value may contain multiple IDs. The loaded voice's `phoneme_id_map` is authoritative; there is no universal symbol vocabulary. `PhonemizeResult.token_ids` is a flattened convenience view. For Piper inference, use each sentence's IDs separately.

## Missing symbols

A produced phoneme absent from the configured map is recorded in `EncodeResult` and sentence/result data. The `missing` policy controls whether processing stops, warns, or continues silently:

```python
from piperg2p import MissingPhonemePolicy, phonemize_prepared

result = phonemize_prepared(
    "Hello world",
    language="en-us",
    config="voice.onnx.json",
    missing=MissingPhonemePolicy.WARN,
)
print(result.missing_phonemes)
```

| Policy                        | Behavior                                                  |
| ----------------------------- | --------------------------------------------------------- |
| `MissingPhonemePolicy.ERROR`  | Raise `MissingPhonemeError`                               |
| `MissingPhonemePolicy.WARN`   | Emit `MissingPhonemeWarning` and skip the unmapped symbol |
| `MissingPhonemePolicy.IGNORE` | Skip the unmapped symbol silently                         |

With `WARN` and `IGNORE`, the absent symbol remains recorded in result data even though encoding continues.
