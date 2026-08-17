"""Controlled command execution for trace-producing programs."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
from typing import Any


@dataclass(frozen=True)
class ExecutionResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


def execute(command: list[str], cwd: Path, timeout_seconds: int = 30) -> ExecutionResult:
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout_seconds, check=False)
        return ExecutionResult(command, completed.returncode, completed.stdout, completed.stderr)
    except subprocess.TimeoutExpired as exc:
        return ExecutionResult(command, -1, exc.stdout or "", exc.stderr or "", True)


def write_execution_metadata(path: Path, reference: ExecutionResult, candidate: ExecutionResult) -> None:
    path.write_text(json.dumps({"reference": asdict(reference), "candidate": asdict(candidate)}, indent=2), encoding="utf-8")
