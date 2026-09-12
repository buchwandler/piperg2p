# Voice configuration

`VoiceConfig.from_json` reads a Piper `.onnx.json` file. Strict parsing is the default and requires `num_symbols`, `num_speakers`, `audio.sample_rate`, and a non-empty `phoneme_id_map`.

```python
from piperg2p import VoiceConfig

config = VoiceConfig.from_json("voice.onnx.json")
config = VoiceConfig.from_dict(config.to_dict())
```

`phoneme_type` is a string-compatible `PhonemeType` enum with values `text`, `espeak`, `pinyin`, `hebrew`, `japanese`, and `thai`. This Phase 1 release implements `text` and `espeak`. `strict=False` is available for legacy configs and emits a compatibility warning when values are inferred.

ID values are normalized to immutable integer tuples. IDs must be non-negative and below `num_symbols`. Voice maps are never replaced by a universal vocabulary. Vowel clusters must have at least two elements and their merged token must be in the map.
