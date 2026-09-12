# Quick start

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
