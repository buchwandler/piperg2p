# Contributing

Install development and documentation dependencies, then run the same checks used to protect the public API and docs site:

```bash
python -m pip install -e ".[dev,docs]"
python -m pytest -q
ruff check .
python docs/make.py html
python -m build
```

Update documentation when public behavior changes and update executable examples when the high-level facade changes. Keep fake-provider backend tests independent from live eSpeak; mark tests that need eSpeak or other external resources appropriately. Do not add Piper, Spokenform, or Numeralform as PiperG2P dependencies. Keep optional integrations optional and update compatibility/provenance pages when those claims change.

Do not edit the generated [changelog](changelog.md) by hand. Update the releaseledger source record and regenerate it through the project workflow.
