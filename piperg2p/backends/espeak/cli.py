from __future__ import annotations

import subprocess
from dataclasses import dataclass

from ...diagnostics import BackendDiagnostics
from ...errors import PhonemizationError
from .clauses import Clause, compose_clauses, split_cli_clauses
from .discovery import discover


@dataclass
class EspeakCliBackend:
    executable: str | None = None
    vowel_clusters: frozenset[tuple[str, ...]] = frozenset()
    timeout: float | None = None
    data_path: str | None = None

    def __post_init__(self) -> None:
        paths = discover(executable=self.executable, data=self.data_path)
        self.executable = paths.executable
        self.data_path = paths.data
        self.discovery_source = paths.source
        self._diagnostics = BackendDiagnostics(
            requested_mode="cli",
            implementation="cli",
            executable=self.executable,
            data_path=self.data_path,
            parity="best-effort",
            discovery_source=self.discovery_source,
        )

    @property
    def diagnostics(self) -> BackendDiagnostics:
        return self._diagnostics

    def _ipa(self, text: str, voice: str) -> str:
        if not text.strip():
            return ""
        try:
            process = subprocess.run(
                [self.executable or "", "-q", "--ipa=3", "-v", voice, "--stdin"],
                # eSpeak only flushes the final clause completely when stdin
                # contains a line terminator. Without one, some versions
                # return a truncated pronunciation for the final word.
                input=text if text.endswith("\n") else f"{text}\n",
                encoding="utf-8",
                errors="strict",
                capture_output=True,
                check=False,
                timeout=self.timeout,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise PhonemizationError(f"eSpeak CLI invocation failed: {exc}") from exc
        if process.returncode:
            raise PhonemizationError(
                f"eSpeak failed ({process.returncode}): {process.stderr.strip()}"
            )
        return process.stdout.strip("\r\n ")

    def phonemize(self, text: str, *, voice: str) -> list[list[str]]:
        if not text:
            return []
        clauses = [
            Clause(self._ipa(body, voice), terminator, sentence_end)
            for body, terminator, sentence_end in split_cli_clauses(text)
        ]
        return compose_clauses(clauses, self.vowel_clusters)

    def close(self) -> None:
        return None
