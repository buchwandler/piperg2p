# Reference benchmark

## Which benchmark should I use?

- `benchmark_espeak.py` is the pronunciation oracle: it compares PiperG2P output with eSpeak IPA3.
- `benchmark_reference.py` records Piper-specific composition and historical compatibility evidence against a pinned Piper profile.

## Piper compatibility corpus

`benchmarks/data/core.json` records the pinned Piper Python 1.8.0 profile, commit, and compatibility corpus. It covers text normalization, punctuation, sentence boundaries, language switches, raw blocks, vowel clusters, missing symbols, IPA3 overlay hits and misses, mixed sentences, tie or joiner behavior, and the Arabic policy.

Inspect corpus metadata without executing a voice configuration:

```bash
python benchmarks/benchmark_reference.py
```

Execute PiperG2P with a voice configuration and write a reproducible report:

```bash
python benchmarks/benchmark_reference.py \
  --config voice.onnx.json \
  --output report.json
```

Reference Piper execution belongs in a separate pinned development environment. Its reviewed output can be compared with:

```bash
python benchmarks/benchmark_reference.py \
  --config voice.onnx.json \
  --expected benchmarks/data/core.expected.json
```

The command records Piper commit/version, Python and platform information, dependency versions, voice configuration hash, and overlay asset identity. A missing or mismatched expected file exits nonzero. Expected output is never created or changed during normal execution; refreshing it requires `--write-expected --expected PATH` and human review.

## eSpeak IPA3 pronunciation benchmark

`benchmark_espeak.py` invokes the external executable directly with `-q --ipa=3 -v <voice> --stdin`; the reference does not call PiperG2P's backend or `espeakng-runtime`. The benchmark has core, sentence, composition, lexicon-overlay, and parity suites and reports exact matches, substitutions, insertions, deletions, edit distance, and error rate.

The parity suite (`--suite parity`) covers weak words, contractions, and phrase-context contrasts between native and CLI modes. When Phonodist is available, it can report phonetic classification counts (exact, notation_only, stress_only, segmental).

Quick live check:

```bash
python benchmarks/benchmark_espeak.py --quick --suite core --candidate auto --format summary
```

See the [eSpeak guide](espeak.md) for backend semantics. Golden reference refresh requires explicit `--write-reference-golden --overwrite`; it is never implicit. Reference dependencies and expected outputs are development evidence only and are not runtime dependencies.
