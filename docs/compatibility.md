# Compatibility policy

PiperG2P compares behavior with the pinned Piper Python 1.8.0 reference commit `404aefedbd74baa0bd43e451bc407a2b3aace0f5`. `libpiper` is a separate compatibility profile and is not silently mixed into runtime behavior.

| Feature                        | Current support          | Compatibility label                             |
| ------------------------------ | ------------------------ | ----------------------------------------------- |
| Text frontend                  | Implemented              | Exact for the tested Python profile             |
| Native eSpeak clause API       | System library           | Exact when the public terminator API is present |
| eSpeak CLI                     | Executable required      | Best-effort                                     |
| Raw blocks                     | Implemented for eSpeak   | Reference-tested foundation                     |
| Pinyin, Japanese, Thai, Hebrew | Recognized config values | Unavailable without a provider                  |
| Arabic eSpeak profile          | Recognized voice profile | Unsupported until preprocessing is implemented  |
| Lexphon/G2Lex overlay          | Opt-in extension         | `override-generic-ipa` or `piper-espeak-frozen` |

The compatibility corpus at `benchmarks/data/core.json` records the pinned cases. It is not a golden output and cannot silently refresh. Exactness claims require reference output and dependency metadata. See the [eSpeak guide](espeak.md), [benchmark guide](reference-benchmark.md), and [provenance](provenance.md) for the underlying evidence.
