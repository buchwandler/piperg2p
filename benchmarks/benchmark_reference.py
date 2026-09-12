"""Compare PiperG2P output with reviewed output from a pinned Piper environment."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from piperg2p import PiperFrontend, VoiceConfig
from piperg2p.lexicons import G2LexLookup


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency_versions(names: tuple[str, ...]) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for name in names:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = None
    return result


def _asset_identity(paths: list[str]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for value in paths:
        path = Path(value)
        item: dict[str, Any] = {"path": str(path)}
        if path.is_file():
            item.update({"size": path.stat().st_size, "sha256": _sha256(path)})
        else:
            item["missing"] = True
        result.append(item)
    return result


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
            "compatibility_profile": (
                result.diagnostics.compatibility_profile if result.diagnostics else None
            ),
            "backend_diagnostics": (
                asdict(result.diagnostics.backend_diagnostics)
                if result.diagnostics and result.diagnostics.backend_diagnostics
                else None
            ),
            "lexicon": (
                asdict(result.diagnostics.lexicon)
                if result.diagnostics and result.diagnostics.lexicon
                else None
            ),
        },
    }


def _runtime_metadata(
    corpus: dict[str, Any], config: Path | None, assets: list[str]
) -> dict[str, Any]:
    profile = corpus["profile"]
    metadata: dict[str, Any] = {
        "reference": {
            "repository": profile.get("reference"),
            "commit": profile.get("commit"),
            "version": profile.get("version"),
        },
        "python": sys.version,
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
        "dependencies": _dependency_versions(("piperg2p", "g2lex", "lexphon")),
        "asset_identity": _asset_identity(assets),
    }
    if config is not None:
        metadata["voice_config_sha256"] = _sha256(config)
    return metadata


def _compare_cases(actual: list[dict[str, Any]], expected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expected_by_id = {case["id"]: case for case in expected}
    comparisons: list[dict[str, Any]] = []
    for case in actual:
        reference = expected_by_id.get(case["id"])
        if reference is None:
            comparisons.append({"id": case["id"], "status": "missing-expected"})
            continue
        actual_value = {key: case[key] for key in ("phoneme_type", "sentences")}
        expected_value = {key: reference.get(key) for key in ("phoneme_type", "sentences")}
        comparisons.append(
            {
                "id": case["id"],
                "status": "pass" if actual_value == expected_value else "mismatch",
                "actual": actual_value,
                "expected": expected_value,
            }
        )
    return comparisons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path(__file__).parent / "data" / "core.json")
    parser.add_argument("--config", type=Path, help="Voice config used to execute compatible corpus cases")
    parser.add_argument("--mode", choices=("reference", "overlay"), default="reference")
    parser.add_argument("--lexicon", action="append", default=[], help="Direct .g2lex asset for overlay mode")
    parser.add_argument("--expected", type=Path, help="Reviewed expected output to compare against")
    parser.add_argument("--write-expected", action="store_true", help="Explicitly replace the expected output")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.write_expected and args.expected is None:
        parser.error("--write-expected requires --expected")

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
        "metadata": _runtime_metadata(corpus, args.config, args.lexicon),
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
        if args.expected is not None:
            if args.write_expected:
                args.expected.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                report["comparison"] = {"status": "written-explicitly"}
            elif not args.expected.is_file():
                report["comparison"] = {"status": "missing-expected", "path": str(args.expected)}
                report["status"] = "blocked"
            else:
                expected = json.loads(args.expected.read_text(encoding="utf-8"))
                comparisons = _compare_cases(report["cases"], expected.get("cases", []))
                report["comparison"] = {
                    "status": "pass" if all(item["status"] == "pass" for item in comparisons) else "mismatch",
                    "cases": comparisons,
                }
        report.setdefault("status", "executed")

    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 1 if report.get("comparison", {}).get("status") in {"mismatch", "missing-expected"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
