"""CSV-driven batch analysis and aggregate result generation."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import shutil
from typing import Any

from .pipeline import analyze_metadata


SAFE_NAME = re.compile(r"[^A-Za-z0-9_.-]+")


def _safe_name(value: str, row_number: int) -> str:
    cleaned = SAFE_NAME.sub("_", value.strip()).strip("._")
    return cleaned or f"case_{row_number}"


def _read_cases(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "input" not in reader.fieldnames:
            raise ValueError("Input CSV must have an 'input' column. Optional columns: case_id, enabled.")
        cases: list[dict[str, str]] = []
        for row_number, row in enumerate(reader, start=2):
            raw_input = (row.get("input") or "").strip()
            enabled = (row.get("enabled") or "true").strip().lower()
            if enabled in {"false", "0", "no", "n"}:
                continue
            if not raw_input:
                raise ValueError(f"CSV row {row_number} has an empty input value.")
            case_id = _safe_name(row.get("case_id") or f"case_{row_number - 1}", row_number)
            cases.append({"case_id": case_id, "input": raw_input})
    if not cases:
        raise ValueError("The CSV did not contain any enabled test cases.")
    return cases


def _commands_for_input(metadata: dict[str, Any], input_value: str) -> dict[str, Any]:
    updated = dict(metadata)
    updated["reference_command"] = [*metadata["reference_command"][:-1], input_value]
    updated["candidate_command"] = [*metadata["candidate_command"][:-1], input_value]
    return updated


def analyze_csv(metadata_path: Path, csv_path: Path, output_dir: Path) -> dict[str, Any]:
    """Run the same reference/candidate comparison for every enabled CSV row."""
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    cases = _read_cases(csv_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    case_root = output_dir / "cases"
    if case_root.exists():
        shutil.rmtree(case_root)
    case_root.mkdir(parents=True)

    rows: list[dict[str, Any]] = []
    for ordinal, case in enumerate(cases, start=1):
        case_dir = case_root / f"{ordinal:03d}_{case['case_id']}"
        case_dir.mkdir(parents=True)
        case_metadata = _commands_for_input(metadata, case["input"])
        # Keep execution rooted in the benchmark, not the results folder.
        # This makes reference/candidate executable paths resolve correctly.
        try:
            result = analyze_metadata(case_metadata, metadata_path.parent, case_dir)
            status = "PASS" if result["deltas"] == 0 else "DIVERGENCE"
            error = ""
        except (RuntimeError, ValueError) as exc:
            result = {"aligned_pairs": 0, "deltas": 0, "ranked": 0, "output_dir": str(case_dir)}
            status = "ERROR"
            error = str(exc)
        rows.append({
            "case_number": ordinal,
            "case_id": case["case_id"],
            "input": case["input"],
            "input_length": len(case["input"]),
            "status": status,
            "aligned_pairs": result["aligned_pairs"],
            "deltas": result["deltas"],
            "ranked": result["ranked"],
            "output_dir": result["output_dir"],
            "error": error,
        })

    summary_path = output_dir / "summary.csv"
    fieldnames = list(rows[0])
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts = {"total": len(rows), "pass": 0, "divergence": 0, "error": 0}
    for row in rows:
        counts[row["status"].lower()] += 1
    report_lines = [
        "# ACSA Batch Analysis Report", "",
        f"**Input CSV:** `{csv_path.name}`", "",
        "| Case | Input length | Status | Deltas | Ranked |", "|---|---:|---|---:|---:|",
    ]
    report_lines.extend(
        f"| {row['case_id']} | {row['input_length']} | {row['status']} | {row['deltas']} | {row['ranked']} |"
        for row in rows
    )
    report_lines.extend([
        "", "## Totals", "",
        f"- Total cases: {counts['total']}",
        f"- Matching reference behavior: {counts['pass']}",
        f"- Runtime divergences: {counts['divergence']}",
        f"- Execution errors: {counts['error']}",
        "", "Per-case traces, delta matrices, and feedback reports are in `cases/`.",
    ])
    (output_dir / "batch_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return {**counts, "output_dir": str(output_dir), "summary_csv": str(summary_path)}
