# Provenance and clean-room boundary

This project is implemented independently under Apache-2.0. The compatibility requirements were derived from public Piper configuration and behavior observations, the eSpeak NG public header/API, and the local `01_todo.md` engineering guide.

| Requirement | Public or black-box basis | Independent decision |
| --- | --- | --- |
| Voice-specific ID maps | Piper voice configuration shape | Keep the loaded map authoritative and validate IDs locally. |
| Ordinary BOS/PAD/EOS framing | Observed frontend behavior | Implement a small codec strategy with no universal map. |
| NFD normalization | Existing project behavior and compatibility requirement | Use Python `unicodedata.normalize` at the frontend boundary. |
| Clause terminators | eSpeak NG public `speak_lib.h` | Bind the exported terminator function with ctypes and transform results in pure Python. |
| Native global-state locking | eSpeak public API global behavior | Use one process-wide manager and reentrant lock. |
| Raw blocks | Observed eSpeak/Piper behavior | Use a small state-machine parser and independent composition helper. |
| CLI fallback | Existing project behavior | Keep subprocess execution isolated, UTF-8, no shell, and label parity best-effort. |

No Piper source, comments, tests, lookup tables, model files, bundled resources, or runtime import is used. The pinned upstream identity in the benchmark metadata is historical evidence, not code to port.
