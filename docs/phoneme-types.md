# Phoneme types

The configuration enum recognizes the six current Piper phoneme type names:

| Type | Phase 1 status |
| --- | --- |
| `text` | implemented in core |
| `espeak` | native and CLI backends implemented |
| `pinyin` | encoder scaffold only, provider deferred |
| `japanese` | deferred |
| `thai` | deferred |
| `hebrew` | deferred |

Selecting a deferred type without a custom backend raises an actionable `UnsupportedPhonemeTypeError`. Optional language dependencies are not imported by the core package.
