---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0002
release_version: v0.1.2
kind: changed
summary: Changed eSpeak backend to delegate discovery and execution to espeakng-runtime
status: accepted
audience: null
scopes: []
source_refs:
  - git:d1707b60b5e5330c3419613a083dd43d2eb45d47
paths:
  - piperg2p/backends/espeak/backend.py
  - piperg2p/backends/espeak/cli.py
  - piperg2p/backends/espeak/discovery.py
  - piperg2p/backends/espeak/native.py
  - pyproject.toml
issues: []
prs: []
sources:
  - git:d1707b60b5e5330c3419613a083dd43d2eb45d47
contributors:
  - "@holgern"
breaking: false
internal: false
order: 2
---
