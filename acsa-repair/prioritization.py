"""Security-aware ranking for State-Delta Matrix entries."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .delta import DiffType, StateDelta


@dataclass(frozen=True)
class SecurityFlow:
    source: str
    transforms: tuple[str, ...]
    sink: str
    severity: str = "high"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SecurityFlow":
        return cls(str(data["source"]), tuple(data.get("transforms", [])), str(data["sink"]), str(data.get("severity", "high")))

    @property
    def variables(self) -> set[str]:
        return {self.source, *self.transforms}


@dataclass(frozen=True)
class PrioritizedDelta:
    delta: StateDelta
    score: float
    severity: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        output = asdict(self)
        output["delta"]["diff_type"] = self.delta.diff_type.value
        return output


def _divergence(delta: StateDelta) -> float:
    if delta.diff_type == DiffType.NUMERIC:
        baseline = max(1.0, abs(float(delta.reference or 0)))
        return min(30.0, 10.0 * abs(float(delta.difference)) / baseline)
    if delta.diff_type == DiffType.CONTROL_FLOW:
        return 22.0
    if delta.diff_type in {DiffType.BOOLEAN, DiffType.POINTER, DiffType.TYPE, DiffType.MISSING}:
        return 16.0
    return 8.0


def prioritize(
    deltas: Iterable[StateDelta],
    flows: Iterable[SecurityFlow],
    vulnerable_file: str | None = None,
    vulnerable_line: int | None = None,
) -> list[PrioritizedDelta]:
    flows = list(flows)
    ranked: list[PrioritizedDelta] = []
    severity_weight = {"low": 5.0, "medium": 12.0, "high": 22.0, "critical": 32.0}
    for delta in deltas:
        score = _divergence(delta)
        reasons = [f"typed divergence: {delta.diff_type.value}"]
        matches = [flow for flow in flows if delta.variable in flow.variables]
        if matches:
            flow = max(matches, key=lambda item: severity_weight.get(item.severity.lower(), 22.0))
            score += severity_weight.get(flow.severity.lower(), 22.0)
            reasons.append(f"security flow: {flow.source} → {' → '.join(flow.transforms)} → {flow.sink}")
        if delta.control_flow_changed:
            score += 12.0
            reasons.append("control-flow path differs")
        if vulnerable_file and vulnerable_line and delta.reference_location.startswith(f"{vulnerable_file}:"):
            line = int(delta.reference_location.rsplit(":", 1)[1])
            proximity = max(0.0, 15.0 - abs(line - vulnerable_line))
            if proximity:
                score += proximity
                reasons.append("near reported vulnerable location")
        score *= delta.alignment_confidence
        severity = "critical" if score >= 50 else "high" if score >= 32 else "medium" if score >= 16 else "low"
        ranked.append(PrioritizedDelta(delta, round(score, 2), severity, tuple(reasons)))
    return sorted(ranked, key=lambda item: item.score, reverse=True)
