# piperg2p documentation

- [Installation](installation.md)
- [Quick start](quickstart.md)
- [Voice configuration](voice-config.md)
- [Encoding](encoding.md)
- [eSpeak backends](espeak.md)
- [Pronunciation lexicons](lexicons.md)
- [Core API](api/core.md)
- [Backend API](api/backends.md)
- [Raw phonemes](raw-phonemes.md)
- [Phoneme types](phoneme-types.md)
- [Compatibility policy](compatibility.md)
- [Provenance](provenance.md)

The project is an independent phoneme and ID frontend. It accepts prepared, speakable text and does not synthesize audio or own written-to-spoken semantic normalization.

Applications that need number, unit, currency, date, abbreviation, or other semantic expansion may prepare text with a separate package such as Spokenform before calling `phonemize_prepared()`. Spokenform is not a PiperG2P dependency.
