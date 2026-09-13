from pathlib import Path

EXAMPLES = {
    "cache_and_batch.py",
    "debug_mode_demo.py",
    "demo_both_features.py",
    "espeak_fallback.py",
    "explicit_language_spans.py",
    "external_annotations.py",
    "lexicon_selection.py",
    "marker_demo.py",
    "mixed_language_auto.py",
    "new_api_demo.py",
    "result_inspection.py",
    "structured_stress.py",
}


def test_all_sibling_examples_exist_and_compile():
    root = Path(__file__).parents[1] / "examples"
    assert {path.name for path in root.glob("*.py") if path.name != "_common.py"} == EXAMPLES
    for name in EXAMPLES:
        compile((root / name).read_text(encoding="utf-8"), str(root / name), "exec")


def test_examples_use_explicit_config_loader():
    root = Path(__file__).parents[1] / "examples"
    for name in EXAMPLES - {"lexicon_selection.py"}:
        assert "--config" in (root / name).read_text(encoding="utf-8") or "parser(" in (root / name).read_text(encoding="utf-8")
