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

`result.tokens` contains source offsets. `result.sentences` remains authoritative for sentence-wise Piper inference.
