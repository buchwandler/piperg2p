# Result and span types

PiperG2P returns structured phonemization results and sentence-scoped model IDs. Source offsets throughout this API use half-open character ranges `[start, end)` into the exact input text.

## `PhonemizeResult`

The high-level result contains:

- `clean_text`: source text after the facade's preparation boundary (PiperG2P does not perform semantic verbalization).
- `tokens`: source-aligned `TokenSpan` entries.
- `extended_text`: current extended text view; for PiperG2P it is the prepared source text.
- `phonemes`: flattened phoneme-string convenience view.
- `token_ids`: flattened ID list convenience view.
- `warnings`: phonemization/encoding warning messages.
- `language_routes`: routing decisions, when routing is requested.
- `sentences`: authoritative sentence-level phonemes and IDs.
- `diagnostics`: frontend/backend and optional lexicon diagnostics.
- `missing_phonemes`: absent symbols recorded during encoding.
- `ids`: tuple convenience view of `token_ids`.
- `phoneme_symbols`: tuple of characters from the flattened `phonemes` string; use sentence phoneme data when symbol grouping matters.

Do not use the flattened `token_ids`/`ids` as the normal model-inference unit. Process each `sentence.ids` independently.

```{autoclass} piperg2p.PhonemizeResult
:members: text, ids, phoneme_symbols
:show-inheritance:
```

## `PhonemeSentence`

Each sentence records `phonemes`, `phoneme_string` (the joined string view), `ids`, `missing_phonemes`, and `warnings`. Its `metadata` field is a tuple of extra key/value pairs. Piper model inference should normally receive each sentence's `ids` separately.

```{autoclass} piperg2p.PhonemeSentence
:members: phoneme_string
:show-inheritance:
```

## Source spans and caller annotations

`TokenSpan` preserves the original token text, half-open `char_start`/`char_end` offsets (also available as `start`/`end`), optional `lang`, `extended_text`, and caller metadata. `TokenAnnotation` records source-aligned optional `text`, `pos`, `tag`, `lemma`, `language`, and `morph` fields.

```{autoclass} piperg2p.TokenSpan
:members: start, end
:show-inheritance:
```

```{autoclass} piperg2p.TokenAnnotation
:members: char_start, char_end
:show-inheritance:
```

`OverrideSpan` contains `char_start`, `char_end`, and immutable `attrs`; its `start` and `end` properties are aliases. Common attributes are `ph` for explicit phoneme content, `lang` for an eSpeak voice override, and `stress` for structured stress after pronunciation resolution. See [overrides](../overrides.md).

```{autoclass} piperg2p.OverrideSpan
:members: start, end
:show-inheritance:
```

## Routing types

`LanguageRoute` records a half-open source span, selected `language`, optional `requested_language`, decision `reason`, and evidence. `LanguageRoutingConfig` accepts `mode="explicit"` or `mode="auto"`; automatic routing changes the default only on unambiguous configured evidence. Explicit spans are supplied by the caller as overrides.

```{autoclass} piperg2p.LanguageRoute
:members:
:show-inheritance:
```

```{autoclass} piperg2p.LanguageRoutingConfig
:members:
:show-inheritance:
```

The runtime currently accepts per-language evidence mappings, lookup-capable objects, or callables even though `LanguageRoutingConfig.lexicons` is annotated more narrowly. This reference records behavior without changing that contract. See [language routing](../language-routing.md).
