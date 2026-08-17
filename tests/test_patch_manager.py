import tempfile
from pathlib import Path
import unittest

from acsa_repair.patch_manager import apply_length_guard_fix, reset_candidate


class PatchManagerTests(unittest.TestCase):
    def test_applies_and_resets_fixture_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            benchmark = Path(directory)
            (benchmark / "candidate_seed").mkdir()
            (benchmark / "candidate").mkdir()
            seed = "int f(void) { if (length > buffer_size) { return 1; } return 0; }\n"
            (benchmark / "candidate_seed" / "parser.c").write_text(seed, encoding="utf-8")
            (benchmark / "candidate" / "parser.c").write_text(seed, encoding="utf-8")
            applied = apply_length_guard_fix(benchmark)
            self.assertTrue(applied.applied)
            self.assertIn("length >= buffer_size", (benchmark / "candidate" / "parser.c").read_text(encoding="utf-8"))
            reset = reset_candidate(benchmark)
            self.assertTrue(reset.applied)
            self.assertEqual(seed, (benchmark / "candidate" / "parser.c").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
