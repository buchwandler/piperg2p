"""Sibling-oriented high-level PiperG2P API."""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from .backends import EspeakBackend
from .cache import cache_key, get_or_create
from .codec import MissingPhonemePolicy
from .config import PhonemeType, VoiceConfig
from .errors import UnsupportedCompatibilityError
from .frontend import PiperFrontend
from .types import (
    LanguageRoutingConfig,
    OverrideSpanLike,
    PhonemizeResult,
    TokenAnnotationLike,
    TokenSpan,
)

ConfigLike = VoiceConfig | str | Path | Mapping[str, Any]


def _config(value: ConfigLike, *, strict: bool = True) -> VoiceConfig:
    if isinstance(value, VoiceConfig):
        return value
    if isinstance(value, (str, Path)):
        return VoiceConfig.from_json(value, strict=strict)
    if isinstance(value, Mapping):
        return VoiceConfig.from_dict(value, strict=strict)
    raise TypeError("config must be a VoiceConfig, path, or mapping")


def _validate_compatibility(
    *,
    use_spacy: bool | None,
    spacy_model: str | None,
    spacy_model_size: str | None,
    use_goruut_fallback: bool,
) -> None:
    if use_spacy:
        raise UnsupportedCompatibilityError("PiperG2P does not use spaCy")
    if spacy_model is not None:
        raise UnsupportedCompatibilityError("PiperG2P does not use spaCy models")
    if spacy_model_size is not None:
        raise UnsupportedCompatibilityError("PiperG2P does not use spaCy model sizes")
    if use_goruut_fallback:
        raise UnsupportedCompatibilityError(
            "Goruut fallback is not supported by PiperG2P"
        )


def _token_is_word(value: str) -> bool:
    return bool(value) and unicodedata.category(value)[0] in {"L", "N"}


def tokenize(text: str, *, keep_punct: bool = True) -> list[TokenSpan]:
    """Tokenize prepared text without changing its source coordinate space."""
    tokens: list[TokenSpan] = []
    position = 0
    apostrophes = {"'", "’", "ʼ", "＇"}
    hyphens = {"-", "‐", "‑", "‒", "–", "—", "−"}
    while position < len(text):
        value = text[position]
        if _token_is_word(value):
            start = position
            position += 1
            while position < len(text):
                value = text[position]
                if unicodedata.category(value).startswith("M") or _token_is_word(value):
                    position += 1
                    continue
                if value in apostrophes | hyphens:
                    next_position = position + 1
                    if next_position < len(text) and _token_is_word(
                        text[next_position]
                    ):
                        position += 1
                        continue
                break
            tokens.append(TokenSpan(text[start:position], start, position))
            continue
        if keep_punct and unicodedata.category(value)[0] in {"P", "S"}:
            tokens.append(TokenSpan(value, position, position + 1))
        position += 1
    return tokens


