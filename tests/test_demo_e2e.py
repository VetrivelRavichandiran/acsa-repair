import json
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results" / "demo"


class TestDemoE2E(unittest.TestCase):

    def test_demo_end_to_end(self):
        # 1. Run the complete demo through the real CLI
        result = subprocess.run(
            [sys.executable, "-m", "acsa_repair", "run-demo"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=(
                "run-demo failed.\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            ),
        )

        # 2. Verify all expected artifacts exist
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

        # 3. Load prioritized results
        prioritized_path = RESULTS_DIR / "prioritized_deltas.json"

        with prioritized_path.open("r", encoding="utf-8") as f:
            prioritized = json.load(f)

        self.assertTrue(
            prioritized,
            "prioritized_deltas.json is empty",
        )

        # 4. Verify top-ranked length divergence
        top = prioritized[0]
        delta = top["delta"]

        self.assertEqual(delta["variable"], "length")
        self.assertEqual(delta["reference"], 24)
        self.assertEqual(delta["candidate"], 1024)

        self.assertEqual(
            delta["alignment_confidence"],
            0.97,
        )

        self.assertEqual(top["score"], 86.33)
        self.assertEqual(top["severity"], "critical")

        # 5. Verify index divergence
        index_deltas = [
            item
            for item in prioritized
            if item["delta"]["variable"] == "index"
        ]

        self.assertTrue(
            index_deltas,
            "Expected index divergence was not found",
        )

        index_delta = index_deltas[0]["delta"]

        self.assertEqual(index_delta["reference"], 23)
        self.assertEqual(index_delta["candidate"], 1023)

        # 6. Verify epistemically separated feedback
        feedback_path = RESULTS_DIR / "feedback.md"
        feedback = feedback_path.read_text(encoding="utf-8")

        self.assertIn("**Observed fact**", feedback)
        self.assertIn("**Supported relevance**", feedback)
        self.assertIn(
            "**Repair guidance (hypothesis)**",
            feedback,
        )

        # 7. Verify policy output
        self.assertIn(
            "**Patch status:** REJECT",
            feedback,
        )


if __name__ == "__main__":
    unittest.main()