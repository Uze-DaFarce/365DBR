import tempfile
import unittest
from pathlib import Path

from bible_common import extract_verse_ids
from inject_lsb import build_lsb_content, english_verse_ids, verse_ids_for_pack
from lsb_usx import extract_usx


def flatten(nodes) -> str:
    parts = []

    def walk(node):
        if isinstance(node, str):
            parts.append(node)
        elif isinstance(node, dict):
            if node.get("type") == "text":
                parts.append(node.get("text") or "")
            for child in node.get("items") or []:
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(nodes)
    return "".join(parts)


USX_DIR = Path(__file__).parents[1] / "LSB" / "release" / "USX_1"
JOB_USX = USX_DIR / "JOB.usx"
SNG_USX = USX_DIR / "SNG.usx"

SPACE_USX = """<?xml version="1.0" encoding="UTF-8"?>
<usx version="3.0">
  <book code="1CO" style="id">1CO</book>
  <chapter number="2" style="c" sid="1CO 2"/>
  <para style="q" vid="1CO 2:9">“T<char style="sc">hings</char> which eye has not seen,</para>
  <para style="q" vid="1CO 2:9">A<char style="sc">nd</char> <char style="it">which</char> <char style="sc">have not entered</char>,</para>
  <para style="p"><verse number="19" style="v" sid="1CO 3:19"/>“<char style="it">He is</char> <char style="sc">the one</char>”<verse eid="1CO 3:19"/></para>
  <para style="p"><verse number="40" style="v" sid="1CH 1:40"/>The sons <char style="it">were</char> <note caller="1" style="f"><char style="ft">Lit sons</char></note>Alian.<verse eid="1CH 1:40"/></para>
  <para style="p"><verse number="24" style="v" sid="1CO 11:24"/>said, <char style="wj">“remember Me.”</char> <verse eid="1CO 11:24"/><verse number="25" style="v" sid="1CO 11:25"/>In the same way<verse eid="1CO 11:25"/></para>
  <para style="p">
    <verse number="16" style="v" sid="JHN 3:16"/>
    <char style="wj">“For God </char>
    <note caller="1" style="f"><char style="ft">Or thus</char></note>
    <char style="wj">so loved</char><verse eid="JHN 3:16"/>
  </para>
</usx>
"""


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
            verse = flatten(verses[f"JOB.41.{number}"])
            self.assertTrue(verse)
            self.assertNotIn("Lit", verse)
            self.assertNotIn("Ch 40:25 in Heb", verse)

        self.assertIn("Can you draw out Leviathan", flatten(verses["JOB.41.1"]))
        self.assertIn("Remember the battle", flatten(verses["JOB.41.8"]))

    def test_same_line_spaces_between_markup_stay_word_breaks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "1CO.usx"
            path.write_text(SPACE_USX, encoding="utf-8")
            verses, _titles = extract_usx(path)

        line = flatten(verses["1CO.2.9"])
        self.assertIn("Things which", line)
        self.assertNotIn("T hings", line)
        self.assertIn("And which have", line)
        self.assertNotIn("Andwhich", line)
        self.assertIn("He is the one", flatten(verses["1CO.3.19"]))
        self.assertNotIn("isthe", flatten(verses["1CO.3.19"]))
        alian = flatten(verses["1CH.1.40"])
        self.assertIn("were Alian", alian)
        self.assertNotIn("wereAlian", alian)
        self.assertNotIn("Lit", alian)
        same = flatten(verses["1CO.11.24"])
        self.assertIn("Me.” In the same way", same)
        self.assertNotIn("Me.”In", same)
        loved = flatten(verses["JHN.3.16"])
        self.assertIn("For God so loved", loved)
        self.assertNotIn("God  so", loved)
        self.assertNotIn("Or thus", loved)

    def test_title_paras_do_not_bleed_into_verse_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "GEN.usx"
            path.write_text(HEADING_USX, encoding="utf-8")
            verses, titles = extract_usx(path)

        self.assertIn("In the beginning God created the heavens and the earth.", flatten(verses["GEN.1.1"]))
        self.assertNotIn("Creation", flatten(verses["GEN.1.1"]))
        self.assertNotIn("Creation", flatten(titles.get("GEN.1.1", [])))
        self.assertIn("formless and void", flatten(verses["GEN.1.2"]))
        self.assertIn("Let there be light", flatten(verses["GEN.1.2"]))
        self.assertNotIn("God", flatten(verses["GEN.1.2"]))
        self.assertIn("God", flatten(titles["GEN.1.2"]))

    def test_chapter_heading_attaches_to_next_verse_not_previous(self):
        verses, titles = extract_usx(SNG_USX)
        self.assertNotIn("Troubled Dream", flatten(verses["SNG.2.17"]))
        self.assertNotIn("Troubled Dream", flatten(titles.get("SNG.2.17", [])))
        self.assertNotIn("Troubled Dream", flatten(titles.get("SNG.3.1", [])))
        self.assertNotIn("Troubled Dream", flatten(verses["SNG.3.1"]))
        self.assertIn("On my bed", flatten(verses["SNG.3.1"]))

    def test_sng_6_13_is_present_in_usx(self):
        verses, _titles = extract_usx(SNG_USX)
        self.assertIn("SNG.6.13", verses)
        self.assertIn("Shulammite", flatten(verses["SNG.6.13"]))
        self.assertIn("SNG.7.1", verses)
        self.assertIn("sandals", flatten(verses["SNG.7.1"]))
        self.assertNotIn("Shulammite", flatten(verses["SNG.7.1"]))

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


class TestBuildLsbContent(unittest.TestCase):
    def test_shared_paragraph_once_and_inside_the_reading(self):
        para = {
            "name": "para",
            "type": "tag",
            "attrs": {"style": "p"},
            "items": [
                {"type": "text", "text": "yesterday ", "attrs": {"verseId": "MAT.7.21"}},
                {"type": "text", "text": "today ", "attrs": {"verseId": "MAT.7.22"}},
                {"type": "text", "text": "still today", "attrs": {"verseId": "MAT.7.23"}},
                {"type": "text", "text": " tomorrow", "attrs": {"verseId": "MAT.8.16"}},
            ],
        }
        verses = {
            "MAT.7.21": [para],
            "MAT.7.22": [para],
            "MAT.7.23": [para],
            "MAT.8.16": [para],
        }
        title = {
            "name": "para",
            "type": "tag",
            "attrs": {"style": "d"},
            "items": [{"type": "text", "text": "A heading"}],
        }
        content = build_lsb_content(
            ["MAT.7.22", "MAT.7.23"],
            verses,
            {"MAT.7.22": [title]},
        )
        self.assertEqual(flatten(content), "A headingtoday still today")
        self.assertEqual(extract_verse_ids(content), {"MAT.7.22", "MAT.7.23"})
        self.assertIn("yesterday", flatten([para]))


if __name__ == "__main__":
    unittest.main()
