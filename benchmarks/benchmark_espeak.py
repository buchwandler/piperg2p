"""Compare PiperG2P candidates with an independent eSpeak IPA3 reference."""

from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from piperg2p import BackendUnavailableError, PiperG2PError

if __package__ in {None, ""}:
    from reference.candidate import run_candidate
    from reference.compare import compare_case, comparison_dict, metrics
    from reference.corpus import cases_for_suite, load_corpus
    from reference.espeak import EspeakReference, ReferenceInfrastructureError
    from reference.golden import load as load_golden
    from reference.golden import write as write_golden
    from reference.report import render
else:
    from .reference.candidate import run_candidate
    from .reference.compare import compare_case, comparison_dict, metrics
    from .reference.corpus import cases_for_suite, load_corpus
    from .reference.espeak import EspeakReference, ReferenceInfrastructureError
    from .reference.golden import load as load_golden
    from .reference.golden import write as write_golden
    from .reference.report import render


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument(
        "--suite", choices=("core", "sentences", "compose", "lexicon"), default="core"
    )
    parser.add_argument(
        "--reference-source", choices=("live", "golden"), default="live"
    )
    parser.add_argument(
        "--candidate", choices=("auto", "native", "cli"), default="auto"
    )
    parser.add_argument("--voice", default="en-us")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--corpus", type=Path)
    parser.add_argument("--golden", type=Path)
    parser.add_argument("--write-reference-golden", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--policy",
        choices=("raw-exact", "piper-ipa3", "model-symbol", "model-id"),
        default="piper-ipa3",
    )
    parser.add_argument(
        "--format", choices=("summary", "json", "markdown"), default="summary"
    )
    parser.add_argument("--sample-limit", type=int, default=10)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on", choices=("regression",), default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    default_corpus = {
        "core": "espeak_core.json",
        "sentences": "espeak_sentences.json",
        "compose": "piper_compose.json",
        "lexicon": "espeak_core.json",
    }[args.suite]
    corpus_path = args.corpus or Path(__file__).parent / "data" / default_corpus
    corpus = load_corpus(corpus_path)
    cases = cases_for_suite(corpus, args.suite)
    report: dict[str, Any] = {
        "suite": args.suite,
        "candidate": args.candidate,
        "voice": args.voice,
        "policy": args.policy,
        "reference_source": args.reference_source,
        "profile": corpus.get("profile"),
        "comparisons": [],
    }
    if args.reference_source == "golden":
        golden_path = (
            args.golden
            or Path(__file__).parent / "goldens" / f"espeak_ipa3_{args.voice}.json"
        )
        if not golden_path.is_file():
            report.update(
                {
                    "status": "infrastructure-error",
                    "reference_errors": [f"golden reference not found: {golden_path}"],
                }
            )
            return _finish(report, args)
        golden = load_golden(golden_path)
        reference_outputs = {
            item["id"]: SimpleNamespace(raw=item["raw"])
            for item in golden.get("cases", [])
        }
        missing = [case["id"] for case in cases if case["id"] not in reference_outputs]
        if missing:
            report.update(
                {
                    "status": "infrastructure-error",
                    "reference_errors": [
                        f"golden reference is missing cases: {missing}"
                    ],
                }
            )
            return _finish(report, args)
        report["reference_metadata"] = golden.get("metadata")
    else:
        try:
            reference = EspeakReference()
            reference_outputs = {
                case["id"]: reference.run(
                    case["text"], voice=case.get("voice", args.voice)
                )
                for case in cases
            }
            report["reference_metadata"] = reference.metadata()
        except ReferenceInfrastructureError as exc:
            report.update(
                {"status": "infrastructure-error", "reference_errors": [str(exc)]}
            )
            return _finish(report, args)
    comparison_values = []
    candidate_errors: list[str] = []
    candidate_infrastructure_errors: list[str] = []
    for case in cases:
        try:
            candidate, diagnostics = run_candidate(
                case["text"],
                case.get("voice", args.voice),
                candidate=args.candidate,
                config=args.config,
            )
            result = compare_case(
                case["id"],
                reference_outputs[case["id"]].raw,
                candidate,
                policy=args.policy,
            )
            item = comparison_dict(result)
            item["input"] = case["text"]
            item["candidate_diagnostics"] = diagnostics
            report["comparisons"].append(item)
            comparison_values.append(result)
        except (OSError, PiperG2PError, RuntimeError, ValueError) as exc:
            message = f"{case['id']}: {exc}"
            candidate_errors.append(message)
            if isinstance(exc, BackendUnavailableError):
                candidate_infrastructure_errors.append(message)
            report["comparisons"].append(
                {
                    "case_id": case["id"],
                    "passed": False,
                    "error": str(exc),
                    "candidate_error": True,
                }
            )
            comparison_values.append(
                compare_case(
                    case["id"],
                    reference_outputs[case["id"]].raw,
                    "",
                    policy=args.policy,
                )
            )
    report["metrics"] = metrics(
        comparison_values,
        ids=[],
        candidate_errors=len(candidate_errors),
    )
    if candidate_errors:
        report["candidate_errors"] = candidate_errors
    if candidate_infrastructure_errors:
        report["status"] = "infrastructure-error"
    else:
        report["status"] = (
            "pass" if report["metrics"]["cases_failed"] == 0 else "regression"
        )
    if args.write_reference_golden and args.reference_source == "live":
        golden = (
            args.golden
            or Path(__file__).parent / "goldens" / f"espeak_ipa3_{args.voice}.json"
        )
        write_golden(
            golden,
            {
                "metadata": report.get("reference_metadata"),
                "cases": [
                    {"id": case["id"], "raw": reference_outputs[case["id"]].raw}
                    for case in cases
                ],
            },
            overwrite=args.overwrite,
        )
    return _finish(report, args)


def _finish(report: dict[str, Any], args: argparse.Namespace) -> int:
    output = render(report, args.format)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    if report.get("status") == "infrastructure-error":
        return 2
    return 1 if report.get("status") == "regression" else 0


if __name__ == "__main__":
    raise SystemExit(main())
