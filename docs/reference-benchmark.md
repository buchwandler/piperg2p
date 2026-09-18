# Reference benchmark

`benchmarks/data/core.json` records the pinned Piper Python 1.8.0 profile, commit, and minimum compatibility corpus. It covers text normalization, punctuation, sentence boundaries, language switches, raw blocks, vowel clusters, missing symbols, IPA3 overlay hits and misses, mixed sentences, tie or joiner behavior, and the Arabic policy.

Inspect the corpus metadata without executing a voice configuration:

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

The command records Piper commit and version, Python and platform information, dependency versions, voice configuration hash, and overlay asset identity. A missing or mismatched expected file exits nonzero. Expected output is never created or changed during normal execution. Replacing it requires the explicit `--write-expected --expected PATH` command and subsequent human review.

## eSpeak IPA3 primary benchmark

`eSpeak --ipa=3` is the pronunciation gold standard. The direct benchmark has separate core, sentence, composition, lexicon-overlay, and parity suites and reports exact matches plus symbol substitutions, insertions, deletions, edit distance, and error rate.

The parity suite (`--suite parity`) covers weak words, contractions, and phrase-context contrasts to detect stress and pronunciation differences between native and CLI modes. When Phonodist is available (`--phonodist auto` or `--phonodist required`), the benchmark also reports phonetic classification counts (exact, notation_only, stress_only, segmental) to explain structural differences.

Quick live check:

```bash
python benchmarks/benchmark_espeak.py --quick --suite core --candidate auto --format summary
```

Parity suite with Phonodist diagnostics:

```bash
python benchmarks/benchmark_espeak.py --suite parity --candidate auto --reference-source golden --golden benchmarks/goldens/espeak_ipa3_en-us.json --policy piper-ipa3 --phonodist auto --format summary
```

Use `--reference-source live` for the installed executable or `--reference-source golden --golden PATH` for a committed capture. Golden refresh requires `--write-reference-golden --overwrite` and is never implicit. The pinned `benchmark_reference.py` remains secondary evidence for Piper-specific composition and historical compatibility, not the pronunciation oracle.
The normal runtime package does not depend on Piper. Reference dependencies and expected outputs are development and CI evidence only.
