"""Typed State-Delta Matrix generation."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from numbers import Number
from typing import Any, Iterable

from .alignment import AlignedPair
from .trace import TypedValue


class DiffType(StrEnum):
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    STRING = "string"
    POINTER = "pointer"
    TYPE = "type"
    MISSING = "missing"
    CONTROL_FLOW = "control_flow"


@dataclass(frozen=True)
class StateDelta:
    function: str
    variable: str
    reference_location: str
    candidate_location: str
    reference: Any
    candidate: Any
    diff_type: DiffType
    difference: Any
    alignment_confidence: float
    control_flow_changed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _is_pointer(value: TypedValue) -> bool:
    return "pointer" in value.type.lower() or (isinstance(value.value, str) and value.value.startswith("0x"))


def _classify(reference: TypedValue | None, candidate: TypedValue | None) -> tuple[DiffType, Any]:
    if reference is None or candidate is None:
        return DiffType.MISSING, "missing in reference" if reference is None else "missing in candidate"
    if reference.type != candidate.type:
        return DiffType.TYPE, {"reference_type": reference.type, "candidate_type": candidate.type}
    if isinstance(reference.value, bool) and isinstance(candidate.value, bool):
        return DiffType.BOOLEAN, {"reference": reference.value, "candidate": candidate.value}
    if isinstance(reference.value, Number) and isinstance(candidate.value, Number):
        return DiffType.NUMERIC, candidate.value - reference.value
    if _is_pointer(reference) or _is_pointer(candidate):
        return DiffType.POINTER, {"reference": reference.value, "candidate": candidate.value}
    return DiffType.STRING, {"reference": reference.value, "candidate": candidate.value}


def calculate_state_deltas(pairs: Iterable[AlignedPair]) -> list[StateDelta]:
    matrix: list[StateDelta] = []
    for pair in pairs:
        reference, candidate = pair.reference, pair.candidate
        control_flow_changed = reference.control_flow != candidate.control_flow
        names = sorted(set(reference.variables) | set(candidate.variables))
        for name in names:
            before, after = reference.variables.get(name), candidate.variables.get(name)
            if before == after:
                continue
            diff_type, difference = _classify(before, after)
            matrix.append(StateDelta(
                function=reference.function,
                variable=name,
                reference_location=f"{reference.location.file}:{reference.location.line}",
                candidate_location=f"{candidate.location.file}:{candidate.location.line}",
                reference=None if before is None else before.value,
                candidate=None if after is None else after.value,
                diff_type=diff_type,
                difference=difference,
                alignment_confidence=pair.confidence,
                control_flow_changed=control_flow_changed,
            ))
        if control_flow_changed:
            matrix.append(StateDelta(
                function=reference.function,
                variable="__control_flow__",
                reference_location=f"{reference.location.file}:{reference.location.line}",
                candidate_location=f"{candidate.location.file}:{candidate.location.line}",
                reference=reference.control_flow,
                candidate=candidate.control_flow,
                diff_type=DiffType.CONTROL_FLOW,
                difference={"reference": reference.control_flow, "candidate": candidate.control_flow},
                alignment_confidence=pair.confidence,
                control_flow_changed=True,
            ))
    return matrix
