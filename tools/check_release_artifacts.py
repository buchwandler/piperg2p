"""Check that release artifacts contain the intended package and metadata."""

from __future__ import annotations

import argparse
import tarfile
import zipfile
from pathlib import Path


def _wheel_version(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        metadata = next(
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        )
        rows = archive.read(metadata).decode("utf-8").splitlines()
    return next(row.removeprefix("Version: ") for row in rows if row.startswith("Version: "))

def _sdist_version(path: Path) -> str:
    with tarfile.open(path, "r:gz") as archive:
        metadata = next(
            member
            for member in archive.getmembers()
            if member.name.endswith("/PKG-INFO")
        )
        handle = archive.extractfile(metadata)
        if handle is None:
            raise SystemExit(f"sdist PKG-INFO could not be read: {path}")
        rows = handle.read().decode("utf-8").splitlines()

    return next(
        row.removeprefix("Version: ")
        for row in rows
        if row.startswith("Version: ")
    )


def _check_wheel(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    if not any(name.startswith("piperg2p/") and name.endswith(".py") for name in names):
        raise SystemExit(f"wheel does not contain piperg2p Python files: {path}")
    forbidden = ("tests/", "benchmarks/", ".github/")
    included = [name for name in names if name.startswith(forbidden)]
    if included:
        raise SystemExit(f"wheel contains excluded files: {included}")
    return _wheel_version(path)


def _check_sdist(path: Path) -> str:
    with tarfile.open(path, "r:gz") as archive:
        names = archive.getnames()
    required = ("pyproject.toml", "README.md", "LICENSE", "piperg2p/__init__.py")
    if not all(any(name.endswith(value) for name in names) for value in required):
        raise SystemExit(f"sdist is missing a required project file: {path}")
    return _sdist_version(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist", type=Path)
    parser.add_argument("--expected-version")
    args = parser.parse_args()
    wheels = sorted(args.dist.glob("*.whl"))
    sdists = sorted(args.dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit("dist must contain exactly one wheel and one sdist")
    wheel_version = _check_wheel(wheels[0])
    sdist_version = _check_sdist(sdists[0])
    if wheel_version != sdist_version:
        raise SystemExit(
            f"artifact version mismatch: wheel={wheel_version!r}, "
            f"sdist={sdist_version!r}"
        )
    if args.expected_version is not None and wheel_version != args.expected_version:
        raise SystemExit(
            f"artifact version {wheel_version!r} does not match "
            f"expected version {args.expected_version!r}"
        )
    print(
        f"checked {wheels[0].name} and {sdists[0].name} "
        f"(version {wheel_version})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
