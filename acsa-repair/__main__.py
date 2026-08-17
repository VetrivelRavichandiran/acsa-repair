"""Command-line entry point."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

from .pipeline import analyze


def demo(workspace: Path) -> dict:
    source = workspace / "benchmarks" / "example_001"
    output = workspace / "results" / "demo"
    if output.exists():
        shutil.rmtree(output)
    return analyze(source / "metadata.json", output)


def main() -> None:
    parser = argparse.ArgumentParser(description="ACSA-Repair state-delta MVP")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("run-demo", help="run the bundled synthetic trace demo")
    subcommands.add_parser("run-c-fixture", help="build and analyze the real C CWE-787 fixture")
    subcommands.add_parser("fix-c-fixture", help="apply the narrow length-guard fix to the C candidate")
    subcommands.add_parser("reset-c-fixture", help="restore the intentionally flawed C candidate")
    batch_parser = subcommands.add_parser("analyze-csv", help="analyze one C fixture input per CSV row")
    batch_parser.add_argument("--csv", required=True, type=Path, help="CSV with required input column")
    batch_parser.add_argument("--metadata", type=Path, help="benchmark metadata; defaults to the C fixture")
    batch_parser.add_argument("--output", type=Path, help="results directory; defaults to results/cwe787_csv")
    analyze_parser = subcommands.add_parser("analyze", help="compare two trace-producing commands")
    analyze_parser.add_argument("--metadata", required=True, type=Path)
    analyze_parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    workspace = Path(__file__).resolve().parent.parent
    if args.command == "run-demo":
        result = demo(workspace)
    elif args.command == "run-c-fixture":
        from .fixture import build_and_analyze_c_fixture
        result = build_and_analyze_c_fixture(workspace)
    elif args.command == "fix-c-fixture":
        from .patch_manager import apply_length_guard_fix
        result = apply_length_guard_fix(workspace / "benchmarks" / "cwe787_length_guard").__dict__
    elif args.command == "reset-c-fixture":
        from .patch_manager import reset_candidate
        result = reset_candidate(workspace / "benchmarks" / "cwe787_length_guard").__dict__
    elif args.command == "analyze-csv":
        from .batch import analyze_csv
        from .fixture import build_c_fixture
        fixture = workspace / "benchmarks" / "cwe787_length_guard"
        build_c_fixture(fixture)
        metadata = (args.metadata or fixture / "metadata.json").resolve()
        output = (args.output or workspace / "results" / "cwe787_csv").resolve()
        result = analyze_csv(metadata, args.csv.resolve(), output)
    else:
        result = analyze(args.metadata.resolve(), args.output.resolve())
    print(f"ACSA analysis complete: {result}")


if __name__ == "__main__":
    main()
