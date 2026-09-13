# Quick start

The examples below pass prepared, speakable text. Semantic expansion belongs to the calling application, not PiperG2P.

```python
from piperg2p import PiperFrontend

with PiperFrontend.from_config("voice.onnx.json") as frontend:
    result = frontend.phonemize("Hello world.")
    for sentence in result.sentences:
        print(sentence.phoneme_string)
        print(sentence.ids)
```

For a text voice, `phonemize` decomposes input with Unicode NFD and treats each resulting codepoint as a model phoneme. For an eSpeak voice, it selects the configured eSpeak voice and returns one result per detected sentence.

Use `frontend.diagnostics` or `result.diagnostics` to inspect backend implementation and parity.

For sibling-style calls, use the explicit high-level facade:

```python
from piperg2p import phonemize_prepared

result = phonemize_prepared(
    "Hello world",
    language="en-us",
    config="voice.onnx.json",
)
print(result.phonemes)
print(result.token_ids)
```

## Prepare semantics outside the core

Semantic preparation belongs in the calling application when written forms need expansion:

```python
from spokenform import prepare_for_piperg2p
from piperg2p import phonemize_prepared

prepared = prepare_for_piperg2p(
    "Pay $12.50 for 2 kg.",
    language="en",
)

result = phonemize_prepared(
    prepared.spoken_text,
    language="en-us",
    config="voice.onnx.json",
)

print(result.phonemes)
```

The semantic language and Piper voice are separate choices. Spokenform prepares one explicitly selected language; PiperG2P then phonemizes the prepared text using the explicitly selected voice configuration.

The optional preparation package is not imported by PiperG2P and is not required for a minimal PiperG2P installation.

```text
Spokenform language: "en"
Piper voice/config:   "en-us" + voice.onnx.json
```

Do not imply that the Spokenform language selects a Piper voice.

`result.tokens` contains source offsets. `result.sentences` remains authoritative for sentence-wise Piper inference.
