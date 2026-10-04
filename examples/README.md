# PiperG2P examples

These executable examples keep the sibling-project filenames while demonstrating PiperG2P's voice-config-driven API. Each script supports `--help`; examples never download voices, models, catalogs, or lexicons.

| Example                      | What it demonstrates                                                  | Requirements                                                      |
| ---------------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `new_api_demo.py`            | Basic structured `phonemize_prepared()` call                          | Voice config                                                      |
| `result_inspection.py`       | Result, tokens, sentences, IDs, and reverse-ID inspection             | Voice config                                                      |
| `cache_and_batch.py`         | Bounded `get_g2p()` cache reuse and repeated calls                    | Voice config                                                      |
| `debug_mode_demo.py`         | Backend diagnostics and result metadata (there is no debug-mode flag) | Voice config                                                      |
| `demo_both_features.py`      | Prepared result plus explicit source-span language override           | eSpeak voice config                                               |
| `explicit_language_spans.py` | Caller-selected eSpeak voice for a source span                        | eSpeak voice config                                               |
| `external_annotations.py`    | Source-aligned caller POS, tag, lemma, and morphology                 | Voice config                                                      |
| `marker_demo.py`             | Marker ranges converted to ordinary overrides                         | eSpeak voice config                                               |
| `mixed_language_auto.py`     | Conservative auto routing from deterministic in-memory evidence       | eSpeak recommended; text config can inspect route metadata        |
| `structured_stress.py`       | Stress applied to an explicit phoneme override                        | Voice map compatible with the supplied/selected IPA symbols       |
| `espeak_fallback.py`         | Lexicon miss routed to PiperG2P's eSpeak backend                      | eSpeak voice config, `piperg2p[lexphon]`, installed Lexphon asset |
| `lexicon_selection.py`       | Inspect installed pronunciation assets by language                    | `piperg2p[lexphon]`; no voice config                              |

## Run an example

```bash
python examples/result_inspection.py \
  --config /path/to/voice.onnx.json \
  --language en-us \
  --espeak-mode auto
```

The mode option is `auto`, `native`, or `cli`; it applies to eSpeak-backed voice configurations. `language` is a source/routing label and does not select the Piper model or configured base voice.

Lexicon discovery does not need a voice config:

```bash
python -m pip install "piperg2p[lexphon]"
python examples/lexicon_selection.py --language de-de
```

Provision assets separately using the [lexicon guide](../docs/lexicons.md). The fallback example requires an already-installed identifier and never downloads it:

```bash
python examples/espeak_fallback.py \
  --config /path/to/espeak-voice.onnx.json \
  --language de-de \
  --lexicon <installed-lexicon-id> \
  --text "Prepared text to phonemize"
```

Examples do not download voices, models, or lexicons. Lexphon examples expect any required assets to be provisioned beforehand; eSpeak examples use the system runtime or explicitly selected extra. The Piper voice's `phoneme_id_map` is always authoritative, and sentence IDs are the normal Piper inference units.
