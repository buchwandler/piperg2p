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

The `dev` extra provides pytest, coverage, ruff, mypy, and build tooling. eSpeak NG is a system dependency for eSpeak voices. Its executable, shared library, and data directory can be selected with constructor arguments or `PIPERG2P_ESPEAK_EXECUTABLE`, `PIPERG2P_ESPEAK_LIBRARY`, and `PIPERG2P_ESPEAK_DATA`.

No frontend downloads models or makes network requests during phonemization.

Optional lexicon adapters are installed separately:

```bash
pip install 'piperg2p[lexphon]'  # managed Lexphon identifiers
pip install 'piperg2p[g2lex]'     # explicit local .g2lex files
pip install 'piperg2p[espeak-direct]'  # packaged modern eSpeak loader
```

These packages are not imported or required for core/text/eSpeak-only use.
