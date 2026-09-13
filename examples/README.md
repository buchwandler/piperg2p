# PiperG2P examples

Each example requires an explicit Piper voice configuration:

```bash
python examples/result_inspection.py --config /path/to/voice.onnx.json
```

The examples use only PiperG2P and locally provisioned resources. They never download
voices, models, or lexicons. Lexicon examples require installed Lexphon assets. The
benchmark examples and live eSpeak checks are documented under `docs/espeak.md`.

Files mirror the sibling KokoroG2P example inventory while using Piper's explicit
voice configuration and sentence-oriented result objects.
