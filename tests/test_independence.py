import importlib


def test_public_imports_do_not_require_piper():
    module = importlib.import_module("piperg2p")
    assert module.PiperFrontend
    assert "piper" not in module.__dict__
    assert module.PhonemeType.TEXT.value == "text"
