# Raw phonemes

In eSpeak mode, `[[ ... ]]` blocks are parsed before normal conversion. Their contents are inserted as phoneme characters and are not normalized or sent through eSpeak. Adjacent normal text is composed into the active sentence so a normal sentence immediately following a raw block joins that active group.

Opening and closing delimiters without a matching pair are deterministic ordinary text. Empty blocks do not add symbols. Raw symbols still pass through the configured voice map and therefore appear in missing-phoneme diagnostics when unmapped.
