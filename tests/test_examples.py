from pathlib import Path


def test_examples_do_not_download_resources():
    root = Path(__file__).parents[1] / "examples"
    for path in root.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "urllib" not in source
        assert "requests" not in source
        assert "download" not in source.casefold()
