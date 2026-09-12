# Compatibility policy

The primary target is the Python Piper voice behavior at pinned reference commits. `libpiper` behavior is a separate future benchmark profile and is not silently mixed into the runtime.

| Feature | Core | Compatibility label |
| --- | --- | --- |
| Text frontend | yes | exact for tested Python profile |
| Native eSpeak clause API | system library | exact when the public terminator API is present |
| eSpeak CLI | executable required | best-effort |
| Raw blocks | yes, eSpeak only | reference-tested foundation |
| Pinyin, Japanese, Thai, Hebrew, Arabic | no provider in Phase 1 | unsupported or deferred |
| Lexphon/G2Lex overlay | opt-in | override extension, not upstream exact parity |

The pinned Phase 1 corpus metadata is in `benchmarks/data/core.json`. It is not a golden output and cannot silently refresh. Exactness claims require reference output and dependency metadata.
