# Provenance and independence boundary

PiperG2P is independently implemented under Apache-2.0. Its compatibility requirements are based on public Piper configuration/behavior observations, the public eSpeak NG API, and documented optional adapter contracts. This page records the engineering provenance concisely; it is not a claim that the intentional `espeakng-runtime` dependency is absent.

| Requirement                 | Public or behavioral basis                | Independent implementation decision                                                             |
| --------------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Voice-specific ID maps      | Piper voice configuration                 | Keep the loaded map authoritative and validate IDs locally.                                     |
| BOS/PAD/EOS framing         | Observed frontend behavior                | Implement a small codec strategy without a universal map.                                       |
| NFD normalization           | Compatibility requirement                 | Use Python `unicodedata` at the frontend boundary.                                              |
| Clause terminators          | eSpeak NG public API and runtime contract | Use the `espeakng-runtime` public clause API and convert results at the Piper adapter boundary. |
| Native global-state locking | eSpeak public API behavior                | Delegate process-wide locking and lifetime to `espeakng-runtime`.                               |
| Raw blocks                  | Observed Piper/eSpeak behavior            | Use an independent state-machine parser and composition helper.                                 |
| CLI fallback                | Existing frontend behavior                | Delegate CLI execution to `espeakng-runtime`, retaining Piper-local splitting and composition.  |
| Lexphon managed assets      | Lexphon public data/profile APIs          | Keep installation and verification external; interpret assets in the optional adapter.          |
| G2Lex local assets          | G2Lex public open/lookup APIs             | Keep direct lookup narrow, ordered, and exact-key.                                              |
| Sibling architecture        | Public API conventions                    | Reuse lifecycle ideas without copying source or tests.                                          |

Built-in lexicon adapters preserve `phoneme_encoding`, lexicon ID, data version, producer, transform, and generator identity. Generic `ipa` is an override; `espeak-ipa3` represents Piper raw pronunciation content.

The PiperG2P package does not import the Piper runtime/package or bundle Piper source, tests, lookup tables, models, or resources. `espeakng-runtime` is an intentional runtime dependency for eSpeak infrastructure. Pinned upstream identity in benchmark metadata is historical evidence, not code to port.

eSpeak-derived test assets are generated during tests from declared source words and pronunciations. Production dictionaries are not bundled for test convenience.
