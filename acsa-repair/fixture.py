"""Build and run helpers for the bundled C CWE-787 fixture."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

from .pipeline import analyze


def build_c_fixture(fixture: Path) -> None:
    """Compile reference and candidate sources with the active Python interpreter."""
    compiler = shutil.which("clang") or shutil.which("gcc")
    if not compiler:
        raise RuntimeError("No C compiler found. Install clang or gcc and retry.")
    subprocess.run([sys.executable, "build.py"], cwd=fixture, check=True)


def build_and_analyze_c_fixture(workspace: Path) -> dict:
    fixture = workspace / "benchmarks" / "cwe787_length_guard"
    build_c_fixture(fixture)
    output = workspace / "results" / "cwe787_length_guard"
    if output.exists():
        shutil.rmtree(output)
    return analyze(fixture / "metadata.json", output)
