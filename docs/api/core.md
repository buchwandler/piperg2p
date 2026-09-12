# Core API

Public entry points include `PiperFrontend`, `VoiceConfig`, `PhonemeType`, `encode_phonemes`, `MissingPhonemePolicy`, `PhonemizeResult`, `PhonemeSentence`, and `EncodeResult`.

Frontend results are immutable tuples. `PhonemizeResult.sentences` is the model-oriented view. The flattened `.phonemes` and `.ids` properties are convenience views.
