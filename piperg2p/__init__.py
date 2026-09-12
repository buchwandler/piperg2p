"""Independent Piper G2P/ID frontend."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

from .backends import (
    EspeakBackend,
    EspeakCliBackend,
    NativeEspeakProvider,
    PhonemeBackend,
    TextBackend,
)
from .codec import (
    BOS,
    EOS,
    PAD,
    EncodeResult,
    EncoderStrategy,
    MissingPhonemePolicy,
    PinyinEncoder,
    encode_phonemes,
    encode_pinyin,
)
from .config import PhonemeType, PiperConfig, VoiceConfig
from .diagnostics import BackendDiagnostics, FrontendDiagnostics
from .errors import (
    BackendError,
    BackendFallbackWarning,
    BackendUnavailableError,
    CompatibilityWarning,
    ConfigError,
    LexiconConfigurationError,
    LexiconDependencyError,
    LexiconError,
    LexiconResourceError,
    MissingPhonemeError,
    MissingPhonemeWarning,
    PhonemizationError,
    PiperG2PError,
    PiperG2PWarning,
    ResourceError,
    ResourceUnavailableError,
    UnsupportedCompatibilityError,
    UnsupportedPhonemeTypeError,
)
from .frontend import PiperFrontend
from .raw_blocks import (
    RawPhonemeSegment,
    TextSegment,
    compose_raw_segments,
    parse_raw_blocks,
)
from .types import PhonemeSentence, PhonemizeResult

try:
    __version__ = _distribution_version("piperg2p")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = [
    "BOS",
    "EOS",
    "PAD",
    "BackendDiagnostics",
    "BackendError",
    "BackendFallbackWarning",
    "BackendUnavailableError",
    "CompatibilityWarning",
    "ConfigError",
    "EncodeResult",
    "EncoderStrategy",
    "EspeakBackend",
    "EspeakCliBackend",
    "FrontendDiagnostics",
    "LexiconConfigurationError",
    "LexiconDependencyError",
    "LexiconError",
    "LexiconResourceError",
    "MissingPhonemeError",
    "MissingPhonemePolicy",
    "MissingPhonemeWarning",
    "NativeEspeakProvider",
    "PhonemeBackend",
    "PhonemeSentence",
    "PhonemeType",
    "PhonemizationError",
    "PhonemizeResult",
    "PinyinEncoder",
    "PiperConfig",
    "PiperFrontend",
    "PiperG2PError",
    "PiperG2PWarning",
    "RawPhonemeSegment",
    "ResourceError",
    "ResourceUnavailableError",
    "TextBackend",
    "TextSegment",
    "UnsupportedCompatibilityError",
    "UnsupportedPhonemeTypeError",
    "VoiceConfig",
    "compose_raw_segments",
    "encode_phonemes",
    "encode_pinyin",
    "parse_raw_blocks",
]
