"""Compile the C reference and candidate fixture with an available local compiler."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
compiler = shutil.which("clang") or shutil.which("gcc")
if not compiler:
    raise SystemExit("No C compiler was found. Install clang or gcc, then rerun this command.")

for variant in ("reference", "candidate"):
    source = ROOT / variant / "parser.c"
    binary = ROOT / variant / "parser"
    command = [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O0", "-g", str(source), "-o", str(binary)]
    print("Building:", " ".join(command))
    subprocess.run(command, check=True)
print("Built reference/parser and candidate/parser using", compiler)
