# Voice configuration

`VoiceConfig` loads a Piper `.onnx.json` file or validates an in-memory mapping. The high-level `config=` argument accepts a path, an existing `VoiceConfig`, or a mapping:

```python
from piperg2p import VoiceConfig

voice = VoiceConfig.from_json("voice.onnx.json")
from_mapping = VoiceConfig.from_dict(voice.to_dict())
```

Strict parsing is the default and requires `num_symbols`, `num_speakers`, `audio.sample_rate`, and a non-empty `phoneme_id_map`. Use `strict=False` only for compatibility with legacy configurations; inferred values produce a compatibility warning.

The configured `phoneme_type` controls the pronunciation frontend. `text` and `espeak` are implemented; recognized-but-unavailable values and profile restrictions are listed under [current phoneme-type support](phoneme-types.md).

## Voice versus language

The Piper voice configuration remains authoritative for the model's phoneme type, `phoneme_id_map`, and base eSpeak voice. For eSpeak profiles, `espeak.voice` in the config selects that base voice. The high-level `language` passed to `PiperG2P` or `get_g2p()` is a source/routing label; it does not select a different Piper model or automatically replace `espeak.voice`. An explicit language-span route may request a different eSpeak voice for that span.

ID values are normalized to immutable integer tuples and must be non-negative and below `num_symbols`. Voice maps are never replaced by a universal vocabulary. Vowel clusters must have at least two elements and their merged token must be present in the map.
