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

The normal runtime package does not depend on Piper. Reference dependencies and expected outputs are development and CI evidence only.
