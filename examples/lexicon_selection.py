from __future__ import annotations

from _common import language_parser

from piperg2p import available_lexicons, lexicon_info


def main() -> int:
    """List locally installed pronunciation assets for a language."""
    args = language_parser(
        "Inspect locally installed pronunciation assets"
    ).parse_args()
    for name in available_lexicons(args.language):
        print(name, lexicon_info(args.language, name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
