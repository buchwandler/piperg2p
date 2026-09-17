from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, Literal

EspeakMode = Literal["auto", "native", "cli"]

from .backends import PhonemeBackend
from .codec import EncodeResult, MissingPhonemePolicy
from .config import PhonemeType, VoiceConfig
from .diagnostics import FrontendDiagnostics
from .errors import (
    LexiconConfigurationError,
    UnsupportedCompatibilityError,
    UnsupportedPhonemeTypeError,
)
from .lexicons.base import LexiconDiagnostics, PronunciationLookup
from .lexicons.overlay import compose_lexicon_overlay
from .raw_blocks import compose_raw_segments, parse_raw_blocks
from .registry import spec_for
from .types import PhonemeSentence, PhonemizeResult


def _is_arabic_voice(voice: str) -> bool:
    normalized = voice.casefold().replace("_", "-")
    return normalized == "ar" or normalized.startswith(("ar-", "ar+"))


class PiperFrontend:
    """Voice-config-driven Piper frontend independent from Piper's runtime."""

    def __init__(
        self,
        config: VoiceConfig,
        *,
        backend: PhonemeBackend | None = None,
        espeak_mode: EspeakMode = "auto",
        missing: MissingPhonemePolicy | str = MissingPhonemePolicy.WARN,
        lexicons: Sequence[str] = (),
        lexicon_store: Any = None,
        lexicon_backend: PronunciationLookup | None = None,
        use_espeak_fallback: bool = True,
    ) -> None:
        if espeak_mode not in {"auto", "native", "cli"}:
            raise ValueError("eSpeak mode must be 'auto', 'native', or 'cli'")
        if backend is not None and espeak_mode != "auto":
            raise ValueError("backend and espeak_mode are mutually exclusive")
        self.espeak_mode = espeak_mode
        self.use_espeak_fallback = use_espeak_fallback
        self.config = config
        self.missing = MissingPhonemePolicy(missing)
        self._spec = spec_for(config)
        if config.phoneme_type is PhonemeType.ESPEAK and _is_arabic_voice(
            config.espeak_voice
        ):
            raise UnsupportedCompatibilityError(
                "Arabic Piper eSpeak preprocessing is not implemented; "
                "ordinary eSpeak compatibility is unavailable for Arabic voices"
            )
        self._lexicon_identifiers = tuple(lexicons)
        if self._lexicon_identifiers and lexicon_backend is not None:
            raise LexiconConfigurationError(
                "lexicons and lexicon_backend are mutually exclusive"
            )
        if lexicon_store is not None and not self._lexicon_identifiers:
            raise LexiconConfigurationError("lexicon_store requires managed lexicons")
        if (
            self._lexicon_identifiers or lexicon_backend is not None
        ) and config.phoneme_type is not PhonemeType.ESPEAK:
            raise LexiconConfigurationError(
                "lexicon overlay only supports phoneme_type='espeak'"
            )
        self._lexicon_store = lexicon_store
        self._lexicon_backend = lexicon_backend
        self._owns_lexicon_backend = False
        self.backend = backend if backend is not None else self._make_backend()

    @property
    def _lexicon_enabled(self) -> bool:
        return bool(self._lexicon_identifiers or self._lexicon_backend is not None)

    def _make_backend(self) -> PhonemeBackend:
        if self.config.phoneme_type is PhonemeType.ESPEAK:
            from .backends.espeak import EspeakBackend

            return EspeakBackend(
                mode=self.espeak_mode,
                vowel_clusters=self.config.vowel_clusters,
                merge_vowel_clusters=not self._lexicon_enabled,
            )
        if self.config.phoneme_type is PhonemeType.TEXT:
            assert self._spec.backend_factory is not None
            return self._spec.backend_factory(self.config)
        if not self._spec.implemented or self._spec.backend_factory is None:
            extra = (
                f" Install piperg2p[{self._spec.optional_extra}]."
                if self._spec.optional_extra
                else ""
            )
            raise UnsupportedPhonemeTypeError(
                f"phoneme_type {self.config.phoneme_type.value!r} is recognized but not implemented.{extra}"
            )
        return self._spec.backend_factory(self.config)

    def _ensure_lexicon_backend(self) -> PronunciationLookup:
        if self._lexicon_backend is not None:
            return self._lexicon_backend
        from .lexicons.lexphon import LexphonLookup

        self._lexicon_backend = LexphonLookup(
            self.config.espeak_voice,
            self._lexicon_identifiers,
            store=self._lexicon_store,
        )
        self._owns_lexicon_backend = True
        return self._lexicon_backend

    @classmethod
    def from_config(cls, path: str | Path, **kwargs: Any) -> PiperFrontend:
        return cls(VoiceConfig.from_json(path), **kwargs)

    def encode(self, phonemes: Iterable[str]) -> EncodeResult:
        return self._spec.encoder.encode(
            tuple(phonemes), self.config.phoneme_id_map, self.missing
        )

    def _lexicon_diagnostics(self) -> LexiconDiagnostics | None:
        if not self._lexicon_enabled:
            return None
        if self._lexicon_backend is not None:
            return self._lexicon_backend.diagnostics
        return LexiconDiagnostics(
            enabled=True,
            implementation="lexphon",
            language=self.config.espeak_voice,
            identifiers=self._lexicon_identifiers,
            compatibility="override",
        )

    @property
    def diagnostics(self) -> FrontendDiagnostics:
        backend_diagnostics = getattr(self.backend, "diagnostics", None)
        return FrontendDiagnostics(
            phoneme_type=self.config.phoneme_type.value,
            backend=backend_diagnostics.implementation
            if backend_diagnostics
            else type(self.backend).__name__,
            backend_diagnostics=backend_diagnostics,
            lexicon=self._lexicon_diagnostics(),
        )

    def phonemize_prepared(
        self, text: str, *, annotations: Sequence[Any] | None = None
    ) -> PhonemizeResult:
        if self.config.phoneme_type is PhonemeType.ESPEAK:
            segments = parse_raw_blocks(text)
            if self._lexicon_enabled:
                lookup = self._ensure_lexicon_backend()
                groups = compose_lexicon_overlay(
                    segments,
                    lookup,
                    lambda value: self.backend.phonemize(
                        value, voice=self.config.espeak_voice
                    ),
                    vowel_clusters=self.config.vowel_clusters,
                    fallback=self.use_espeak_fallback,
                    annotations=annotations or (),
                )
            else:
                groups = compose_raw_segments(
                    segments,
                    lambda value: self.backend.phonemize(
                        value, voice=self.config.espeak_voice
                    ),
                )
        else:
            groups = self.backend.phonemize(text, voice=self.config.espeak_voice)
        sentences: list[PhonemeSentence] = []
        warning_messages: list[str] = []
        for group in groups:
            encoded = self.encode(group)
            sentences.append(
                PhonemeSentence(
                    tuple(group),
                    encoded.ids,
                    encoded.missing_phonemes,
                    encoded.warnings,
                )
            )
            warning_messages.extend(encoded.warnings)
        return PhonemizeResult(
            clean_text=text,
            sentences=tuple(sentences),
            diagnostics=self.diagnostics,
            warnings=warning_messages,
        )

    phonemize = phonemize_prepared

    def close(self) -> None:
        close = getattr(self.backend, "close", None)
        if close is not None:
            close()
        if self._owns_lexicon_backend and self._lexicon_backend is not None:
            self._lexicon_backend.close()
            self._lexicon_backend = None

    def __enter__(self) -> PiperFrontend:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
