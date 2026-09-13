from __future__ import annotations

import hashlib
import platform
import shutil
import subprocess
from pathlib import Path

from .types import ReferenceOutput


class ReferenceInfrastructureError(RuntimeError):
    pass


class EspeakReference:
    """Independent direct subprocess adapter for eSpeak IPA mode 3."""

    def __init__(self, executable: str | Path | None = None, *, timeout: float | None = None):
        selected = str(executable) if executable else shutil.which("espeak-ng") or shutil.which("espeak")
        if selected is None:
            raise ReferenceInfrastructureError("neither espeak-ng nor espeak is installed")
        self.executable = selected
        self.timeout = timeout
        self.version = self._version()

    def _version(self) -> str | None:
        try:
            process = subprocess.run([self.executable, "--version"], capture_output=True, text=True, check=False)
        except OSError:
            return None
        return (process.stdout or process.stderr).strip()

    def run(self, text: str, *, voice: str) -> ReferenceOutput:
        command = [self.executable, "-q", "--ipa=3", "-v", voice, "--stdin"]
        try:
            process = subprocess.run(
                command,
                input=text,
                encoding="utf-8",
                errors="strict",
                capture_output=True,
                check=False,
                timeout=self.timeout,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise ReferenceInfrastructureError(f"direct eSpeak invocation failed: {exc}") from exc
        if process.returncode:
            raise ReferenceInfrastructureError(
                f"direct eSpeak exited {process.returncode}: {process.stderr.strip()}"
            )
        raw = process.stdout.rstrip("\r\n")
        return ReferenceOutput(
            text=text,
            raw=raw,
            canonical=canonicalize(raw),
            voice=voice,
            metadata=self.metadata(),
        )

    def metadata(self) -> dict[str, object]:
        path = Path(self.executable)
        return {
            "executable": self.executable,
            "version": self.version,
            "platform": platform.platform(),
            "command_shape": ["<executable>", "-q", "--ipa=3", "-v", "<voice>", "--stdin"],
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        }


def canonicalize(value: str) -> str:
    import unicodedata

    return unicodedata.normalize("NFD", value)
