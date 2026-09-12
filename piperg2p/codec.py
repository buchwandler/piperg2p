from __future__ import annotations

import warnings
from collections.abc import Mapping, Sequence
from enum import Enum
from typing import Protocol

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
