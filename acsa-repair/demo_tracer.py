"""Deterministic synthetic tracer used only to validate the MVP pipeline."""
from __future__ import annotations

import json
import sys


def event(event_id: int, line: int, variables: dict, branch: str) -> dict:
    return {
        "event_id": event_id,
        "function": "parse_input",
        "location": {"file": "parser.c", "line": line},
        "iteration": 0,
        "call_stack": ["main", "parse_input"],
        "variables": {name: {"type": "int", "value": value} for name, value in variables.items()},
        "control_flow": {"branch": branch},
    }


def main() -> None:
    mode = sys.argv[1]
    if mode == "reference":
        trace = [
            event(1, 180, {"input_length": 24, "length": 24}, "read_input"),
            event(2, 183, {"length": 24, "buffer_size": 32, "index": 23}, "within_bounds"),
            event(3, 184, {"length": 24, "buffer_size": 32}, "copy_allowed"),
        ]
    elif mode == "candidate":
        trace = [
            event(1, 180, {"input_length": 24, "length": 1024}, "read_input"),
            event(2, 187, {"length": 1024, "buffer_size": 32, "index": 1023}, "out_of_bounds"),
            event(3, 188, {"length": 1024, "buffer_size": 32}, "copy_attempted"),
        ]
    else:
        raise SystemExit("mode must be reference or candidate")
    for item in trace:
        print(json.dumps(item))


if __name__ == "__main__":
    main()
