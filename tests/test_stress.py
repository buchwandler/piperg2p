import pytest

from piperg2p import PiperG2PError
from piperg2p.stress import apply_stress


def test_structured_stress_levels():
    assert apply_stress("ˈkat", -2) == "kat"
    assert apply_stress("ˈkat", -1) == "ˌkat"
    assert apply_stress("kat", 1) == "ˌkat"
    assert apply_stress("kat", 2) == "ˈkat"


def test_invalid_stress_can_be_strict_or_permissive():
    assert apply_stress("kat", 0) == "kat"
    with pytest.raises(PiperG2PError):
        apply_stress("kat", 0, strict=True)
