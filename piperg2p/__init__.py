"""Independent Piper G2P/ID frontend."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

from .api import (
    PiperG2P,
    get_g2p,
    phoneme_ids,
    phonemes,
    phonemize,
    phonemize_prepared,
    tokenize,
)
from .backends import (
    EspeakBackend,
    EspeakCliBackend,
    NativeEspeakProvider,
    PhonemeBackend,
    TextBackend,
)
from .cache import cache_info, clear_cache
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
    ids_to_phonemes,
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
from .language_routing import normalize_language, route_language
from .lexicons.registry import available_lexicons, lexicon_info
from .markers import apply_marker_overrides, parse_delimited
from .raw_blocks import (
    RawPhonemeSegment,
    TextSegment,
    compose_raw_segments,
    parse_raw_blocks,
)
from .stress import apply_stress
from .types import (
    LanguageRoute,
    LanguageRoutingConfig,
    LexiconEvidence,
    OverrideSpan,
    OverrideSpanLike,
    PhonemeSentence,
    PhonemizeResult,
    TokenAnnotation,
    TokenAnnotationLike,
    TokenSpan,
)

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
    "LanguageRoute",
    "LanguageRoutingConfig",
    "LexiconConfigurationError",
    "LexiconDependencyError",
    "LexiconError",
    "LexiconEvidence",
    "LexiconResourceError",
    "MissingPhonemeError",
    "MissingPhonemePolicy",
    "MissingPhonemeWarning",
    "NativeEspeakProvider",
    "OverrideSpan",
    "OverrideSpanLike",
    "PhonemeBackend",
    "PhonemeSentence",
    "PhonemeType",
    "PhonemizationError",
    "PhonemizeResult",
    "PinyinEncoder",
    "PiperConfig",
    "PiperFrontend",
    "PiperG2P",
    "PiperG2PError",
    "PiperG2PWarning",
    "RawPhonemeSegment",
    "ResourceError",
    "ResourceUnavailableError",
    "TextBackend",
    "TextSegment",
    "TokenAnnotation",
    "TokenAnnotationLike",
    "TokenSpan",
    "UnsupportedCompatibilityError",
    "UnsupportedPhonemeTypeError",
    "VoiceConfig",
    "apply_marker_overrides",
    "apply_stress",
    "available_lexicons",
    "cache_info",
    "clear_cache",
    "compose_raw_segments",
    "encode_phonemes",
    "encode_pinyin",
    "get_g2p",
    "ids_to_phonemes",
    "lexicon_info",
    "normalize_language",
    "parse_delimited",
    "parse_raw_blocks",
    "phoneme_ids",
    "phonemes",
    "phonemize",
    "phonemize_prepared",
    "route_language",
    "tokenize",
]
