from __future__ import annotations

from typing import Protocol

from .clauses import Clause


class ClauseProvider(Protocol):
    def clauses(self, text: str, voice: str) -> list[Clause]: ...
