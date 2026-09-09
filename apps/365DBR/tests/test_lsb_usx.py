import tempfile
import unittest
from pathlib import Path

from inject_lsb import english_verse_ids, verse_ids_for_pack
from lsb_usx import extract_usx


USX_DIR = Path(__file__).parents[1] / "LSB" / "release" / "USX_1"
JOB_USX = USX_DIR / "JOB.usx"
SNG_USX = USX_DIR / "SNG.usx"

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

    def test_sng_6_13_is_present_in_usx(self):
        verses, _titles = extract_usx(SNG_USX)
        self.assertIn("SNG.6.13", verses)
        self.assertIn("Shulammite", verses["SNG.6.13"])
        self.assertIn("SNG.7.1", verses)
        self.assertIn("sandals", verses["SNG.7.1"])
        self.assertNotIn("Shulammite", verses["SNG.7.1"])

    def test_english_verse_ids_ignore_original_org_numbering(self):
        data = {
            "content": [{"items": [{"attrs": {"verseId": "SNG.7.1"}}]}],
            "parallels": [
                {
                    "bibleId": "de4e12af7f28f599-01",
                    "content": [
                        {"items": [{"attrs": {"verseId": "SNG.6.13"}}]},
                        {"items": [{"attrs": {"verseId": "SNG.7.1"}}]},
                    ],
                }
            ],
        }
        self.assertEqual(english_verse_ids(data), ["SNG.6.13", "SNG.7.1"])

    def test_pack_keeps_lsb_only_verse_in_range(self):
        data = {
            "content": [{"items": [{"attrs": {"verseId": "SNG.7.1"}}]}],
            "parallels": [
                {
                    "bibleId": "de4e12af7f28f599-01",
                    "content": [{"items": [{"attrs": {"verseId": "SNG.6.12"}}]}],
                }
            ],
        }
        usx = {"SNG.6.12": "a", "SNG.6.13": "Come back, O Shulammite", "SNG.7.1": "sandals"}
        path = Path("SNG.6.1-SNG.6.13.json")
        ids = verse_ids_for_pack(path, data, usx)
        self.assertIn("SNG.6.12", ids)
        self.assertIn("SNG.6.13", ids)


if __name__ == "__main__":
    unittest.main()
