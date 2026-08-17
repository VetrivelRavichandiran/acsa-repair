"""Runtime trace schema, validation, and JSONL I/O."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Location:
    file: str
    line: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Location":
        return cls(file=str(data["file"]), line=int(data["line"]))


@dataclass(frozen=True)
class TypedValue:
    type: str
    value: Any

    @classmethod
    def from_raw(cls, raw: Any) -> "TypedValue":
        if isinstance(raw, dict) and "type" in raw and "value" in raw:
            return cls(type=str(raw["type"]), value=raw["value"])
        return cls(type=type(raw).__name__, value=raw)


@dataclass(frozen=True)
class StateEvent:
    event_id: int
    function: str
    location: Location
    variables: dict[str, TypedValue]
    iteration: int = 0
    call_stack: tuple[str, ...] = ()
    expressions: dict[str, Any] = field(default_factory=dict)
    control_flow: dict[str, Any] = field(default_factory=dict)

    @property
    def alignment_key(self) -> tuple[str, tuple[str, ...], int, int]:
        """Stable cross-version anchor; source lines are intentionally excluded."""
        return (self.function, self.call_stack, self.iteration, self.event_id)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StateEvent":
        required = {"event_id", "function", "location", "variables"}
        missing = required.difference(data)
        if missing:
            raise ValueError(f"Trace event is missing required keys: {sorted(missing)}")
        variables = {name: TypedValue.from_raw(value) for name, value in data["variables"].items()}
        return cls(
            event_id=int(data["event_id"]),
            function=str(data["function"]),
            location=Location.from_dict(data["location"]),
            variables=variables,
            iteration=int(data.get("iteration", 0)),
            call_stack=tuple(data.get("call_stack", [])),
            expressions=dict(data.get("expressions", {})),
            control_flow=dict(data.get("control_flow", {})),
        )


def read_jsonl(path: Path) -> list[StateEvent]:
    events: list[StateEvent] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            events.append(StateEvent.from_dict(json.loads(line)))
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            raise ValueError(f"Invalid trace event at {path}:{line_number}: {exc}") from exc
    return events


def event_to_dict(event: StateEvent) -> dict[str, Any]:
    return asdict(event)


def write_jsonl(path: Path, events: Iterable[StateEvent]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event_to_dict(event), sort_keys=True) + "\n")
