# Raw phonemes

In eSpeak mode, `[[ ... ]]` blocks are parsed before normal conversion. Their contents are inserted as phoneme characters and are not normalized or sent through eSpeak. Adjacent normal text is composed into the active sentence so a normal sentence immediately following a raw block joins that active group.

## Semantic preparation and raw blocks

PiperG2P owns raw blocks such as `[[ tɛst ]]`. Spokenform must not reinterpret text inside those blocks. Discover Piper raw blocks before semantic preparation and pass their source ranges to Spokenform as protected spans:

```python
from piperg2p import (
    RawPhonemeSegment,
    parse_raw_blocks,
    phonemize_prepared,
)
from spokenform import ProtectedSpan, prepare_for_piperg2p

source = "Use 2 kg [[ tɛst ]] and 3 kg."

protected = [
    ProtectedSpan(
        segment.source_start,
        segment.source_end,
        kind="piperg2p-raw-phonemes",
    )
    for segment in parse_raw_blocks(source)
    if isinstance(segment, RawPhonemeSegment)
]

prepared = prepare_for_piperg2p(
    source,
    language="en",
    protected_spans=protected,
)

result = phonemize_prepared(
    prepared.spoken_text,
    language="en-us",
    config="voice.onnx.json",
)
```

Discover Piper raw blocks before semantic preparation and pass their source ranges to Spokenform as protected spans. This keeps caller-owned raw phonemes unchanged while surrounding written semantics can be expanded.

If an application also has source-coordinate overrides, map those source spans through `PreparedText.map_source_span()` before constructing overrides for the prepared text. Do not reuse token or POS metadata from the source text across a semantic replacement without reanalyzing the prepared text.
Opening and closing delimiters without a matching pair are deterministic ordinary text. Empty blocks do not add symbols. Raw symbols still pass through the configured voice map and therefore appear in missing-phoneme diagnostics when unmapped.
