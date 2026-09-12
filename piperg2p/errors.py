"""Public exceptions and warnings raised by :mod:`piperg2p`."""

from __future__ import annotations


class PiperG2PError(Exception):
    """Base class for piperg2p failures."""


class ConfigError(PiperG2PError, ValueError):
    """The voice configuration is invalid."""


class UnsupportedPhonemeTypeError(ConfigError):
    """The configuration names a frontend that is not supported."""


class UnsupportedCompatibilityError(ConfigError):
    """The recognized profile is outside the implemented compatibility boundary."""


class BackendError(PiperG2PError):
    """Base class for backend failures."""


class BackendUnavailableError(BackendError):
    """A requested backend cannot be initialized."""


class PhonemizationError(BackendError):
    """A backend failed while converting text."""


class ResourceError(PiperG2PError):
    """A language or backend resource is invalid."""


class ResourceUnavailableError(ResourceError):
    """An optional resource is not installed or usable."""


class LexiconError(PiperG2PError):
    """Base class for lexicon overlay failures."""


class LexiconDependencyError(LexiconError):
    """An optional lexicon package is not installed."""


class LexiconResourceError(LexiconError):
    """A requested lexicon asset or runtime is invalid or unavailable."""


class LexiconConfigurationError(LexiconError):
    """Lexicon options are incompatible with the selected frontend."""


class MissingPhonemeError(PiperG2PError, KeyError):
    """A required phoneme is absent from the selected voice map."""


class PiperG2PWarning(UserWarning):
    """Base class for piperg2p warnings."""


class MissingPhonemeWarning(PiperG2PWarning):
    """A phoneme was omitted because it is absent from the voice map."""


class BackendFallbackWarning(PiperG2PWarning):
    """A backend fell back to a less compatible implementation."""


class CompatibilityWarning(PiperG2PWarning):
    """A compatibility-relevant lenient behavior was used."""
