from __future__ import annotations

import warnings
from collections.abc import Mapping, Sequence
from enum import Enum
from pathlib import Path
from typing import Protocol

from .config import VoiceConfig
from .errors import ConfigError, MissingPhonemeError, MissingPhonemeWarning
from .types import EncodeResult

PAD = "_"
BOS = "^"
EOS = "$"


class MissingPhonemePolicy(str, Enum):
    ERROR = "error"
    WARN = "warn"
    IGNORE = "ignore"


class EncoderStrategy(Protocol):
    def encode(
        self,
        phonemes: Sequence[str],
        id_map: Mapping[str, Sequence[int]],
        missing: MissingPhonemePolicy | str = MissingPhonemePolicy.WARN,
    ) -> EncodeResult: ...


def _control_ids(
    id_map: Mapping[str, Sequence[int]],
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    try:
        return tuple(id_map[BOS]), tuple(id_map[PAD]), tuple(id_map[EOS])
    except KeyError as exc:
        raise ConfigError(
            f"phoneme_id_map is missing required control symbol {exc.args[0]!r}"
        ) from exc


def _missing(
    phoneme: str, policy: MissingPhonemePolicy, items: list[str], messages: list[str]
) -> None:
    items.append(phoneme)
    message = f"phoneme {phoneme!r} is not present in voice phoneme_id_map"
    if policy is MissingPhonemePolicy.ERROR:
        raise MissingPhonemeError(message)
    if policy is MissingPhonemePolicy.WARN:
        warnings.warn(message, MissingPhonemeWarning, stacklevel=3)
        messages.append(message)


def encode_phonemes(
    phonemes: Sequence[str],
    id_map: Mapping[str, Sequence[int]],
    *,
    missing: MissingPhonemePolicy | str = MissingPhonemePolicy.WARN,
) -> EncodeResult:
    """Encode ordinary Piper IDs: ``BOS + PAD + (phoneme + PAD)* + EOS``."""
    policy = MissingPhonemePolicy(missing)
    bos_ids, pad_ids, eos_ids = _control_ids(id_map)
    out: list[int] = [int(value) for value in bos_ids + pad_ids]
    missing_items: list[str] = []
    messages: list[str] = []
    for phoneme in phonemes:
        ids = id_map.get(phoneme)
        if ids is None:
            _missing(phoneme, policy, missing_items, messages)
            continue
        out.extend(int(value) for value in ids)
        out.extend(int(value) for value in pad_ids)
    out.extend(int(value) for value in eos_ids)
    return EncodeResult(tuple(out), tuple(missing_items), tuple(messages))


class OrdinaryEncoder:
    def encode(
        self,
        phonemes: Sequence[str],
        id_map: Mapping[str, Sequence[int]],
        missing: MissingPhonemePolicy | str = MissingPhonemePolicy.WARN,
    ) -> EncodeResult:
        return encode_phonemes(phonemes, id_map, missing=missing)


class PinyinEncoder:
    """Group-aware encoder for flat Pinyin symbols."""

    def encode(
        self,
        phonemes: Sequence[str],
        id_map: Mapping[str, Sequence[int]],
        missing: MissingPhonemePolicy | str = MissingPhonemePolicy.WARN,
    ) -> EncodeResult:
        policy = MissingPhonemePolicy(missing)
        bos_ids, pad_ids, eos_ids = _control_ids(id_map)
        out: list[int] = [int(value) for value in bos_ids]
        missing_items: list[str] = []
        messages: list[str] = []
        for phoneme in phonemes:
            ids = id_map.get(phoneme)
            if ids is None:
                _missing(phoneme, policy, missing_items, messages)
                continue
            out.extend(int(value) for value in ids)
            if (
                phoneme in "12345"
                or phoneme.isspace()
                or phoneme in ",.!?;:，。！？；："
            ):
                out.extend(int(value) for value in pad_ids)
        out.extend(int(value) for value in eos_ids)
        return EncodeResult(tuple(out), tuple(missing_items), tuple(messages))


def encode_pinyin(
    phonemes: Sequence[str],
    id_map: Mapping[str, Sequence[int]],
    *,
    missing: MissingPhonemePolicy | str = MissingPhonemePolicy.WARN,
) -> EncodeResult:
    return PinyinEncoder().encode(phonemes, id_map, missing)


def ids_to_phonemes(ids: Sequence[int], config: object) -> str:
    """Decode framed Piper IDs using one explicit voice configuration."""
    if not isinstance(config, VoiceConfig):
        if isinstance(config, (str, Path)):
            config = VoiceConfig.from_json(config)
        elif isinstance(config, Mapping):
            config = VoiceConfig.from_dict(config)
        else:
            raise TypeError("config must be a VoiceConfig, path, or mapping")
    values = tuple(int(value) for value in ids)
    bos = tuple(config.phoneme_id_map[BOS])
    pad = tuple(config.phoneme_id_map[PAD])
    eos = tuple(config.phoneme_id_map[EOS])
    if values[: len(bos) + len(pad)] == bos + pad:
        values = values[len(bos) + len(pad) :]
    if values[-len(eos) :] == eos:
        values = values[: -len(eos)]
    candidates: dict[tuple[int, ...], str] = {}
    for symbol, symbol_ids in config.phoneme_id_map.items():
        if symbol in {BOS, PAD, EOS}:
            continue
        key = tuple(symbol_ids)
        previous = candidates.get(key)
        if previous is not None and previous != symbol:
            raise ConfigError(
                f"ambiguous ID mapping for {key!r}: {previous!r}, {symbol!r}"
            )
        candidates[key] = symbol
    keys = sorted(candidates, key=len, reverse=True)
    output: list[str] = []
    position = 0
    while position < len(values):
        matches = [key for key in keys if values[position : position + len(key)] == key]
        if not matches:
            raise ConfigError(f"cannot decode Piper ID sequence at position {position}")
        longest = matches[0]
        if len(matches) > 1 and len(matches[1]) == len(longest):
            raise ConfigError(f"ambiguous Piper ID sequence at position {position}")
        output.append(candidates[longest])
        position += len(longest)
        if values[position : position + len(pad)] == pad:
            position += len(pad)
    return "".join(output)
