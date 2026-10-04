# High-level API

The sibling-style API is the recommended application-facing layer. It accepts prepared text plus an explicit source/routing language and Piper voice configuration. The `config` selects the model profile and its voice-specific `phoneme_id_map`; `language` does not replace that voice or its base `espeak.voice`.

## Reusable facade

`PiperG2P` exposes both plain-string and structured-result methods. Its compatibility parameters for spaCy/Goruut do not activate those integrations: unsupported non-default values raise `UnsupportedCompatibilityError`.

```{autoclass} piperg2p.PiperG2P
:members: phonemize, phonemize_prepared, lexicon_evidence, close
:special-members: __init__
:show-inheritance:
```

`get_g2p()` constructs a reusable facade and uses a bounded cache when no custom lexicon backend/store is injected. Repeated calls with the same cache identity may return the same object. The context-manager protocol closes the facade; `clear_cache()` closes cached values.

```{autofunction} piperg2p.get_g2p

```

## One-shot phonemization and IDs

```{autofunction} piperg2p.phonemize_prepared

```

Module-level `phonemize()` is an alias of `phonemize_prepared()` and returns `PhonemizeResult`. The compatibility parameters `return_ids` and `return_phonemes` are currently accepted but are no-ops; they do not alter the return type or omit fields.

```{autofunction} piperg2p.phonemize

```

```{autofunction} piperg2p.phonemes

```

```{autofunction} piperg2p.phoneme_ids

```

| Call                                                | Return value      |
| --------------------------------------------------- | ----------------- |
| `PiperG2P.phonemize(text)`                          | `str`             |
| `PiperG2P.phonemize_prepared(text, ...)`            | `PhonemizeResult` |
| Module `phonemize_prepared(...)` / `phonemize(...)` | `PhonemizeResult` |
| Module `phonemes(...)`                              | `str`             |
| Module `phoneme_ids(...)`                           | `list[int]`       |

Use the `sentence.ids` sequences as the normal Piper inference units; the flattened result IDs are convenience views. See [result types](types.md).

## Tokenization, cache, markers, and lexicon discovery

```{autofunction} piperg2p.tokenize

```

```{autofunction} piperg2p.cache_info

```

```{autofunction} piperg2p.clear_cache

```

```{autofunction} piperg2p.parse_delimited

```

```{autofunction} piperg2p.apply_marker_overrides

```

```{autofunction} piperg2p.available_lexicons

```

```{autofunction} piperg2p.lexicon_info

```

Use `ids_to_phonemes()` for diagnostic/reverse inspection, not as a guaranteed lossless inverse: multiple phoneme symbols can share IDs or make a sequence ambiguous. See the [usage guide](../usage.md), [overrides](../overrides.md), and [lexicon guide](../lexicons.md).

```{autofunction} piperg2p.ids_to_phonemes

```
