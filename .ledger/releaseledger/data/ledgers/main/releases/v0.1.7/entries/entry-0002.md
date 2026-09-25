---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0002
release_version: v0.1.7
kind: changed
summary:
  Improved CLI sentence splitting with Phrasplit while preserving punctuation
  and language-specific grouping
status: accepted
audience: null
scopes: []
source_refs:
  - git:82cf9008469efe3418f752d94ab74d2629110e19
paths:
  - docs/espeak.md
  - piperg2p/backends/espeak/clauses.py
  - pyproject.toml
  - tests/test_clause_backend.py
  - tests/test_dependency_contract.py
  - tests/test_espeak_exact_contract.py
issues: []
prs: []
sources:
  - git:82cf9008469efe3418f752d94ab74d2629110e19
contributors:
  - "@holgern"
breaking: false
internal: false
order: 2
---
