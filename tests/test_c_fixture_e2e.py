import json
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results" / "cwe787_length_guard"


class TestCFixtureE2E(unittest.TestCase):

    def test_c_fixture_end_to_end(self):
        # 1. Run the complete C benchmark through the real CLI
        result = subprocess.run(
            [sys.executable, "-m", "acsa_repair", "run-c-fixture"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=(
                "run-c-fixture failed.\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            ),
        )

        # 2. Verify expected artifacts
        expected_files = [
            "execution.json",
            "reference_trace.jsonl",
            "candidate_trace.jsonl",
            "aligned_pairs.json",
            "state_delta_matrix.json",
            "prioritized_deltas.json",
            "feedback.md",
        ]

        for filename in expected_files:
            path = RESULTS_DIR / filename
            self.assertTrue(
                path.exists(),
                f"Missing expected artifact: {path}",
            )

        # 3. Verify both executions succeeded
        execution = json.loads(
            (RESULTS_DIR / "execution.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            execution["reference"]["returncode"],
            0,
            "Reference execution failed",
        )

        self.assertEqual(
            execution["candidate"]["returncode"],
            0,
            "Candidate execution failed",
        )

        # 4. Verify trace alignment
        aligned = json.loads(
            (RESULTS_DIR / "aligned_pairs.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            len(aligned),
            2,
            "Expected two aligned execution events",
        )

        # 5. Verify that ACSA detected the behavioral divergence
        prioritized = json.loads(
            (RESULTS_DIR / "prioritized_deltas.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertTrue(
            prioritized,
            "Expected at least one prioritized delta",
        )

        # 6. Verify the detected control-flow divergence
        top = prioritized[0]
        delta = top["delta"]

        self.assertEqual(
            delta["variable"],
            "__control_flow__",
        )

        self.assertEqual(
            delta["reference"]["branch"],
            "reject_oversized",
        )

        self.assertEqual(
            delta["candidate"]["branch"],
            "copy_would_overflow",
        )

        self.assertEqual(
            delta["diff_type"],
            "control_flow",
        )

        self.assertTrue(
            delta["control_flow_changed"],
        )

        # 7. Verify prioritization
        self.assertEqual(
            top["severity"],
            "high",
        )

        self.assertGreater(
            top["score"],
            0,
        )

        # 8. Verify final verification decision
        feedback = (
            RESULTS_DIR / "feedback.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "**Patch status:** REJECT",
            feedback,
        )


if __name__ == "__main__":
    unittest.main()