class PiperG2P:
    """Reusable voice-config-driven facade over :class:`PiperFrontend`."""

    def __init__(
        self,
        language: str,
        config: ConfigLike,
        *,
        lexicons: str | Sequence[str] | None = None,
        use_espeak_fallback: bool = True,
        use_cli: bool = False,
        strict: bool = True,
        missing: MissingPhonemePolicy | str = MissingPhonemePolicy.WARN,
        lexicon_store: Any = None,
        lexicon_backend: Any = None,
        use_spacy: bool | None = None,
        spacy_model: str | None = None,
        spacy_model_size: str | None = None,
        use_goruut_fallback: bool = False,
    ) -> None:
        if not language:
            raise ValueError("language must not be empty")
        _validate_compatibility(
            use_spacy=use_spacy,
            spacy_model=spacy_model,
            spacy_model_size=spacy_model_size,
            use_goruut_fallback=use_goruut_fallback,
        )
        self.language = language
        self.config = _config(config, strict=strict)
        self.use_espeak_fallback = use_espeak_fallback
        self._frontend = PiperFrontend(
            self.config,
            backend=(
                EspeakBackend(mode="cli", vowel_clusters=self.config.vowel_clusters)
                if use_cli and self.config.phoneme_type is PhonemeType.ESPEAK
                else None
            ),
            missing=missing,
            lexicons=tuple([lexicons] if isinstance(lexicons, str) else lexicons or ()),
            lexicon_store=lexicon_store,
            lexicon_backend=lexicon_backend,
            use_espeak_fallback=use_espeak_fallback,
        )

    @property
    def frontend(self) -> PiperFrontend:
        return self._frontend

    def phonemize(self, text: str) -> str:
        return self.phonemize_prepared(text).phonemes

    def phonemize_prepared(
        self,
        text: str,
        *,
        overrides: Sequence[OverrideSpanLike] | None = None,
        annotations: Sequence[TokenAnnotationLike] | None = None,
        overlap: Literal["snap", "strict", "split"] = "snap",
        strict_stress: bool = False,
        language_routing: LanguageRoutingConfig | Mapping[str, Any] | None = None,
    ) -> PhonemizeResult:
        result = self._frontend.phonemize_prepared(text, annotations=annotations)
        result.clean_text = text
        result.extended_text = text
        result.tokens = tokenize(text)
        result.phonemes = "".join(
            sentence.phoneme_string for sentence in result.sentences
        )
        result.token_ids = [
            identifier for sentence in result.sentences for identifier in sentence.ids
        ]
        if overrides or annotations or language_routing is not None:
            from .spans import apply_overrides

            result = apply_overrides(
                self,
                result,
                text,
                overrides=overrides or (),
                annotations=annotations or (),
                overlap=overlap,
                strict_stress=strict_stress,
                language_routing=language_routing,
            )
        elif strict_stress:
            raise ValueError("strict_stress requires an override or annotation span")
        return result

    __call__ = phonemize_prepared

    def lexicon_evidence(self, word: str, tag: str | None = None):
        from .lexicons.registry import evidence_for_lookup

        return evidence_for_lookup(self._frontend, word, tag=tag)

    def close(self) -> None:
        self._frontend.close()

    def __enter__(self) -> PiperG2P:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def get_g2p(
    language: str,
    *,
    config: ConfigLike,
    lexicons: str | Sequence[str] | None = None,
    use_espeak_fallback: bool = True,
    use_cli: bool = False,
    strict: bool = True,
    missing: MissingPhonemePolicy | str = MissingPhonemePolicy.WARN,
    lexicon_store: Any = None,
    lexicon_backend: Any = None,
    use_spacy: bool | None = None,
    spacy_model: str | None = None,
    spacy_model_size: str | None = None,
    use_goruut_fallback: bool = False,
) -> PiperG2P:
    normalized_config = _config(config, strict=strict)
    lexicon_names = tuple([lexicons] if isinstance(lexicons, str) else lexicons or ())
    kwargs = {
        "lexicons": lexicon_names,
        "use_espeak_fallback": use_espeak_fallback,
        "use_cli": use_cli,
        "strict": strict,
        "missing": missing,
        "lexicon_store": lexicon_store,
        "lexicon_backend": lexicon_backend,
        "use_spacy": use_spacy,
        "spacy_model": spacy_model,
        "spacy_model_size": spacy_model_size,
        "use_goruut_fallback": use_goruut_fallback,
    }
    if lexicon_backend is not None or lexicon_store is not None:
        return PiperG2P(language, normalized_config, **kwargs)
    key = cache_key(
        normalized_config,
        language,
        use_cli=use_cli,
        missing=MissingPhonemePolicy(missing).value,
        lexicons=lexicon_names,
        strict=strict,
        use_espeak_fallback=use_espeak_fallback,
    )
    return get_or_create(key, lambda: PiperG2P(language, normalized_config, **kwargs))


def _require_g2p(
    language: str,
    config: ConfigLike | None,
    g2p: PiperG2P | None,
    **kwargs: Any,
) -> PiperG2P:
    if g2p is not None:
        if config is not None:
            raise TypeError("config must be omitted when reusing g2p")
        return g2p
    if config is None:
        raise TypeError("config is required when g2p is not supplied")
    return get_g2p(language, config=config, **kwargs)


def phonemize_prepared(
    text: str,
    language: str,
    *,
    config: ConfigLike | None = None,
    overrides: Sequence[OverrideSpanLike] | None = None,
    annotations: Sequence[TokenAnnotationLike] | None = None,
    return_ids: bool = True,
    return_phonemes: bool = True,
    overlap: Literal["snap", "strict", "split"] = "snap",
    lexicons: str | Sequence[str] | None = None,
    use_espeak_fallback: bool = True,
    use_cli: bool = False,
    strict: bool = True,
    strict_stress: bool = False,
    g2p: PiperG2P | None = None,
    language_routing: LanguageRoutingConfig | Mapping[str, Any] | None = None,
    missing: MissingPhonemePolicy | str = MissingPhonemePolicy.WARN,
) -> PhonemizeResult:
    del return_ids, return_phonemes
    frontend = _require_g2p(
        language,
        config,
        g2p,
        lexicons=lexicons,
        use_espeak_fallback=use_espeak_fallback,
        use_cli=use_cli,
        strict=strict,
        missing=missing,
    )
    return frontend.phonemize_prepared(
        text,
        overrides=overrides,
        annotations=annotations,
        overlap=overlap,
        strict_stress=strict_stress,
        language_routing=language_routing,
    )


phonemize = phonemize_prepared


def phonemes(*args: Any, **kwargs: Any) -> str:
    return phonemize_prepared(*args, **kwargs).phonemes


def phoneme_ids(*args: Any, **kwargs: Any) -> list[int]:
    return list(phonemize_prepared(*args, **kwargs).token_ids)
