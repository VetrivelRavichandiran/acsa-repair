"""Small, local candidate-version manager for reproducible repair experiments."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil


@dataclass(frozen=True)
class PatchResult:
    applied: bool
    message: str


def reset_candidate(benchmark_dir: Path) -> PatchResult:
    """Restore the supplied intentionally flawed candidate source."""
    template = benchmark_dir / "candidate_seed" / "parser.c"
    destination = benchmark_dir / "candidate" / "parser.c"
    if not template.exists():
        return PatchResult(False, f"Seed source not found: {template}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, destination)
    binary = benchmark_dir / "candidate" / "parser"
    if binary.exists():
        binary.unlink()
    return PatchResult(True, "Candidate restored to the initial flawed version.")


def apply_length_guard_fix(benchmark_dir: Path) -> PatchResult:
    """Apply a deliberately narrow, inspectable fix for the bundled fixture."""
    source = benchmark_dir / "candidate" / "parser.c"
    if not source.exists():
        return PatchResult(False, f"Candidate source not found: {source}")
    text = source.read_text(encoding="utf-8")
    old = "if (length > buffer_size) {"
    new = "if (length >= buffer_size) {"
    if old not in text:
        return PatchResult(False, "Expected flawed guard was not found; no file was changed.")
    source.write_text(text.replace(old, new, 1), encoding="utf-8")
    binary = benchmark_dir / "candidate" / "parser"
    if binary.exists():
        binary.unlink()
    return PatchResult(True, "Applied candidate fix: reject length >= buffer_size.")
