# Encoding

Ordinary encoding uses the configured map and preserves this framing:

```text
BOS, PAD, (phoneme IDs, PAD)*, EOS
```

Map values may contain multiple IDs. Missing phonemes are always recorded in `EncodeResult` and sentence results. `MissingPhonemePolicy.ERROR` raises `MissingPhonemeError`, `WARN` emits `MissingPhonemeWarning` and skips the symbol, and `IGNORE` skips it silently.

A separate `PinyinEncoder` exists for future provider integration. It does not change ordinary `text` or `espeak` framing.
