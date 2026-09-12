"""Execute PiperG2P compatibility and lexicon-overlay benchmark corpora."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from piperg2p import PiperFrontend, VoiceConfig
from piperg2p.lexicons import G2LexLookup


def _run_case(frontend: PiperFrontend, case: dict[str, Any]) -> dict[str, Any]:
    result = frontend.phonemize(case["text"])
    return {
        "id": case["id"],
        "status": "pass",
        "phoneme_type": case.get("phoneme_type"),
        "sentences": [
            {"phonemes": sentence.phoneme_string, "ids": list(sentence.ids)}
            for sentence in result.sentences
        ],
        "diagnostics": {
            "backend": result.diagnostics.backend if result.diagnostics else None,
            "lexicon": (
                result.diagnostics.lexicon.implementation
                if result.diagnostics and result.diagnostics.lexicon
                else None
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path(__file__).parent / "data" / "core.json")
    parser.add_argument("--config", type=Path, help="Voice config used to execute compatible corpus cases")
    parser.add_argument("--mode", choices=("reference", "overlay"), default="reference")
    parser.add_argument("--lexicon", action="append", default=[], help="Direct .g2lex asset for overlay mode")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    profile = corpus["profile"]
    report: dict[str, Any] = {
        "mode": args.mode,
        "parity": (
            "piper-eSpeak-only compatibility target"
            if args.mode == "reference"
            else "PiperG2P-owned lexicon overlay extension"
        ),
        "profile": profile,
        "cases": [],
    }
    if args.config is None:
        report["status"] = "metadata-only"
        report["case_count"] = len(corpus["cases"])
    else:
        config = VoiceConfig.from_json(args.config)
        lookup = G2LexLookup(args.lexicon, language=config.espeak_voice) if args.mode == "overlay" else None
        try:
            frontend = PiperFrontend(config, lexicon_backend=lookup) if lookup is not None else PiperFrontend(config)
            try:
                for case in corpus["cases"]:
                    if case.get("phoneme_type") != config.phoneme_type.value:
                        report["cases"].append({"id": case["id"], "status": "skipped"})
                    else:
                        report["cases"].append(_run_case(frontend, case))
            finally:
                frontend.close()
        finally:
            if lookup is not None:
                lookup.close()
        report["status"] = "executed"
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
