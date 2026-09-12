# Contributing

Run the core checks before submitting changes:

```bash
pytest -q
python -m build
```

Keep backend transformations independently testable with fake providers. Mark live eSpeak tests with `espeak` and `integration`. Do not add Piper as a runtime dependency or copy upstream implementation and data. Update provenance when a compatibility requirement changes.
