# Installation

The core package supports Python 3.10 and newer and has no mandatory non-standard runtime dependency.

```bash
pip install .
```

## Semantic preparation boundary

PiperG2P consumes prepared, speakable text. It does not depend on Numeralform
or Spokenform and does not own written-to-spoken semantic normalization.
Higher-level applications should perform that preparation before calling
PiperG2P.


## Optional semantic preparation

Spokenform is a separate package for applications that need written-to-spoken semantic expansion. Install it independently from PiperG2P:

```bash
python -m pip install spokenform
```

```python
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

Spokenform is not a PiperG2P core, optional-extra, development, or core-test dependency.
The `dev` extra provides pytest, coverage, ruff, mypy, and build tooling. eSpeak NG is a system dependency for eSpeak voices. Its executable, shared library, and data directory can be selected with constructor arguments or `PIPERG2P_ESPEAK_EXECUTABLE`, `PIPERG2P_ESPEAK_LIBRARY`, and `PIPERG2P_ESPEAK_DATA`.

No frontend downloads models or makes network requests during phonemization.

Optional lexicon adapters are installed separately:

```bash
pip install 'piperg2p[lexphon]'  # managed Lexphon identifiers
pip install 'piperg2p[g2lex]'     # explicit local .g2lex files
pip install 'piperg2p[espeak-direct]'  # packaged modern eSpeak loader
```

These packages are not imported or required for core/text/eSpeak-only use.
