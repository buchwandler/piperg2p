from __future__ import annotations

import json
import warnings
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .errors import CompatibilityWarning, ConfigError, UnsupportedPhonemeTypeError


class PhonemeType(str, Enum):
    ESPEAK = "espeak"
    TEXT = "text"
    PINYIN = "pinyin"
    HEBREW = "hebrew"
    JAPANESE = "japanese"
    THAI = "thai"


def _integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{name} must be an integer")
    return value


@dataclass(frozen=True)
class VoiceConfig:
    """Validated subset of a Piper ``.onnx.json`` voice configuration."""

    num_symbols: int
    num_speakers: int
    sample_rate: int
    phoneme_id_map: Mapping[str, tuple[int, ...]]
    phoneme_type: PhonemeType = PhonemeType.ESPEAK
    espeak_voice: str = "en-us"
    speaker_id_map: Mapping[str, int] = field(default_factory=dict)
    default_speaker_id: int = 0
    noise_scale: float = 0.667
    length_scale: float = 1.0
    noise_w: float = 0.8
    hop_length: int = 256
    vowel_clusters: frozenset[tuple[str, ...]] = field(default_factory=frozenset)
    piper_version: str | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            phoneme_type = PhonemeType(self.phoneme_type)
        except (TypeError, ValueError) as exc:
            raise UnsupportedPhonemeTypeError(
                f"unsupported phoneme_type {self.phoneme_type!r}; expected one of "
                f"{', '.join(item.value for item in PhonemeType)}"
            ) from exc
        object.__setattr__(self, "phoneme_type", phoneme_type)
        object.__setattr__(
            self,
            "phoneme_id_map",
            MappingProxyType(
                {str(key): tuple(value) for key, value in self.phoneme_id_map.items()}
            ),
        )
        object.__setattr__(
            self,
            "speaker_id_map",
            MappingProxyType(
                {str(key): int(value) for key, value in self.speaker_id_map.items()}
            ),
        )
        object.__setattr__(
            self,
            "vowel_clusters",
            frozenset(
                tuple(str(value) for value in cluster)
                for cluster in self.vowel_clusters
            ),
        )
        object.__setattr__(self, "extra", MappingProxyType(dict(self.extra)))

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any], *, strict: bool = True) -> VoiceConfig:
        if not isinstance(raw, Mapping):
            raise ConfigError("voice config must be a mapping")
        audio = raw.get("audio")
        inference = raw.get("inference")
        espeak = raw.get("espeak")
        if not isinstance(audio, Mapping):
            if strict:
                raise ConfigError("voice config is missing audio.sample_rate")
            audio = {}
        if not isinstance(inference, Mapping):
            if strict and "inference" in raw:
                raise ConfigError("inference must be a mapping")
            inference = {}
        if not isinstance(espeak, Mapping):
            if strict and "espeak" in raw:
                raise ConfigError("espeak must be a mapping")
            espeak = {}

        id_map_raw = raw.get("phoneme_id_map")
        if not isinstance(id_map_raw, Mapping) or not id_map_raw:
            raise ConfigError("voice config is missing phoneme_id_map")
        id_map: dict[str, tuple[int, ...]] = {}
        for phoneme, values in id_map_raw.items():
            if isinstance(values, int) and not isinstance(values, bool):
                values = (values,)
            elif isinstance(values, Sequence) and not isinstance(
                values, (str, bytes, bytearray)
            ):
                values = tuple(values)
            else:
                raise ConfigError(f"invalid id list for phoneme {phoneme!r}")
            if not values:
                raise ConfigError(f"id list for phoneme {phoneme!r} is empty")
            ids = tuple(
                _integer(value, f"id list for phoneme {phoneme!r}") for value in values
            )
            if any(value < 0 for value in ids):
                raise ConfigError(
                    f"id list for phoneme {phoneme!r} contains a negative ID"
                )
            id_map[str(phoneme)] = ids

        if "num_symbols" not in raw:
            if strict:
                raise ConfigError("voice config is missing num_symbols")
            num_symbols = max(max(values) for values in id_map.values()) + 1
            warnings.warn(
                "inferred num_symbols from phoneme_id_map",
                CompatibilityWarning,
                stacklevel=2,
            )
        else:
            num_symbols = _integer(raw["num_symbols"], "num_symbols")
        if num_symbols <= 0:
            raise ConfigError("num_symbols must be positive")

        if "num_speakers" not in raw:
            if strict:
                raise ConfigError("voice config is missing num_speakers")
            num_speakers = 1
        else:
            num_speakers = _integer(raw["num_speakers"], "num_speakers")
        if num_speakers <= 0:
            raise ConfigError("num_speakers must be positive")

        if "sample_rate" not in audio:
            if strict:
                raise ConfigError("voice config is missing audio.sample_rate")
            sample_rate = 22050
        else:
            sample_rate = _integer(audio["sample_rate"], "audio.sample_rate")
        if sample_rate <= 0:
            raise ConfigError("audio.sample_rate must be positive")
        if max(value for values in id_map.values() for value in values) >= num_symbols:
            raise ConfigError("phoneme_id_map contains an ID outside num_symbols")

        speaker_map_raw = raw.get("speaker_id_map") or {}
        if not isinstance(speaker_map_raw, Mapping):
            raise ConfigError("speaker_id_map must be a mapping")
        speaker_map = {
            str(key): _integer(value, f"speaker_id_map[{key!r}]")
            for key, value in speaker_map_raw.items()
        }
        default_speaker = _integer(
            raw.get("default_speaker_id", 0), "default_speaker_id"
        )
        if default_speaker < 0 or default_speaker >= num_speakers:
            raise ConfigError("default_speaker_id is outside num_speakers")
        if any(value < 0 or value >= num_speakers for value in speaker_map.values()):
            raise ConfigError("speaker_id_map contains an ID outside num_speakers")

        clusters_raw = raw.get("vowel_clusters") or ()
        if not isinstance(clusters_raw, Sequence) or isinstance(
            clusters_raw, (str, bytes)
        ):
            raise ConfigError("vowel_clusters must be a sequence of sequences")
        clusters: set[tuple[str, ...]] = set()
        for cluster in clusters_raw:
            if isinstance(cluster, str):
                values = tuple(cluster)
            elif isinstance(cluster, Sequence):
                values = tuple(str(value) for value in cluster)
            else:
                raise ConfigError("each vowel cluster must be a sequence")
            if len(values) < 2:
                raise ConfigError("vowel clusters must contain at least two elements")
            if "".join(values) not in id_map:
                raise ConfigError(
                    f"merged vowel cluster {''.join(values)!r} is absent from phoneme_id_map"
                )
            clusters.add(values)

        known = {
            "num_symbols",
            "num_speakers",
            "audio",
            "inference",
            "espeak",
            "phoneme_id_map",
            "phoneme_type",
            "speaker_id_map",
            "default_speaker_id",
            "hop_length",
            "vowel_clusters",
            "piper_version",
        }
        extra = {key: value for key, value in raw.items() if key not in known}
        return cls(
            num_symbols=num_symbols,
            num_speakers=num_speakers,
            sample_rate=sample_rate,
            phoneme_id_map=id_map,
            phoneme_type=raw.get("phoneme_type", PhonemeType.ESPEAK),
            espeak_voice=str(espeak.get("voice", "en-us")),
            speaker_id_map=speaker_map,
            default_speaker_id=default_speaker,
            noise_scale=float(inference.get("noise_scale", 0.667)),
            length_scale=float(inference.get("length_scale", 1.0)),
            noise_w=float(inference.get("noise_w", 0.8)),
            hop_length=_integer(raw.get("hop_length", 256), "hop_length"),
            vowel_clusters=frozenset(clusters),
            piper_version=(
                str(raw["piper_version"])
                if raw.get("piper_version") is not None
                else None
            ),
            extra=extra,
        )

    @classmethod
    def from_json(cls, path: str | Path, *, strict: bool = True) -> VoiceConfig:
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle), strict=strict)

    @property
    def noise_w_scale(self) -> float:
        return self.noise_w

    def to_dict(self) -> dict[str, Any]:
        result = dict(self.extra)
        result.update(
            {
                "num_symbols": self.num_symbols,
                "num_speakers": self.num_speakers,
                "audio": {"sample_rate": self.sample_rate},
                "inference": {
                    "noise_scale": self.noise_scale,
                    "length_scale": self.length_scale,
                    "noise_w": self.noise_w,
                },
                "espeak": {"voice": self.espeak_voice},
                "phoneme_id_map": {
                    key: list(values) if len(values) != 1 else values[0]
                    for key, values in self.phoneme_id_map.items()
                },
                "phoneme_type": self.phoneme_type.value,
                "speaker_id_map": dict(self.speaker_id_map),
                "default_speaker_id": self.default_speaker_id,
                "hop_length": self.hop_length,
                "vowel_clusters": [
                    list(cluster) for cluster in sorted(self.vowel_clusters)
                ],
            }
        )
        if self.piper_version is not None:
            result["piper_version"] = self.piper_version
        return result


PiperConfig = VoiceConfig
