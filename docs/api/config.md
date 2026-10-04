# Configuration API

`VoiceConfig` is the validated, immutable view of the Piper `.onnx.json` fields used by PiperG2P. `PiperConfig` is a compatibility alias. High-level `config=` arguments accept a path, mapping, or existing `VoiceConfig`; the lower-level frontend expects a `VoiceConfig` or path via `from_config()`.

Strict parsing is the default. `strict=False` is a compatibility mode for legacy inputs that can infer supported defaults and emit `CompatibilityWarning`; it does not make unsupported phoneme providers available.

```{autoclass} piperg2p.VoiceConfig
:members: from_dict, from_json, to_dict, noise_w_scale
:show-inheritance:
```

```{autoclass} piperg2p.PhonemeType
:members:
:show-inheritance:
```

For the supported/unavailable distinction and the base eSpeak voice versus routing language, see [phoneme types](../phoneme-types.md) and [voice configuration](../voice-config.md).
