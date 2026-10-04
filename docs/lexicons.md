# Pronunciation lexicons

PiperG2P can optionally overlay lexicon pronunciations on an eSpeak voice. Raw `[[ ... ]]` blocks take precedence, then configured lexicons are consulted, and unresolved source intervals are sent to PiperG2P's own eSpeak backend. PiperG2P owns fallback policy; Lexphon performs lexicon-only lookup.

> **No implicit downloads:** PiperG2P never downloads lexicon data. Provision and verify assets explicitly before runtime selection.

## Provision managed Lexphon assets

Install the optional adapter and use Lexphon's data commands to inspect and provision assets:

```bash
python -m pip install "piperg2p[lexphon]"
lexphon data available de-DE
lexphon data install <lexicon-id>
lexphon data verify <lexicon-id>
```

Inspect what is locally installed before choosing an identifier:

```python
from piperg2p import available_lexicons, lexicon_info

for name in available_lexicons("de-DE"):
    print(name, lexicon_info("de-DE", name))
```

Select an installed asset by its actual identifier:

```python
from piperg2p import get_g2p

with get_g2p(
    "de-de",
    config="voice.onnx.json",
    lexicons=("<installed-lexicon-id>",),
) as g2p:
    result = g2p.phonemize_prepared("Guten Tag")
```

The placeholder is not a promise that any particular identifier is published. Keep provisioning separate from runtime startup.

## Lookup and fallback behavior

Lexicon lookup is lexicon-only. A miss is passed to PiperG2P's eSpeak backend, not to Lexphon's generic eSpeak provider. Disable that fallback with `use_espeak_fallback=False` when a miss should remain explicit. Final IDs always use the configured voice map and its missing-symbol policy.

Generic `ipa` pronunciations are normalized as generic IPA overrides. `espeak-ipa3` pronunciations are retained as Piper raw phoneme content. A lexicon hit that contains a symbol absent from the voice map is not silently replaced by eSpeak. Lexicon-first output is an intentional extension, not an unqualified exact-upstream-parity claim.

Precedence is:

1. Explicit `[[ raw phonemes ]]` blocks.
2. Configured lexicons, in order.
3. PiperG2P eSpeak fallback for unresolved source intervals, unless disabled.
4. The voice's missing-symbol policy during ID encoding.

`result.diagnostics.lexicon` reports overlay implementation, language, identifiers, encodings, asset provenance, and compatibility label. Lookup/resource failures are errors, not normal misses. Optional packages are imported only when the corresponding adapter is selected.

## Direct local G2Lex files

For local development with explicit `.g2lex` files, install the separate extra and use the G2Lex adapter directly:

```bash
python -m pip install "piperg2p[g2lex]"
```

```python
from piperg2p import PiperFrontend
from piperg2p.lexicons import G2LexLookup

lookup = G2LexLookup(["./build/custom.g2lex"], language="de-DE")
frontend = PiperFrontend.from_config(
    "voice.onnx.json",
    lexicon_backend=lookup,
)
```

This is a separate local-development path; the injected adapter is caller-owned. Built-in adapters read `phoneme_encoding` metadata, accept generic IPA and `espeak-ipa3`, and reject unsupported kinds, languages, or encodings.

`g2p.lexicon_evidence(word, tag=...)` can expose provenance for a selected hit. Mixed lexicon/eSpeak sentences may differ from pure eSpeak because selected source spans are intentionally processed independently.
