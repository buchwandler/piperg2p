# Backend API

The eSpeak adapter delegates discovery and execution to `espeakng-runtime` while retaining Piper-specific clause composition and phoneme policy. `auto`, `native`, and `cli` behavior and capability semantics are explained in the [eSpeak guide](../espeak.md).

```{autoclass} piperg2p.EspeakBackend
:members: diagnostics, phonemize, close
:special-members: __init__
:show-inheritance:
```

```{autoclass} piperg2p.EspeakCliBackend
:members: diagnostics, phonemize, close
:special-members: __init__
:show-inheritance:
```

`NativeEspeakProvider` and `EspeakCliBackend` are retained as compatibility wrappers for downstream users. Piper's public `Clause` has three fields; runtime clause terminator codes are converted at the adapter boundary and are not exposed through that type.

```{autoclass} piperg2p.NativeEspeakProvider
:members:
:show-inheritance:
```

```{autoclass} piperg2p.TextBackend
:members: diagnostics, phonemize, close
:show-inheritance:
```

Piper owns the public frontend boundary, NFD normalization, punctuation spacing, language-switch and joiner cleanup, vowel-cluster merging, raw blocks, and lexicon overlays. See [diagnostics](diagnostics.md) for stable reported fields.
