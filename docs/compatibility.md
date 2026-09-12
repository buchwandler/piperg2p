# Compatibility policy

The primary target is the Piper Python voice behavior at the pinned Piper 1.8.0 reference commit `404aefedbd74baa0bd43e451bc407a2b3aace0f5`. `libpiper` behavior is a separate compatibility profile and is not silently mixed into the runtime.

| Feature | Core | Compatibility label |
| --- | --- | --- |
| Text frontend | yes | exact for tested Python profile |
| Native eSpeak clause API | system library | exact when the public terminator API is present |
| eSpeak CLI | executable required | best-effort |
| Raw blocks | yes, eSpeak only | reference-tested foundation |
| Pinyin, Japanese, Thai, Hebrew | recognized configuration values | unavailable, no provider |
| Arabic eSpeak | recognized voice profile | explicitly unsupported until preprocessing is implemented |
| Lexphon/G2Lex overlay | opt-in | `override-generic-ipa` or `piper-espeak-frozen` extension |

The pinned Phase 1 corpus metadata is in `benchmarks/data/core.json`. It is not a golden output and cannot silently refresh. Exactness claims require reference output and dependency metadata.
