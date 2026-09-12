import warnings

import pytest

from piperg2p import (
    MissingPhonemeError,
    MissingPhonemePolicy,
    MissingPhonemeWarning,
    encode_phonemes,
    encode_pinyin,
)

MAP = {
    "^": [10, 11],
    "_": [0],
    "$": [12],
    "a": [3],
    "x": [4, 5],
    "1": [6],
    " ": [7],
    ".": [8],
}


def test_ordinary_framing_supports_multi_id_symbols():
    result = encode_phonemes(["a", "x"], MAP)
    assert result.ids == (10, 11, 0, 3, 0, 4, 5, 0, 12)
    assert isinstance(result.ids, tuple)


def test_missing_policies_report_and_warn():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = encode_phonemes(["missing", "missing"], MAP)
    assert result.missing_phonemes == ("missing", "missing")
    assert (
        len(
            [
                item
                for item in caught
                if issubclass(item.category, MissingPhonemeWarning)
            ]
        )
        == 2
    )
    assert result.warnings
    assert encode_phonemes(
        ["missing"], MAP, missing=MissingPhonemePolicy.IGNORE
    ).missing_phonemes == ("missing",)
    with pytest.raises(MissingPhonemeError):
        encode_phonemes(["missing"], MAP, missing=MissingPhonemePolicy.ERROR)


def test_missing_control_symbols_are_config_errors():
    with pytest.raises(ValueError):
        encode_phonemes([], {"^": [1], "_": [0]})


def test_pinyin_padding_is_group_aware():
    result = encode_pinyin(["a", "1", "x", " ", "."], MAP)
    assert result.ids == (10, 11, 3, 6, 0, 4, 5, 7, 0, 8, 0, 12)
