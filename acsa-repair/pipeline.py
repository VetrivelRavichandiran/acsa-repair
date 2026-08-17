"""End-to-end trace comparison pipeline."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .alignment import align_events
from .delta import calculate_state_deltas
from .executor import execute, write_execution_metadata
from .feedback import render_feedback
from .prioritization import SecurityFlow, prioritize
from .trace import read_jsonl


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _resolve_command(command: list[str], root: Path) -> list[str]:
    """Resolve explicit benchmark-local executable paths on every platform."""
    if not command:
        raise ValueError("Execution command cannot be empty.")
    resolved = list(command)
    executable = resolved[0]
    if not (executable.startswith(".") or "/" in executable or "\\" in executable):
        return resolved
    path = Path(executable)
    if not path.is_absolute():
        path = root / path
    if os.name == "nt" and path.suffix.lower() != ".exe":
        exe_path = path.with_suffix(".exe")
        if exe_path.exists():
            path = exe_path
    resolved[0] = str(path.resolve())
    return resolved


def analyze_metadata(metadata: dict[str, Any], root: Path, output_dir: Path) -> dict[str, Any]:
    """Analyze parsed metadata rooted at its benchmark directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    reference_run = execute(_resolve_command(list(metadata["reference_command"]), root), root)
    candidate_run = execute(_resolve_command(list(metadata["candidate_command"]), root), root)
    write_execution_metadata(output_dir / "execution.json", reference_run, candidate_run)
    if reference_run.returncode != 0 or candidate_run.returncode != 0:
        raise RuntimeError("Reference or candidate execution failed; inspect execution.json")

    reference_path = output_dir / "reference_trace.jsonl"
    candidate_path = output_dir / "candidate_trace.jsonl"
    reference_path.write_text(reference_run.stdout, encoding="utf-8")
    candidate_path.write_text(candidate_run.stdout, encoding="utf-8")
    pairs = align_events(read_jsonl(reference_path), read_jsonl(candidate_path))
    deltas = calculate_state_deltas(pairs)
    flows = [SecurityFlow.from_dict(item) for item in metadata.get("security_flows", [])]
    ranked = prioritize(deltas, flows, metadata.get("vulnerable_file"), metadata.get("vulnerable_line"))
    _write_json(output_dir / "aligned_pairs.json", [{
        "reference_event": pair.reference.event_id,
        "candidate_event": pair.candidate.event_id,
        "confidence": pair.confidence,
        "rationale": pair.rationale,
    } for pair in pairs])
    _write_json(output_dir / "state_delta_matrix.json", [delta.to_dict() for delta in deltas])
    _write_json(output_dir / "prioritized_deltas.json", [item.to_dict() for item in ranked])
    (output_dir / "feedback.md").write_text(render_feedback(ranked), encoding="utf-8")
    return {"aligned_pairs": len(pairs), "deltas": len(deltas), "ranked": len(ranked), "output_dir": str(output_dir)}


def analyze(metadata_path: Path, output_dir: Path) -> dict[str, Any]:
    """Load metadata from disk and run one reference/candidate comparison."""
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return analyze_metadata(metadata, metadata_path.parent, output_dir)
