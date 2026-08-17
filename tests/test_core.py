import unittest

from acsa_repair.alignment import align_events
from acsa_repair.delta import DiffType, calculate_state_deltas
from acsa_repair.prioritization import SecurityFlow, prioritize
from acsa_repair.trace import StateEvent


def state(event_id, line, variables, branch="ok"):
    return StateEvent.from_dict({
        "event_id": event_id,
        "function": "parse_input",
        "location": {"file": "parser.c", "line": line},
        "iteration": 0,
        "call_stack": ["main", "parse_input"],
        "variables": variables,
        "control_flow": {"branch": branch},
    })


class AcsaCoreTests(unittest.TestCase):
    def test_alignment_survives_line_shift(self):
        reference = state(2, 183, {"length": {"type": "int", "value": 24}})
        candidate = state(2, 187, {"length": {"type": "int", "value": 1024}})
        pairs = align_events([reference], [candidate])
        self.assertEqual(1, len(pairs))
        self.assertGreater(pairs[0].confidence, 0.8)

    def test_delta_engine_emits_typed_numeric_and_control_flow_deltas(self):
        reference = state(2, 183, {"length": {"type": "int", "value": 24}}, "within_bounds")
        candidate = state(2, 187, {"length": {"type": "int", "value": 1024}}, "out_of_bounds")
        deltas = calculate_state_deltas(align_events([reference], [candidate]))
        numeric = next(item for item in deltas if item.variable == "length")
        self.assertEqual(DiffType.NUMERIC, numeric.diff_type)
        self.assertEqual(1000, numeric.difference)
        self.assertTrue(numeric.control_flow_changed)
        self.assertTrue(any(item.diff_type == DiffType.CONTROL_FLOW for item in deltas))

    def test_security_flow_prioritizes_length_over_unrelated_counter(self):
        reference = state(2, 183, {
            "length": {"type": "int", "value": 24},
            "counter": {"type": "int", "value": 17},
        })
        candidate = state(2, 187, {
            "length": {"type": "int", "value": 1024},
            "counter": {"type": "int", "value": 18},
        })
        deltas = calculate_state_deltas(align_events([reference], [candidate]))
        ranked = prioritize(deltas, [SecurityFlow("length", ("buffer_size",), "memcpy", "critical")], "parser.c", 183)
        self.assertEqual("length", ranked[0].delta.variable)
        self.assertIn("security flow", " ".join(ranked[0].reasons))


if __name__ == "__main__":
    unittest.main()
