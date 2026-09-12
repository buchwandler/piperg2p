from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .backends import EspeakBackend, PhonemeBackend, TextBackend
from .codec import EncoderStrategy, OrdinaryEncoder, PinyinEncoder
from .config import PhonemeType, VoiceConfig
from .errors import UnsupportedPhonemeTypeError


@dataclass(frozen=True)
class FrontendSpec:
    phoneme_type: PhonemeType
    backend_factory: Callable[[VoiceConfig], PhonemeBackend] | None
    encoder: EncoderStrategy
    optional_extra: str | None = None
    implemented: bool = True



def _text_backend(config: VoiceConfig) -> TextBackend:
    del config
    return TextBackend()



def _espeak_backend(config: VoiceConfig) -> EspeakBackend:
    return EspeakBackend(vowel_clusters=config.vowel_clusters)



REGISTRY: dict[PhonemeType, FrontendSpec] = {
    PhonemeType.TEXT: FrontendSpec(PhonemeType.TEXT, _text_backend, OrdinaryEncoder()),
    PhonemeType.ESPEAK: FrontendSpec(PhonemeType.ESPEAK, _espeak_backend, OrdinaryEncoder()),
    PhonemeType.PINYIN: FrontendSpec(
        PhonemeType.PINYIN, None, PinyinEncoder(), "zh", False
    ),
    PhonemeType.HEBREW: FrontendSpec(
        PhonemeType.HEBREW, None, OrdinaryEncoder(), "he", False
    ),
    PhonemeType.JAPANESE: FrontendSpec(
        PhonemeType.JAPANESE, None, OrdinaryEncoder(), "ja", False
    ),
    PhonemeType.THAI: FrontendSpec(
        PhonemeType.THAI, None, OrdinaryEncoder(), "th", False
    ),
}



def spec_for(config: VoiceConfig) -> FrontendSpec:
    try:
        return REGISTRY[config.phoneme_type]
    except KeyError as exc:
        raise UnsupportedPhonemeTypeError(f"unsupported phoneme_type {config.phoneme_type.value!r}") from exc
