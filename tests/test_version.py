from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

import piperg2p


def test_public_version_matches_distribution_metadata() -> None:
    try:
        expected = version("piperg2p")
    except PackageNotFoundError:
        expected = "0+unknown"

    assert piperg2p.__version__ == expected
