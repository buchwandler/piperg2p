# Overrides, annotations, markers, and stress

Overrides let a caller provide source-aligned pronunciation or language metadata without adding an NLP dependency. Span offsets address the exact prepared text passed to `phonemize_prepared()` and use half-open `[start, end)` character ranges.

## Direct phoneme and language overrides

Use `OverrideSpan(start, end, attrs)` for a direct phoneme override (`ph`) or to route a span through another eSpeak voice (`lang`):

```python
from piperg2p import OverrideSpan, get_g2p

text = "Hello Welt"
with get_g2p("en-us", config="voice.onnx.json") as g2p:
    result = g2p.phonemize_prepared(
        text,
        overrides=[OverrideSpan(6, 10, {"lang": "de-de"})],
    )
```

`ph` supplies the resolved phoneme content for that source range; its symbols must still exist in the configured voice's `phoneme_id_map`. A `lang` override asks the eSpeak backend to pronounce the span with that voice. It does not change the Piper model or the voice configuration's base `espeak.voice`.

Overlaps and token boundaries are controlled by `overlap`:

- `"snap"` expands partial boundaries to token edges and reports a warning.
- `"strict"` skips a range that partially overlaps a token; overlapping override ranges are also rejected/skipped with a warning.
- `"split"` preserves the exact character boundaries, allowing a token to be split across ordinary and overridden segments.

Overlapping ranges are not generally composable; avoid them. For `ph` plus `stress`, stress is applied after pronunciation resolution. Valid stress levels are `-2`, `-1`, `1`, and `2`; a compatible vowel-bearing phoneme string must be used and every resulting symbol must be supported by the voice map. See the executable [`structured_stress.py`](https://github.com/buchwandler/piperg2p/blob/main/examples/structured_stress.py) example for a compatible-voice demonstration.

## Caller-supplied annotations

`TokenAnnotation` carries caller-supplied metadata over a source range. It accepts `pos`, `tag`, `lemma`, `language`, and `morph`; the values are attached to covered output tokens so the caller's existing linguistic metadata remains available. PiperG2P preserves this supplied information but does not run spaCy or automatically add an NLP dependency.

```python
from piperg2p import TokenAnnotation, get_g2p

with get_g2p("en-us", config="voice.onnx.json") as g2p:
    result = g2p.phonemize_prepared(
        "Hello world",
        annotations=[TokenAnnotation(0, 5, text="Hello", pos="INTJ", tag="UH",
                                     lemma="hello", morph="Number=Sing")],
    )
```

When `text` is supplied on an annotation, it must match the covered source slice. Offsets must align with the current text.

## Marker parsing

Marker helpers separate identifying source ranges from assigning behavior:

1. `parse_delimited()` removes paired markers and returns clean text, clean-text ranges, and parser warnings.
2. `apply_marker_overrides()` converts those ranges and caller assignments to ordinary `OverrideSpan` objects.

```python
from piperg2p import apply_marker_overrides, parse_delimited

clean, ranges, marker_warnings = parse_delimited("Say @hello@ today")
overrides = apply_marker_overrides(clean, ranges, {1: {"lang": "en-us"}})
```

Ranges are in the returned clean-text coordinate space, not the original marked string. Unmatched markers are restored as literal text with a warning. Escape the marker or escape character with the helper's escape prefix. Keep parser warnings distinct from phonemization warnings when reporting diagnostics. See [`marker_demo.py`](https://github.com/buchwandler/piperg2p/blob/main/examples/marker_demo.py).

## Source alignment after transformations

Semantic rewriting can insert, remove, or reorder characters and thereby invalidate spans and annotations. Build spans against the final text that PiperG2P will consume, or explicitly remap them after each transformation. See [prepared-text ownership](prepared-text.md) for the boundary and [language routing](language-routing.md) for explicit/automatic language choices.
