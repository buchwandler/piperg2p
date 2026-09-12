# Phoneme types

The configuration enum recognizes the six current Piper phoneme type names:

| Type                | Phase 1 status                                        |
| ------------------- | ----------------------------------------------------- |
| `text`              | implemented in core                                   |
| `espeak`            | native and CLI backends implemented                   |
| `pinyin`            | recognized configuration value, unavailable           |
| `japanese`          | recognized configuration value, unavailable           |
| `thai`              | recognized configuration value, unavailable           |
| `hebrew`            | recognized configuration value, unavailable           |
| Arabic eSpeak voice | explicitly blocked until preprocessing is implemented |

Selecting a deferred type without a custom backend raises an actionable `UnsupportedPhonemeTypeError`. Arabic eSpeak profiles raise `UnsupportedCompatibilityError`. Optional language dependencies are not imported by the core package.
