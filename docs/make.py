#!/usr/bin/env python
"""Build PiperG2P documentation with Sphinx.

Usage: python docs/make.py [clean|html|dirhtml|latex|latexpdf|text|man|changes|linkcheck|doctest|all|help]
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run the requested Sphinx documentation build target."""
    script_dir = Path(__file__).resolve().parent
    source_dir = script_dir
    build_dir = script_dir / "_build"
    target = sys.argv[1] if len(sys.argv) > 1 else "html"

    if target == "clean":
        if build_dir.exists():
            print(f"Cleaning {build_dir}...")
            shutil.rmtree(build_dir)
        return 0

    if target == "help":
        print(__doc__)
        return 0

    valid_targets = {
        "html",
        "dirhtml",
        "latex",
        "latexpdf",
        "text",
        "man",
        "changes",
        "linkcheck",
        "doctest",
        "all",
    }
    if target not in valid_targets:
        print(f"Unknown target: {target}")
        print("Use 'help' target for help")
        return 1

    build_dir.mkdir(parents=True, exist_ok=True)
    formats = ["html", "dirhtml", "latex"] if target == "all" else [target]
    for fmt in formats:
        output_dir = build_dir / fmt
        command = ["sphinx-build", "-W", "-b", fmt, str(source_dir), str(output_dir)]
        print(f"Building {fmt} documentation...")
        subprocess.run(command, check=True)

    print(f"Build finished. Documentation is in {build_dir / formats[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
