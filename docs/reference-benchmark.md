# Reference benchmark

`benchmarks/data/core.json` records a small pinned Phase 1 corpus identity and its comparison policies. Run the metadata inspection with:

```bash
python benchmarks/benchmark_reference.py
```

Reference Piper execution belongs in a separate development environment or subprocess. It is not a runtime dependency. Golden outputs must be refreshed explicitly, with a pinned commit, dependency versions, voice configuration hash, and human review. The current corpus intentionally reports metadata only until that isolated provider is provisioned.
