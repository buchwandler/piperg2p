# Errors and warnings

Errors are organized by the failure boundary: configuration/compatibility, backend execution, resources, lexicons, and missing voice-map symbols. Warning classes derive from `PiperG2PWarning`.

```{autoclass} piperg2p.PiperG2PError
:show-inheritance:
```

```{autoclass} piperg2p.ConfigError
:show-inheritance:
```

```{autoclass} piperg2p.UnsupportedPhonemeTypeError
:show-inheritance:
```

```{autoclass} piperg2p.UnsupportedCompatibilityError
:show-inheritance:
```

```{autoclass} piperg2p.BackendError
:show-inheritance:
```

```{autoclass} piperg2p.BackendUnavailableError
:show-inheritance:
```

```{autoclass} piperg2p.PhonemizationError
:show-inheritance:
```

```{autoclass} piperg2p.ResourceError
:show-inheritance:
```

```{autoclass} piperg2p.ResourceUnavailableError
:show-inheritance:
```

```{autoclass} piperg2p.LexiconError
:show-inheritance:
```

```{autoclass} piperg2p.LexiconDependencyError
:show-inheritance:
```

```{autoclass} piperg2p.LexiconResourceError
:show-inheritance:
```

```{autoclass} piperg2p.LexiconConfigurationError
:show-inheritance:
```

```{autoclass} piperg2p.MissingPhonemeError
:show-inheritance:
```

```{autoclass} piperg2p.PiperG2PWarning
:show-inheritance:
```

```{autoclass} piperg2p.MissingPhonemeWarning
:show-inheritance:
```

```{autoclass} piperg2p.BackendFallbackWarning
:show-inheritance:
```

```{autoclass} piperg2p.CompatibilityWarning
:show-inheritance:
```

See [encoding](../encoding.md) for missing-symbol policy and [eSpeak modes](../espeak.md) for automatic fallback behavior.
