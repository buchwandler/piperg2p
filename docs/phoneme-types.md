# Phoneme types

`phoneme_type` is a string-compatible enum in the Piper voice configuration. The current support boundary is:

| Type/profile | Current support                               |
| ------------ | --------------------------------------------- |
| `text`       | Implemented in core                           |
| `espeak`     | Implemented through native and CLI backends   |
| `pinyin`     | Recognized but unavailable without a provider |
| `japanese`   | Recognized but unavailable without a provider |
| `thai`       | Recognized but unavailable without a provider |
| `hebrew`     | Recognized but unavailable without a provider |

Selecting an unavailable type without a custom backend raises `UnsupportedPhonemeTypeError`. Arabic is not another `PhonemeType` enum member: it is an eSpeak profile restriction that raises `UnsupportedCompatibilityError` until Piper-compatible preprocessing is implemented. Optional language dependencies are not imported by the core package.

See [voice configuration](voice-config.md) and the [compatibility guide](compatibility.md) for the relationship between configured voices and supported backend capabilities.
