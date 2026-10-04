# Low-level frontend API

`PiperFrontend` is the lower-level voice-config-driven frontend. Most applications should start with the sibling-style facade documented on the [high-level API page](high-level.md); use this class when you need direct backend, encoder, or lexicon adapter control.

Autodoc renders the constructor and public methods from the current implementation, avoiding a manually copied signature:

```{autoclass} piperg2p.PiperFrontend
:members: from_config, encode, phonemize_prepared, phonemize, close
:special-members: __init__
:show-inheritance:
```

`PiperFrontend.phonemize()` aliases its low-level `phonemize_prepared()` and returns a `PhonemizeResult` (unlike `PiperG2P.phonemize()`, which returns `str`). The frontend accepts a validated `VoiceConfig`; `from_config()` loads a JSON path. Runtime lexicon selection is optional, mutually exclusive between managed identifiers and an injected backend, and supported only for `phoneme_type="espeak"`. The voice's `phoneme_id_map` remains authoritative.

See the [configuration reference](config.md), [result types](types.md), and [backend guide](backends.md) for details.
