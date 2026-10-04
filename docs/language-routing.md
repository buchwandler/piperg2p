# Language routing

`language` passed to `PiperG2P` or `get_g2p()` is the default source/routing language. The Piper config independently selects the model, phoneme type, ID map, and base `espeak.voice`. Routing can select an eSpeak voice for one span; it never changes the configured Piper model or base voice.

Meaningful language-specific pronunciation routing requires an eSpeak-backed voice. A `text` voice maps normalized text characters and does not provide language-specific pronunciation.

## Explicit spans

For a caller-known language span, use an ordinary `OverrideSpan` with a `lang` attribute. The range uses half-open `[start, end)` offsets in the exact prepared source text:

```python
from piperg2p import OverrideSpan, get_g2p

text = "Hello Welt"
with get_g2p("en-us", config="voice.onnx.json") as g2p:
    result = g2p.phonemize_prepared(
        text,
        overrides=[OverrideSpan(6, 10, {"lang": "de-de"})],
    )
```

An explicit choice is evidence supplied by the caller. `LanguageRoutingConfig(mode="explicit")` does not infer additional languages; use explicit override spans for the known source ranges. See [overrides](overrides.md).

## Conservative automatic routing

`LanguageRoutingConfig(mode="auto")` considers only configured candidate languages and switches away from the default only when exactly one candidate has evidence for a token. A per-language mapping whose keys are known words can supply deterministic in-memory evidence; the stored values are not interpreted:

```python
from piperg2p import LanguageRoutingConfig, get_g2p

routing = LanguageRoutingConfig(
    mode="auto",
    languages=("en-us", "de-de"),
    lexicons={"de-de": {"Welt": True}},
)
with get_g2p("en-us", config="voice.onnx.json") as g2p:
    result = g2p.phonemize_prepared("Hello Welt", language_routing=routing)
    for route in result.language_routes:
        print(route.language, route.reason, route.evidence)
```

This illustrates policy only; production routing should use evidence appropriate to the application. A route selected from evidence has reason `"lexicon-evidence"`. Unknown words stay on the default language (`"default-language"`); if multiple candidates match, ambiguous words also stay on the default (`"ambiguous-lexicon-evidence"`). Auto routing is evidence-driven, not language identification.

The current runtime accepts per-language evidence sources implemented as word-key mappings, objects with `lookup(word)`, or callables. The dataclass's `lexicons` type annotation is narrower than those runtime forms; this documentation task records the observed behavior without changing routing semantics. This lightweight evidence interface is not a managed Lexphon adapter. See [lexicons](lexicons.md) for asset provisioning.

For an executable offline routing example, see [`mixed_language_auto.py`](https://github.com/buchwandler/piperg2p/blob/main/examples/mixed_language_auto.py); for source-aligned explicit routing, see [`explicit_language_spans.py`](https://github.com/buchwandler/piperg2p/blob/main/examples/explicit_language_spans.py).
