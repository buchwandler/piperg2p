# Diagnostics API

Diagnostics are immutable dataclasses that describe the selected frontend/backend, capability, fallback, and optional lexicon state. They are observational; `inspect_espeak()` performs capability inspection without initializing an inference backend.

```{autoclass} piperg2p.BackendDiagnostics
:members:
:show-inheritance:
```

```{autoclass} piperg2p.FrontendDiagnostics
:members:
:show-inheritance:
```

```{autoclass} piperg2p.EspeakCapabilities
:members:
:show-inheritance:
```

```{autofunction} piperg2p.inspect_espeak

```

`parity` is Piper's clause/composition compatibility label; `phoneme_parity` is the runtime's raw phoneme semantic parity. `exact_clause_api` reports terminator-capable native clause support and does not promise identical phoneme semantics. See the [eSpeak guide](../espeak.md) for interpretation.
