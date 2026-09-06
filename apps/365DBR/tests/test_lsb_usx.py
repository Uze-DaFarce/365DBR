import tempfile
import unittest
from pathlib import Path

from lsb_usx import extract_usx


JOB_USX = Path(__file__).parents[1] / "data" / "LSB" / "release" / "USX_1" / "JOB.usx"
SNG_USX = Path(__file__).parents[1] / "data" / "LSB" / "release" / "USX_1" / "SNG.usx"

HEADING_USX = """<?xml version="1.0" encoding="UTF-8"?>
<usx version="3.0">
  <book code="GEN" style="id">GEN</book>
  <chapter number="1" style="c" sid="GEN 1"/>
  <para style="s"><char style="it">Creation</char></para>
  <para style="p"><verse number="1" style="v" sid="GEN 1:1"/>In the beginning God created the heavens and the earth.<verse eid="GEN 1:1"/></para>
  <para style="p"><verse number="2" style="v" sid="GEN 1:2"/>And the earth was formless and void.</para>
  <para style="sp">God</para>
  <para style="q" vid="GEN 1:2">Let there be light.<verse eid="GEN 1:2"/></para>
  <chapter eid="GEN 1"/>
</usx>
"""


class LsbUsxTests(unittest.TestCase):
    def test_job_41_1_through_8_survive_milestone_boundaries(self):
        verses, _titles = extract_usx(JOB_USX)
        for number in range(1, 9):
            verse = verses[f"JOB.41.{number}"]
            self.assertTrue(verse)
            self.assertNotIn("Lit", verse)
            self.assertNotIn("Ch 40:25 in Heb", verse)

        self.assertIn("Can you draw out Leviathan", verses["JOB.41.1"])
        self.assertIn("Remember the battle", verses["JOB.41.8"])

    def test_title_paras_do_not_bleed_into_verse_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "GEN.usx"
            path.write_text(HEADING_USX, encoding="utf-8")
            verses, titles = extract_usx(path)

        self.assertEqual(verses["GEN.1.1"], "In the beginning God created the heavens and the earth.")
        self.assertNotIn("Creation", verses["GEN.1.1"])
        self.assertIn("Creation", titles["GEN.1.1"])
        self.assertIn("formless and void", verses["GEN.1.2"])
        self.assertIn("Let there be light", verses["GEN.1.2"])
        self.assertNotIn("God", verses["GEN.1.2"])
        self.assertIn("God", titles["GEN.1.2"])

    def test_chapter_heading_attaches_to_next_verse_not_previous(self):
        verses, titles = extract_usx(SNG_USX)
        self.assertNotIn("Troubled Dream", verses["SNG.2.17"])
        self.assertFalse(any("Troubled Dream" in t for t in titles.get("SNG.2.17", [])))
        self.assertTrue(any("Troubled Dream" in t for t in titles.get("SNG.3.1", [])))
        self.assertIn("On my bed", verses["SNG.3.1"])


if __name__ == "__main__":
    unittest.main()
