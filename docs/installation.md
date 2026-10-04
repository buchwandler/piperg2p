# Installation

## Python requirement

PiperG2P supports Python 3.10 and newer.

## Install the package

```bash
python -m pip install piperg2p
```

The core package depends on `espeakng-runtime` for eSpeak infrastructure and `phrasplit` for sentence segmentation. It does not depend on Piper, Spokenform, or Numeralform.

## eSpeak runtime choices

Text voices do not invoke eSpeak. For eSpeak voices, `espeakng-runtime` discovers and manages the native library or CLI fallback. The `espeak-direct` extra enables its bundled-loader support where supported:

```bash
python -m pip install "piperg2p[espeak-direct]"
```

See [eSpeak modes and capability inspection](espeak.md) for backend behavior and configuration precedence.

## Optional extras

| Extra           | Purpose                                          |
| --------------- | ------------------------------------------------ |
| `lexphon`       | Managed installed pronunciation assets           |
| `lexicons`      | Alias-equivalent convenience extra for `lexphon` |
| `g2lex`         | Direct local `.g2lex` files                      |
| `espeak-direct` | Bundled `espeakng-runtime` loader support        |
| `reference`     | Reference/phonetic benchmark tooling             |
| `docs`          | Sphinx, MyST Parser, and RTD theme               |
| `dev`           | Tests, lint, type-check, and package build tools |

Lexicon data is provisioned separately and is never downloaded by PiperG2P at runtime. See [lexicon provisioning](lexicons.md).

## Termux / Android

Install the system eSpeak package and PiperG2P:

```bash
pkg install espeak
python -m pip install piperg2p
```

Do not use the desktop/server bundled loader merely to obtain eSpeak on Android. Use `inspect_espeak()` to see whether an exact-capable native library is available. `espeak_mode="auto"` selects native operation when the required capability is present and otherwise falls back to CLI. Capability discovery handles system package changes without relying on a hard-coded eSpeak version.

## Development and documentation

From a source checkout, install the development tools and run the checks:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

For documentation work, include the docs extra:

```bash
python -m pip install -e ".[dev,docs]"
python docs/make.py html
```

PiperG2P consumes prepared, speakable text rather than verbalizing written numbers, dates, units, and similar semantics. See the canonical [prepared-text guide](prepared-text.md) for that boundary and optional composition.
