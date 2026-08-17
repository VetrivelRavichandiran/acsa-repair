"""Factual cognitive interpretation and LLM-ready feedback rendering."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .prioritization import PrioritizedDelta


def render_feedback(ranked: Iterable[PrioritizedDelta], limit: int = 10) -> str:
    selected = list(ranked)[:limit]
    status = "REJECT" if any(item.severity in {"critical", "high"} for item in selected) else "REPAIR"
    lines = [
        "# ACSA Verification Report", "", f"**Patch status:** {status}", "",
        "This report separates direct observations from hypotheses. It does not establish causality by itself.", "",
    ]
    if not selected:
        return "\n".join(lines + ["No aligned state divergences were observed."])
    for index, item in enumerate(selected, start=1):
        delta = item.delta
        lines.extend([
            f"## {index}. {item.severity.upper()} — `{delta.variable}`", "",
            "**Observed fact**",  
            f"- Aligned execution: `{delta.function}` at reference `{delta.reference_location}` and candidate `{delta.candidate_location}`.",
            f"- `{delta.variable}` changed from `{delta.reference!r}` to `{delta.candidate!r}` ({delta.diff_type.value}; difference: `{delta.difference!r}`).",
            f"- Alignment confidence: `{delta.alignment_confidence:.2f}`; priority score: `{item.score:.2f}`.",
            "", "**Supported relevance**",
        ])
        lines.extend(f"- {reason}." for reason in item.reasons)
        lines.extend([
            "", "**Repair guidance (hypothesis)**",
            f"- Re-examine how `{delta.variable}` is computed or propagated before preserving the candidate behavior.",
            "- Preserve intended functionality; do not suppress the affected operation merely to remove the signal.", "",
        ])
    return "\n".join(lines)


def summary_by_severity(ranked: Iterable[PrioritizedDelta]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for item in ranked:
        counts[item.severity] += 1
    return dict(counts)
