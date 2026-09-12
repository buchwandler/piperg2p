# Installation

The core package supports Python 3.10 and newer and has no mandatory non-standard runtime dependency.

```bash
pip install .
```

The `dev` extra provides pytest, coverage, ruff, mypy, and build tooling. eSpeak NG is a system dependency for eSpeak voices. Its executable, shared library, and data directory can be selected with constructor arguments or `PIPERG2P_ESPEAK_EXECUTABLE`, `PIPERG2P_ESPEAK_LIBRARY`, and `PIPERG2P_ESPEAK_DATA`.

No frontend downloads models or makes network requests during phonemization.
