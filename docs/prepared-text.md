# Prepared-text boundary

PiperG2P consumes prepared, speakable text. Its responsibility begins with the text that should be pronounced; it does not verbalize written numbers, units, currency amounts, dates, times, abbreviations, URLs, versions, or other domain-specific semantic forms.

Applications that need those forms expanded can compose PiperG2P with a separate semantic-preparation layer. Such a layer is an external integration, not a PiperG2P dependency. The following is an **external composition example**; the Spokenform package is not included in this repository snapshot, and this integration is not verified by PiperG2P's local test suite:

```python
# External composition example; install and validate the preparation layer separately.
from spokenform import prepare_for_piperg2p
from piperg2p import phonemize_prepared

prepared = prepare_for_piperg2p(
    "Pay $12.50 for 2 kg.",
    language="en",
).spoken_text

result = phonemize_prepared(
    prepared,
    language="en-us",
    config="voice.onnx.json",
)
```

The semantic-preparation language and PiperG2P's `language` are separate choices. The latter is a source/routing label; `config` selects the Piper voice. The configured JSON's `espeak.voice` supplies the base eSpeak voice. Changing the language label does not select a different Piper model or replace the base voice.

## Preserve Piper raw phoneme blocks

PiperG2P assigns special meaning to `[[ ... ]]` blocks. If an external text transformation runs first, protect those source ranges so the contents are not verbalized, normalized, or rewritten as ordinary prose. Restore the blocks before passing text to PiperG2P. See [raw phonemes](raw-phonemes.md) for Piper's delimiter rules and [overrides](overrides.md) for source-span operations.

## Source-coordinate overrides

Overrides and annotations use source offsets into the exact text being phonemized, with half-open `[start, end)` ranges. Any external transformation that inserts, deletes, or reorders text can invalidate those offsets. Compute or remap source coordinates after the transformation, against the final prepared string; do not reuse offsets from the original input unless the transformation guarantees alignment.

PiperG2P does not import or require Spokenform or Numeralform. Keep semantic preparation in the calling application and pass only the final speakable text to PiperG2P.
