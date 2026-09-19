---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0003
release_version: v0.1.5
kind: changed
summary:
  Changed CLI clause batching to preserve multiline clause bodies and raised
  the espeakng-runtime minimum to 0.1.5
status: accepted
audience: null
scopes: []
source_refs:
  - git:33ba13d5f1b849f6492c96f6d8b014d2451ffab3
paths:
  - docs/espeak.md
  - piperg2p/codec.py
  - pyproject.toml
  - tests/test_clause_backend.py
  - tests/test_dependency_contract.py
  - tests/test_espeak_exact_contract.py
  - tests/test_real_optional_integration.py
issues: []
prs: []
sources:
  - git:33ba13d5f1b849f6492c96f6d8b014d2451ffab3
contributors:
  - "@holgern"
breaking: false
internal: false
order: 3
---
