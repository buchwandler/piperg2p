from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .backends import PhonemeBackend
from .codec import EncodeResult, MissingPhonemePolicy
from .config import PhonemeType, VoiceConfig
from .diagnostics import FrontendDiagnostics
from .errors import UnsupportedPhonemeTypeError
from .raw_blocks import compose_raw_segments, parse_raw_blocks
from .registry import spec_for
from .types import PhonemeSentence, PhonemizeResult


class PiperFrontend:
    """Voice-config-driven Piper frontend independent from Piper's runtime."""

    def __init__(
        self,
        config: VoiceConfig,
        *,
        backend: PhonemeBackend | None = None,
        missing: MissingPhonemePolicy | str = MissingPhonemePolicy.WARN,
    ) -> None:
        self.config = config
        self.missing = MissingPhonemePolicy(missing)
        self._spec = spec_for(config)
        self.backend = backend if backend is not None else self._make_backend()

    def _make_backend(self) -> PhonemeBackend:
        if self.config.phoneme_type in {PhonemeType.TEXT, PhonemeType.ESPEAK}:
            return self._spec.backend_factory(self.config)
        raise UnsupportedPhonemeTypeError(
            f"phoneme_type {self.config.phoneme_type.value!r} requires optional extra {self._spec.optional_extra!r}"
        )

    @classmethod
    def from_config(cls, path: str | Path, **kwargs: Any) -> PiperFrontend:
        return cls(VoiceConfig.from_json(path), **kwargs)

    def encode(self, phonemes: Iterable[str]) -> EncodeResult:
        return self._spec.encoder.encode(tuple(phonemes), self.config.phoneme_id_map, self.missing)

    @property
    def diagnostics(self) -> FrontendDiagnostics:
        backend_diagnostics = getattr(self.backend, "diagnostics", None)
        return FrontendDiagnostics(
            phoneme_type=self.config.phoneme_type.value,
            backend=backend_diagnostics.implementation if backend_diagnostics else type(self.backend).__name__,
            backend_diagnostics=backend_diagnostics,
        )

    def phonemize_prepared(self, text: str) -> PhonemizeResult:
        if self.config.phoneme_type is PhonemeType.ESPEAK:
            segments = parse_raw_blocks(text)
            groups = compose_raw_segments(
                segments,
                lambda value: self.backend.phonemize(value, voice=self.config.espeak_voice),
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
            text=text,
            sentences=tuple(sentences),
            diagnostics=self.diagnostics,
            warnings=tuple(warning_messages),
        )

    phonemize = phonemize_prepared

    def close(self) -> None:
        close = getattr(self.backend, "close", None)
        if close is not None:
            close()

    def __enter__(self) -> PiperFrontend:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
