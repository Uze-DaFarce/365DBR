"""OSHB WLC 4.20 word list. Direct verse <w> words, and <w> words inside <seg>.

Qere text inside a note is not a word in this list. This module does not
align words, vote, or assign a Strong's number.
"""

import glob
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

OSIS_TO_USFM = {
    "GEN": "GEN", "EXOD": "EXO", "LEV": "LEV", "NUM": "NUM", "DEUT": "DEU",
    "JOSH": "JOS", "JUDG": "JDG", "RUTH": "RUT", "1SAM": "1SA", "2SAM": "2SA",
    "1KGS": "1KI", "2KGS": "2KI", "1CHR": "1CH", "2CHR": "2CH", "EZRA": "EZR",
    "NEH": "NEH", "ESTH": "EST", "JOB": "JOB", "PS": "PSA", "PROV": "PRO",
    "ECCL": "ECC", "SONG": "SNG", "ISA": "ISA", "JER": "JER", "LAM": "LAM",
    "EZEK": "EZK", "DAN": "DAN", "HOS": "HOS", "JOEL": "JOL", "AMOS": "AMO",
    "OBAD": "OBA", "JONAH": "JON", "MIC": "MIC", "NAH": "NAM", "HAB": "HAB",
    "ZEPH": "ZEP", "HAG": "HAG", "ZECH": "ZEC", "MAL": "MAL",
}


def norm_heb_consonants(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    return re.sub(r"[^\u05D0-\u05EA]", "", text)


def map_ref(ref_str: str) -> str:
    parts = ref_str.strip().split(".")
    if len(parts) != 3:
        return ref_str.upper()
    book, chapter, verse = parts[0].upper(), parts[1], parts[2]
    return f"{OSIS_TO_USFM.get(book, book)}.{chapter}.{verse}"


def load_oshb_wlc():
    ns = {"o": "http://www.bibletechnologies.net/2003/OSIS/namespace"}
    by_verse = {}
    for path in sorted(glob.glob(str(ROOT / "apps/365DBR/RAW/OSHB/wlc/*.xml"))):
        if "VerseMap" in path:
            continue
        root = ET.parse(path).getroot()
        for verse in root.findall(".//o:verse", ns):
            raw_id = verse.attrib.get("osisID", "")
            if not raw_id:
                continue
            words = []
            for elem in verse:
                tag = elem.tag.split("}")[-1]
                if tag == "w":
                    surface = "".join(elem.itertext()).strip()
                    lemma = elem.attrib.get("lemma", "").strip()
                    morph = elem.attrib.get("morph", "").strip()
                    words.append((surface, lemma, morph, norm_heb_consonants(surface)))
                elif tag == "seg":
                    for word in elem.findall(".//o:w", ns):
                        surface = "".join(word.itertext()).strip()
                        lemma = word.attrib.get("lemma", "").strip()
                        morph = word.attrib.get("morph", "").strip()
                        words.append((surface, lemma, morph, norm_heb_consonants(surface)))
            by_verse[map_ref(raw_id)] = words
    return by_verse
