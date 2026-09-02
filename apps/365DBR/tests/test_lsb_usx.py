import unittest
from pathlib import Path

from lsb_usx import extract_usx


JOB_USX = Path(__file__).parents[1] / "data" / "LSB" / "release" / "USX_1" / "JOB.usx"


class LsbUsxTests(unittest.TestCase):
    def test_job_41_1_through_8_survive_milestone_boundaries(self):
        verses = extract_usx(JOB_USX)
        for number in range(1, 9):
            verse = verses[f"JOB.41.{number}"]
            self.assertTrue(verse)
            self.assertNotIn("Lit", verse)
            self.assertNotIn("Ch 40:25 in Heb", verse)

        self.assertIn("Can you draw out Leviathan", verses["JOB.41.1"])
        self.assertIn("Remember the battle", verses["JOB.41.8"])


if __name__ == "__main__":
    unittest.main()
