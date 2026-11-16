import sys
sys.stdout.reconfigure(encoding="utf-8")
#!/usr/bin/env python3
"""
Foundations Library (FL) Compiler — build_fl.py
Mt. Sinai LLC Monorepo (D:\\Users\\uzeda\\Mt. Sinai LLC\\monorepo\\apps\\foundations\\)

Outputs & Maintains:
1. apps/foundations/data/education.json (Canonical Structured Data Layer - 2 Parts, 8 Chapters, 8 Labs)
2. apps/foundations/what-does-the-bible-say-about-education.html (Canonical Book 2 Web/Print Guide)
3. apps/foundations/what-does-the-bible-say-about-god.html (Canonical Book 1 Metadata/Header Sync)
4. 1-Hop Redirect Stubs:
   - apps/foundations/education.html -> /foundations/what-does-the-bible-say-about-education.html
   - apps/foundations/god.html -> /foundations/what-does-the-bible-say-about-god.html
   - apps/foundations/what-we-know.html -> /foundations/what-does-the-bible-say-about-god.html
   - apps/foundations/what-we-know-about-god.html -> /foundations/what-does-the-bible-say-about-god.html
   - apps/365DBR/What_We_Know.html -> /foundations/what-does-the-bible-say-about-god.html
5. apps/foundations/.htaccess & apps/foundations/404-case-router.html (GoDaddy Case-Insensitive Routing)
"""

import argparse
import json
import re
import html
from pathlib import Path
from datetime import datetime, timezone

# ==============================================================================
# 1. PATH & URL CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent
MONOREPO_APPS_DIR = BASE_DIR.parent
RAW_MD_PATH = BASE_DIR / "raw" / "education_manuscript.md"
JSON_OUT_PATH = BASE_DIR / "data" / "education.json"

# Book 1: What Does the Bible Say About God? (What We Know About God)
GOD_CANONICAL_SLUG = "what-does-the-bible-say-about-god.html"
GOD_CANONICAL_URL = f"https://mt-sin.ai/foundations/{GOD_CANONICAL_SLUG}"
GOD_CANONICAL_PATH = BASE_DIR / GOD_CANONICAL_SLUG
GOD_RAW_MD_PATH = BASE_DIR / "raw" / "god_manuscript.md"
GOD_JSON_OUT_PATH = BASE_DIR / "data" / "god.json"

# Book 2: What Does the Bible Say About Education?
EDU_CANONICAL_SLUG = "what-does-the-bible-say-about-education.html"
EDU_CANONICAL_URL = f"https://mt-sin.ai/foundations/{EDU_CANONICAL_SLUG}"
EDU_CANONICAL_PATH = BASE_DIR / EDU_CANONICAL_SLUG

# Redirect & Server Config Paths
REDIRECT_365DBR_PATH = MONOREPO_APPS_DIR / "365DBR" / "What_We_Know.html"
HTACCESS_PATH = BASE_DIR / ".htaccess"
CASE_ROUTER_PATH = BASE_DIR / "404-case-router.html"

# ==============================================================================
# 2. BIBLE BOOK REGISTRY & DETERMINISTIC 365DBR DEEP-LINKER (&fullverse=1)
# ==============================================================================
BIBLE_BOOKS = {
    "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV", "Numbers": "NUM", "Deuteronomy": "DEU",
    "Joshua": "JOS", "Judges": "JDG", "Ruth": "RUT", "1 Samuel": "1SA", "2 Samuel": "2SA",
    "1 Kings": "1KI", "2 Kings": "2KI", "1 Chronicles": "1CH", "2 Chronicles": "2CH",
    "Ezra": "EZR", "Nehemiah": "NEH", "Esther": "EST", "Job": "JOB", "Psalms": "PSA", "Psalm": "PSA",
    "Proverbs": "PRO", "Ecclesiastes": "ECC", "Song of Solomon": "SNG", "Isaiah": "ISA",
    "Jeremiah": "JER", "Lamentations": "LAM", "Ezekiel": "EZK", "Daniel": "DAN",
    "Hosea": "HOS", "Joel": "JOL", "Amos": "AMO", "Obadiah": "OBA", "Jonah": "JON",
    "Micah": "MIC", "Nahum": "NAM", "Habakkuk": "HAB", "Zephaniah": "ZEP", "Haggai": "HAG",
    "Zechariah": "ZEC", "Malachi": "MAL",
    "Matthew": "MAT", "Mark": "MRK", "Luke": "LUK", "John": "JHN", "Acts": "ACT",
    "Romans": "ROM", "1 Corinthians": "1CO", "2 Corinthians": "2CO", "Galatians": "GAL",
    "Ephesians": "EPH", "Philippians": "PHP", "Colossians": "COL",
    "1 Thessalonians": "1TH", "2 Thessalonians": "2TH", "1 Timothy": "1TI", "2 Timothy": "2TI",
    "Titus": "TIT", "Philemon": "PHM", "Hebrews": "HEB", "James": "JAS",
    "1 Peter": "1PE", "2 Peter": "2PE", "1 John": "1JN", "2 John": "2JN", "3 John": "3JN",
    "Jude": "JUD", "Revelation": "REV"
}

BOOK_NAMES_SORTED = sorted(BIBLE_BOOKS.keys(), key=len, reverse=True)
BOOK_PATTERN = "|".join(re.escape(b) for b in BOOK_NAMES_SORTED)

CITATION_REGEX = re.compile(
    rf"\b(?P<book>{BOOK_PATTERN})\s+(?P<ref>\d+(?:[:\d,\s\-\–—]*\d+)?)(?P<tail>(?:\s*;\s*\d+[:\d,\s\-\–—]*\d+)*)"
)

def build_365dbr_url(book_code: str, ch_verse_str: str) -> str:
  clean = ch_verse_str.strip().replace("—", "-").replace("–", "-")
  if book_code == "JUD" and ":" not in clean:
    first_v = re.split(r"[-\s,]", clean)[0]
    return f"/365DBR/bible.html?book=JUD&chapter=1&verse={first_v}&fullverse=1"
  if ":" in clean:
    ch_part, v_part = clean.split(":", 1)
    ch = re.sub(r"\D", "", ch_part) or "1"
    first_v = re.split(r"[-\s,]", v_part.strip())[0]
    first_v = re.sub(r"\D", "", first_v) or "1"
    return (
        f"/365DBR/bible.html?book={book_code}&chapter={ch}&verse={first_v}&fullverse=1"
    )
  else:
    ch = re.split(r"[-\s,]", clean)[0]
    ch = re.sub(r"\D", "", ch) or "1"
    return f"/365DBR/bible.html?book={book_code}&chapter={ch}&verse=1&fullverse=1"


def _format_ref_group(book_name: str, book_code: str, ref_group: str, include_book: bool) -> str:
    s = ref_group.strip()
    if ":" not in s:
        url = build_365dbr_url(book_code, s)
        label = f"{book_name} {s}" if include_book else s
        return (
            f'<a href="{url}" class="fl-scripture-link" '
            f'title="Open {book_name} {s} in 365DBR Scripture Reader">{label}</a>'
        )

    ch_part, v_part = s.split(":", 1)
    ch = re.sub(r"\D", "", ch_part) or "1"
    v_tokens = re.split(r"(\s*,\s*)", v_part)
    out_parts = []
    first_seg = True
    for tok in v_tokens:
        if re.match(r"^\s*,\s*$", tok):
            out_parts.append(tok)
        elif tok.strip():
            seg = tok.strip()
            url = build_365dbr_url(book_code, f"{ch}:{seg}")
            if first_seg:
                label = f"{book_name} {ch_part.strip()}:{seg}" if include_book else f"{ch_part.strip()}:{seg}"
                title_ref = f"{book_name} {ch_part.strip()}:{seg}"
                first_seg = False
            else:
                label = seg
                title_ref = f"{book_name} {ch_part.strip()}:{seg}"
            out_parts.append(
                f'<a href="{url}" class="fl-scripture-link" '
                f'title="Open {title_ref} in 365DBR Scripture Reader">{label}</a>'
            )
    return "".join(out_parts)


def linkify_scripture_references(html_text: str) -> str:
    tokens = re.split(
        r"(<a\b[^>]*>.*?</a>)", html_text, flags=re.IGNORECASE | re.DOTALL
    )
    out = []
    for tok in tokens:
        if tok.lower().startswith("<a "):
            out.append(tok)
            continue

        def _replace_match(m: re.Match) -> str:
            book_name = m.group("book")
            ref = m.group("ref")
            tail = m.group("tail") or ""
            book_code = BIBLE_BOOKS[book_name]
            linked = _format_ref_group(book_name, book_code, ref, include_book=True)

            if tail:
                parts = re.split(r"(\s*;\s*)", tail)
                for p in parts:
                    if re.match(r"^\s*;\s*$", p):
                        linked += p
                    elif p.strip():
                        linked += _format_ref_group(book_name, book_code, p.strip(), include_book=False)
            return linked

        out.append(CITATION_REGEX.sub(_replace_match, tok))
    return "".join(out)


def write_if_changed(path: Path, new_content: str, dry_run: bool = False) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            old_content = path.read_text(encoding="utf-8")
            if old_content == new_content:
                print(f" [UNCHANGED] {path}")
                return False
        except Exception:
            pass
    if dry_run:
        print(f" [DRY-RUN: WOULD UPDATE] {path}")
        return True
    path.write_text(new_content, encoding="utf-8")
    print(f" [UPDATED]   {path}")
    return True


def write_json_if_changed(path: Path, doc_data: dict, dry_run: bool = False) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    new_ts = doc_data.get("generated_at", "")
    ordered = {k: v for k, v in doc_data.items() if k != "generated_at"}
    if path.exists():
        try:
            existing_raw = path.read_text(encoding="utf-8")
            existing_json = json.loads(existing_raw)
            existing_cmp = {k: v for k, v in existing_json.items() if k != "generated_at"}
            if existing_cmp == ordered and "generated_at" in existing_json:
                ordered["generated_at"] = existing_json["generated_at"]
                candidate_str = json.dumps(ordered, indent=2, ensure_ascii=False)
                if existing_raw == candidate_str:
                    print(f" [UNCHANGED] {path}")
                    return False
                if not dry_run:
                    path.write_text(candidate_str, encoding="utf-8")
                    print(f" [UPDATED KEY ORDER] {path}")
                else:
                    print(f" [DRY-RUN: WOULD REORDER KEYS] {path}")
                return True
        except Exception:
            pass
    ordered["generated_at"] = new_ts
    new_str = json.dumps(ordered, indent=2, ensure_ascii=False)
    return write_if_changed(path, new_str, dry_run=dry_run)

# ==============================================================================
# 3. SURGICAL MANUSCRIPT CLEANUP RULES
# ==============================================================================
def clean_manuscript_text(raw_text: str) -> str:
  text = raw_text.replace("\r\n", "\n").replace("\u00a0", " ")
  for esc, char in [
      (r"\#", "#"),
      (r"\!", "!"),
      (r"\~", "~"),
      (r"\_", "_"),
      (r"\[", "["),
      (r"\]", "]"),
      (r"\&", "&"),
      (r"\.", "."),
      (r"\)", ")"),
      (r"\(", "("),
  ]:
    text = text.replace(esc, char)
  text = text.replace(
      "directed primary from Parent to Child",
      "directed primarily from Parent to Child",
  )
  text = re.sub(r"\(Genesis 39:9\)\.Notice", "(Genesis 39:9). Notice", text)
  text = re.sub(r"^(\s*\d+\.\s+)\*\*\d+\.\s+", r"\1**", text, flags=re.MULTILINE)
  text = re.sub(
      r"^(\s*[\-\*]\s+)\*\*(\d+\.)\s+", r"\1**", text, flags=re.MULTILINE
  )
  text = re.sub(
      r"^\s*1\.\s+\*\*Step 4:\s*Family Prayer\*\*",
      "**Step 4: Family Prayer**",
      text,
      flags=re.MULTILINE,
  )
  text = re.sub(r"^\s*<!--\s*end list\s*-->\s*$", "", text, flags=re.MULTILINE)
  return text

def strip_md_wrappers(line: str) -> str:
    s = re.sub(r"^#+\s*", "", line.strip())
    s = s.replace("**", "").strip()
    return s

# ==============================================================================
# 4. MARKDOWN TO STRUCTURED JSON AST PARSER
# ==============================================================================
def parse_manuscript_to_json(cleaned_md: str) -> dict:
    lines = cleaned_md.split("\n")

    doc_data = {
        "schema_version": "1.2.0",
        "app": {
            "name": "Foundations Library",
            "abbr": "FL",
            "slug": "foundations",
            "storage_prefix": "fl_edu_",
            "base_url": "https://mt-sin.ai/foundations/",
            "canonical_url": EDU_CANONICAL_URL,
            "short_url": "https://mt-sin.ai/foundations/education.html",
            "sibling_god_url": GOD_CANONICAL_URL,
            "scripture_engine_url": "https://mt-sin.ai/365DBR/"
        },
        "metadata": {
            "id": "fl-book-education",
            "slug": "what-does-the-bible-say-about-education",
            "short_slug": "education",
            "title": "What Does the Bible Say About Education?",
            "subtitle": "Foundational Truths for Parents and Students Survival Guide",
            "authors": ["Rowley Shaw", "Patty Shaw"],
            "publisher": "Mt. Sinai LLC",
            "attributions": [
                "Ken Ham",
                "Patricia Engler",
                "Britt Beemer",
                "Answers in Genesis (AiG)",
                "Gemini"
            ],
            "anchor_scriptures": [
                "Psalm 11:3",
                "Proverbs 1:7",
                "1 Corinthians 3:11",
                "Genesis 1–11"
            ]
        },
        "intro": {
            "title": "About This Resource & Attribution",
            "blocks": []
        },
        "parts": [],
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

    current_part = None
    current_chapter = None
    current_section = None
    current_lab = None
    input_counter = 0

    def add_block(target_list: list, text_line: str):
        nonlocal input_counter
        stripped = text_line.strip()
        if not stripped:
            return

        if "HTML BUILD NOTE:" in stripped:
            if "static visual comparison chart" in stripped:
                target_list.append({"type": "widget", "widget_id": "k12_hours_svg_chart"})
                return
            elif "interactive Lab #2 calculator" in stripped:
                target_list.append({"type": "widget", "widget_id": "lab2_hour_audit_calculator"})
                return

        if "_____" in stripped:
            input_counter += 1
            lab_num = current_lab["lab_number"] if current_lab else 0
            field_id = f"fl_edu_lab{lab_num}_input_{input_counter}"
            label_part = re.sub(r"_+", "", stripped).strip()
            label_clean = re.sub(r"^[\-\*\s]+", "", label_part).replace("*", "").strip()
            is_numeric_audit = "Weekly " in label_clean and "hours:" in label_clean
            is_signature = any(k in label_clean for k in ["Signatures:", "Date Signed:"])
            target_list.append({
                "type": "lab_input",
                "input_id": field_id,
                "label": label_clean or "Our Family's Answer:",
                "input_kind": "number" if is_numeric_audit else ("signature" if is_signature else "textarea")
            })
            return

        if re.match(r"^(\-|\*)\s+", stripped):
            content = re.sub(r"^(\-|\*)\s+", "", stripped)
            target_list.append({"type": "ul_item", "text": content})
            return
        if re.match(r"^\d+\.\s+", stripped):
            content = re.sub(r"^\d+\.\s+", "", stripped)
            target_list.append({"type": "ol_item", "text": content})
            return

        target_list.append({"type": "paragraph", "text": stripped})

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        bare = strip_md_wrappers(line)
        is_heading_line = line.startswith("#") or (line.startswith("**") and line.endswith("**"))

        if bare.startswith("What Does the Bible Say About Education?") or bare.startswith("Foundational Truths for Parents and Students"):
            continue
        if bare.startswith("About This Resource & Attribution"):
            continue

        if re.match(r"^PART\s+(I|II|1|2)\b", bare, re.IGNORECASE):
            part_num = 1 if re.match(r"^PART\s+(I|1)\b", bare, re.IGNORECASE) and not bare.upper().startswith("PART II") else 2
            current_part = {
                "part_number": part_num,
                "id": f"part-{part_num}",
                "title": bare,
                "subtitle": "",
                "tagline": "",
                "direction": "Parent-to-Child" if part_num == 1 else "Student-to-Parent",
                "baton_callout": None,
                "chapters": []
            }
            doc_data["parts"].append(current_part)
            current_chapter = None
            current_section = None
            current_lab = None
            continue

        m_ch = re.match(r"^Chapter\s+(\d+)\s*:\s*(.+)$", bare, re.IGNORECASE)
        if m_ch and is_heading_line:
            ch_num = int(m_ch.group(1))
            if current_part is None:
                current_part = {
                    "part_number": 1 if ch_num <= 4 else 2,
                    "id": f"part-{1 if ch_num <= 4 else 2}",
                    "title": "PART I: THE BIBLICAL MANDATE" if ch_num <= 4 else "PART II: THE BABYLON SURVIVAL GUIDE",
                    "subtitle": "",
                    "tagline": "",
                    "direction": "Parent-to-Child" if ch_num <= 4 else "Student-to-Parent",
                    "baton_callout": None,
                    "chapters": []
                }
                doc_data["parts"].append(current_part)

            current_chapter = {
                "chapter_number": ch_num,
                "id": f"ch-{ch_num}",
                "title": bare,
                "subtitle": "",
                "blocks": [],
                "sections": [],
                "lab": None
            }
            current_part["chapters"].append(current_chapter)
            current_section = None
            current_lab = None
            continue

        if current_part is not None and current_chapter is None:
            if "Why the Baton Passes Here" in bare:
                current_part["baton_callout"] = {"title": bare, "blocks": []}
            elif current_part["baton_callout"] is not None:
                add_block(current_part["baton_callout"]["blocks"], line)
            elif is_heading_line:
                if not current_part["subtitle"]:
                    current_part["subtitle"] = bare
                else:
                    current_part["tagline"] = bare
            else:
                if not current_part["subtitle"]:
                    current_part["subtitle"] = bare
            continue

        m_lab = re.search(r"(?:Family Table|Student-to-Parent|Family\s*&\s*Student Commissioning)\s+Lab\s*#(\d+)", bare, re.IGNORECASE)
        if m_lab and current_chapter is not None and (is_heading_line or bare.startswith("6. Family")):
            lab_num = int(m_lab.group(1))
            lab_title_clean = re.sub(r"^6\.\s*", "", bare)
            lab_dir = (
                "Parent-to-Child" if lab_num <= 4
                else ("Student-to-Parent" if lab_num <= 7 else "Joint Family & Student Commissioning")
            )
            current_lab = {
                "lab_number": lab_num,
                "id": f"lab-{lab_num}",
                "direction": lab_dir,
                "title": lab_title_clean,
                "blocks": []
            }
            current_chapter["lab"] = current_lab
            current_section = None
            continue

        if current_chapter is not None and current_lab is None and line.startswith("#"):
            if not current_chapter["subtitle"] and not current_chapter["blocks"] and not current_chapter["sections"]:
                current_chapter["subtitle"] = bare
                continue
            sec_idx = len(current_chapter["sections"]) + 1
            current_section = {
                "id": f"ch-{current_chapter['chapter_number']}-sec-{sec_idx}",
                "heading": bare,
                "blocks": []
            }
            current_chapter["sections"].append(current_section)
            continue

        if current_lab is not None:
            add_block(current_lab["blocks"], line)
        elif current_section is not None:
            add_block(current_section["blocks"], line)
        elif current_chapter is not None:
            add_block(current_chapter["blocks"], line)
        elif current_part is None:
            add_block(doc_data["intro"]["blocks"], line)

    return doc_data

# ==============================================================================
# 5. INLINE MARKDOWN FORMATTER & WIDGET RENDERERS
# ==============================================================================
SOCIAL_SVG_PATHS = {
    "x": (
        "X (Twitter)",
        '<svg class="fl-social-icon" viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true" focusable="false"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
    ),
    "youtube": (
        "YouTube",
        '<svg class="fl-social-icon" viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true" focusable="false"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>',
    ),
    "facebook": (
        "Facebook",
        '<svg class="fl-social-icon" viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true" focusable="false"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
    ),
    "instagram": (
        "Instagram",
        '<svg class="fl-social-icon" viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true" focusable="false"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>',
    ),
    "rumble": (
        "Rumble",
        '<svg class="fl-social-icon" viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true" focusable="false"><path d="M13.39 2.22c-3.15-.63-6.52.27-8.79 2.37-2.31 2.13-3.23 5.48-2.42 8.53.79 2.98 3.19 5.48 6.13 6.42 3.12 1 6.69.34 9.21-1.72 2.47-2.02 3.69-5.32 3.14-8.47-.55-3.19-3.03-5.94-6.17-6.88-.36-.11-.73-.18-1.1-.25zM9.5 8.25c.28-.16.63-.15.91.02l5.25 3.25c.46.28.46.96 0 1.24l-5.25 3.25c-.28.17-.63.18-.91.02-.28-.16-.45-.46-.45-.79v-6.2c0-.33.17-.63.45-.79z"/></svg>',
    ),
}

def render_ext_or_social_link(label: str, url: str) -> str:
    u_low = url.lower()
    platform_key = None
    if "x.com/" in u_low or "twitter.com/" in u_low:
        platform_key = "x"
    elif "youtube.com/" in u_low or "youtu.be/" in u_low:
        platform_key = "youtube"
    elif "facebook.com/" in u_low:
        platform_key = "facebook"
    elif "instagram.com/" in u_low:
        platform_key = "instagram"
    elif "rumble.com/" in u_low:
        platform_key = "rumble"

    if not platform_key:
        return f'<a href="{url}" target="_blank" rel="noopener" class="fl-ext-link">{label}</a>'

    plat_name, svg_icon = SOCIAL_SVG_PATHS[platform_key]
    clean_label = label.strip()
    if clean_label.startswith("http://") or clean_label.startswith("https://"):
        m_handle = re.search(r"/(@[A-Za-z0-9_.-]+)", url)
        if m_handle:
            clean_label = m_handle.group(1)
        else:
            m_slug = re.search(r"/(?:c|user|channel)/([^/?#]+)", url)
            if m_slug:
                clean_label = m_slug.group(1)
            else:
                m_tail = re.search(r"https?://[^/]+/([^/?#]+)", url)
                if m_tail:
                    clean_label = "@" + m_tail.group(1).lstrip("@")

    title_attr = html.escape(f"{clean_label} on {plat_name}", quote=True)
    return (
        f'<a href="{url}" target="_blank" rel="noopener" '
        f'class="fl-ext-link fl-social-link fl-social-{platform_key}" '
        f'title="{title_attr}" aria-label="{title_attr}">'
        f'{svg_icon}<span>{clean_label}</span></a>'
    )

def format_inline_md(text: str) -> str:
  s = html.escape(text, quote=False)
  # Strip markdown backticks around URLs, bare domains (e.g. `x.com`), or @handles (including dots/hyphens)
  s = re.sub(r"`((?:https?://)?[A-Za-z0-9.-]+\.[a-z]{2,}[^`\s]*)`", r"\1", s)
  s = re.sub(r"`(@[A-Za-z0-9_.-]+)`", r"\1", s)
  s = re.sub(
      r"&lt;(https?://[^&>\s]+)&gt;",
      lambda m: render_ext_or_social_link(m.group(1), m.group(1)),
      s,
  )
  s = re.sub(
      r"\[([^\]]+)\]\((https?://[^\)]+)\)",
      lambda m: render_ext_or_social_link(m.group(1), m.group(2)),
      s,
  )
  s = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", s)
  s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
  s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)

  # Swap web-only phrasing for natural print-table phrasing when printed
  web_to_print_swaps = [
      (
          "in your print Bible or by using the interactive verse links",
          (
              'in your Bible<span class="web-only"> (or click the interactive'
              " verse links)</span>"
          ),
      ),
      (
          "in your print Bible or the online text",
          'in your Bible<span class="web-only"> or the online text</span>',
      ),
      (
          "in your print Bible or the integrated 365DBR Scripture reader",
          (
              'in your Bible<span class="web-only"> or the integrated 365DBR'
              " Scripture reader</span>"
          ),
      ),
      (
          (
              "in your printed Bibles or by using <strong>the integrated 365DBR"
              " Scripture reader</strong>"
          ),
          (
              'in your Bible<span class="web-only"> or by using <strong>the'
              " integrated 365DBR Scripture reader</strong></span>"
          ),
      ),
      (
          "Open your Bibles using the interactive verse links and read",
          (
              'Open your Bible<span class="web-only"> (or use the interactive'
              " verse links)</span> and read"
          ),
      ),
      (
          "Gather around the table with a notebook, pen, and the integrated"
          " 365DBR Scripture reader.",
          (
              "Gather around the table with your Bible, a notebook, and a"
              ' pen<span class="web-only"> (or use the integrated 365DBR'
              " Scripture reader)</span>."
          ),
      ),
      (
          " — Print or Discuss at the Table",
          '<span class="web-only"> — Print or Discuss at the Table</span>',
      ),
  ]
  for old_str, new_str in web_to_print_swaps:
    s = s.replace(old_str, new_str)

  return linkify_scripture_references(s)

def render_k12_static_svg_chart() -> str:
    return """
    <figure class="fl-chart-card" id="k12-hours-comparison-chart" aria-label="K through 12 Hours Comparison Chart">
      <div class="fl-chart-header">
        <h4>K–12 Cumulative Worldview Shaping: 13-Year Hour Comparison</h4>
        <p class="fl-chart-sub">Comparing 13 years (Kindergarten through 12th Grade) of secular classroom immersion vs. Sunday-only attendance vs. the Biblical Partnership of Daily Personal Study (Psalm 1:2; Joshua 1:8; Acts 17:11) &amp; Family Table Discipleship (Deuteronomy 6:6–9).</p>
      </div>
      <svg viewBox="0 0 820 310" class="fl-svg-chart" role="img" aria-labelledby="svg-k12-title">
        <title id="svg-k12-title">K-12 Secular Classroom Hours vs Time in God's Word</title>
        <rect x="0" y="0" width="820" height="310" rx="8" fill="#faf8f5" stroke="#d6cfc2" stroke-width="1.5"/>
        <line x1="230" y1="35" x2="230" y2="255" stroke="#bfb6a5" stroke-width="1.5"/>
        <line x1="410" y1="35" x2="410" y2="255" stroke="#e5dec9" stroke-dasharray="4,4"/>
        <line x1="590" y1="35" x2="590" y2="255" stroke="#e5dec9" stroke-dasharray="4,4"/>
        <line x1="770" y1="35" x2="770" y2="255" stroke="#e5dec9" stroke-dasharray="4,4"/>

        <text x="218" y="72" text-anchor="end" font-family="Merriweather, serif" font-size="13" font-weight="bold" fill="#2c2520">Secular K–12 Classroom</text>
        <text x="218" y="90" text-anchor="end" font-family="Merriweather, serif" font-size="11" fill="#6b5e53">(35 hrs/wk × 36 wks × 13 yrs)</text>
        <rect x="230" y="52" width="520" height="44" rx="4" fill="#9e2a2b"/>
        <text x="758" y="79" font-family="Merriweather, serif" font-size="13" font-weight="bold" fill="#9e2a2b">16,380 hrs (12,000–14,000+ core)</text>

        <text x="218" y="147" text-anchor="end" font-family="Merriweather, serif" font-size="13" font-weight="bold" fill="#2c2520">Sunday School / Youth Only</text>
        <text x="218" y="165" text-anchor="end" font-family="Merriweather, serif" font-size="11" fill="#6b5e53">(~40 min/wk × 52 wks × 13 yrs)</text>
        <rect x="230" y="127" width="18" height="44" rx="3" fill="#d97706"/>
        <text x="256" y="154" font-family="Merriweather, serif" font-size="13" font-weight="bold" fill="#b45309">~450 hrs (30:1 Ratio Deficit)</text>

        <text x="218" y="222" text-anchor="end" font-family="Merriweather, serif" font-size="13" font-weight="bold" fill="#1e3a5f">Daily Personal + Family + Church</text>
        <text x="218" y="240" text-anchor="end" font-family="Merriweather, serif" font-size="11" fill="#6b5e53">(Ps 1:2; Josh 1:8; Deut 6:6–9)</text>
        <rect x="230" y="202" width="185" height="44" rx="4" fill="#1e3a5f"/>
        <text x="425" y="229" font-family="Merriweather, serif" font-size="13" font-weight="bold" fill="#1e3a5f">3,500–5,000+ hrs (+ Christ-Centered Ed)</text>

        <text x="410" y="288" text-anchor="middle" font-family="Merriweather, serif" font-size="11.5" font-style="italic" fill="#4a4036">
          "Everyone, after he has been fully trained (katērtismenos — κατηρτισμένος), will be like his teacher." — Luke 6:40
        </text>
      </svg>
    </figure>
    """

def render_lab2_interactive_calculator() -> str:
    return """
    <div class="fl-calculator-card" id="fl-lab2-calculator">
      <h4>Interactive Lab #2: 12-Year (K–12) Worldview Hour Audit Calculator</h4>
      <p class="fl-calc-desc">Enter your household's estimated <strong>weekly hours</strong> below. Your values save automatically to your browser (<code>fl_edu_calc_...</code>) and render your personalized 12-year cumulative worldview trajectory.</p>
      <div class="fl-calc-grid">
        <div class="fl-calc-field">
          <label for="fl_edu_calc_school">1. Weekly Secular School &amp; Homework Hours:</label>
          <input type="number" id="fl_edu_calc_school" class="fl-persist-input fl-calc-input" data-storage-key="fl_edu_calc_school" min="0" max="100" step="0.5" value="35" />
          <span class="fl-calc-print-line">_______ hrs/wk</span>
        </div>
        <div class="fl-calc-field">
          <label for="fl_edu_calc_media">2. Weekly Secular Media, Gaming &amp; Screen Hours:</label>
          <input type="number" id="fl_edu_calc_media" class="fl-persist-input fl-calc-input" data-storage-key="fl_edu_calc_media" min="0" max="100" step="0.5" value="20" />
          <span class="fl-calc-print-line">_______ hrs/wk</span>
        </div>
        <div class="fl-calc-field">
          <label for="fl_edu_calc_personal">3. Weekly Personal / Private Bible Study Hours (Psalm 1:2; Joshua 1:8; Acts 17:11):</label>
          <input type="number" id="fl_edu_calc_personal" class="fl-persist-input fl-calc-input" data-storage-key="fl_edu_calc_personal" min="0" max="100" step="0.25" value="1.75" />
          <span class="fl-calc-print-line">_______ hrs/wk</span>
        </div>
        <div class="fl-calc-field">
          <label for="fl_edu_calc_family">4. Weekly Family Table Study &amp; Church Hours (Deuteronomy 6:6–9):</label>
          <input type="number" id="fl_edu_calc_family" class="fl-persist-input fl-calc-input" data-storage-key="fl_edu_calc_family" min="0" max="100" step="0.25" value="3.5" />
          <span class="fl-calc-print-line">_______ hrs/wk</span>
        </div>
      </div>
      <div class="fl-calc-results" id="fl-calc-results-box">
        <div class="fl-calc-bars">
          <div class="fl-bar-row">
            <div class="fl-bar-label">
              <strong>12-Year Secular Stream (School + Media):</strong>
              <span id="fl-12yr-secular-val">0 hrs</span>
            </div>
            <div class="fl-bar-track"><div id="fl-12yr-secular-bar" class="fl-bar-fill fl-bar-secular" style="width: 85%;"></div></div>
          </div>
          <div class="fl-bar-row">
            <div class="fl-bar-label">
              <strong>12-Year Word of God Stream (Personal + Family/Church):</strong>
              <span id="fl-12yr-biblical-val">0 hrs</span>
            </div>
            <div class="fl-bar-track"><div id="fl-12yr-biblical-bar" class="fl-bar-fill fl-bar-biblical" style="width: 15%;"></div></div>
          </div>
        </div>
        <p id="fl-calc-summary-verdict" class="fl-calc-verdict"></p>
      </div>
      <div class="fl-calc-print-worksheet print-only">
        <strong>Paper Worksheet 12-Year (K–12) Worldview Audit Formula:</strong><br/>
        &bull; <strong>12-Yr Secular Stream:</strong> (Line 1 School Hrs × 432 wks) + (Line 2 Media Hrs × 624 wks) = <strong>_____________ Secular Hours</strong><br/>
        &bull; <strong>12-Yr Word of God Stream:</strong> (Line 3 Personal Hrs + Line 4 Family/Church Hrs) × 624 wks = <strong>_____________ Biblical Hours</strong><br/>
        &bull; <strong>Our Household Ratio:</strong> Secular Hours &divide; Biblical Hours = <strong>________ to 1</strong>
      </div>
    </div>
    """

def render_blocks_html(blocks: list) -> str:
    html_out = []
    in_ul = False
    in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            html_out.append("</ul>")
            in_ul = False
        if in_ol:
            html_out.append("</ol>")
            in_ol = False

    for b in blocks:
        btype = b["type"]
        if btype == "ul_item":
          if in_ol:
            html_out.append("</ol>")
            in_ol = False
          if not in_ul:
            html_out.append('<ul class="fl-list">')
            in_ul = True
          rendered_item = format_inline_md(b["text"]).strip()
          if re.match(r"^<strong>.+?:</strong>$", rendered_item):
            html_out.append(f'<li class="fl-list-lead">{rendered_item}</li>')
          else:
            html_out.append(f"<li>{rendered_item}</li>")
        elif btype == "ol_item":
            if in_ul:
                html_out.append("</ul>")
                in_ul = False
            if not in_ol:
                html_out.append('<ol class="fl-list">')
                in_ol = True
            html_out.append(f"<li>{format_inline_md(b['text'])}</li>")
        else:
            close_lists()
            if btype == "paragraph":
                html_out.append(f"<p>{format_inline_md(b['text'])}</p>")
            elif btype == "widget":
                if b["widget_id"] == "k12_hours_svg_chart":
                    html_out.append(render_k12_static_svg_chart())
                elif b["widget_id"] == "lab2_hour_audit_calculator":
                    html_out.append(render_lab2_interactive_calculator())
            elif btype == "lab_input":
                if b["input_kind"] == "number":
                    continue
                fid = b["input_id"]
                lbl = format_inline_md(b["label"])
                if b["input_kind"] == "signature":
                    html_out.append(f"""
                    <div class="fl-lab-response-block fl-signature-field">
                      <label for="{fid}" class="fl-response-label">{lbl}</label>
                      <input type="text" id="{fid}" class="fl-persist-input fl-sig-input" data-storage-key="{fid}" placeholder="Type full name(s) or print to sign by hand..." />
                      <div class="fl-print-blank-line fl-print-sig-line" data-print-for="{fid}">________________________________________________________</div>
                    </div>
                    """)
                else:
                    html_out.append(f"""
                    <div class="fl-lab-response-block">
                      <label for="{fid}" class="fl-response-label">{lbl}</label>
                      <textarea id="{fid}" class="fl-persist-input fl-textarea" data-storage-key="{fid}" rows="3" placeholder="Type your household's biblical response here (saved automatically in this browser)..."></textarea>
                      <div class="fl-print-blank-line" data-print-for="{fid}">
                        <div>__________________________________________________________________________________________</div>
                        <div>__________________________________________________________________________________________</div>
                        <div>__________________________________________________________________________________________</div>
                      </div>
                    </div>
                    """)
    close_lists()
    return "\n".join(html_out)

# ==============================================================================
# 6. HTML COMPILER (BOOK 2: WHAT DOES THE BIBLE SAY ABOUT EDUCATION?)
# ==============================================================================
def build_education_html(doc_data: dict) -> str:
    toc_items = []
    body_sections = []

    intro_html = f"""
    <section id="about-resource" class="fl-intro-card">
      <h2>{html.escape(doc_data['intro']['title'])}</h2>
      {render_blocks_html(doc_data['intro']['blocks'])}
    </section>
    """
    body_sections.append(intro_html)

    for part in doc_data["parts"]:
        pid = part["id"]
        toc_items.append(f'<li class="fl-toc-part"><a href="#{pid}">{html.escape(part["title"])}</a></li>')

        baton_html = ""
        if part.get("baton_callout"):
            bc = part["baton_callout"]
            baton_html = f"""
            <aside class="fl-baton-callout" id="baton-pass-diabetes-principle">
              <h3>{format_inline_md(bc['title'])}</h3>
              {render_blocks_html(bc['blocks'])}
            </aside>
            """

        part_header_html = f"""
        <section id="{pid}" class="fl-part-section fl-page-break-before">
          <div class="fl-part-banner">
            <span class="fl-part-badge">{html.escape(part['direction'])} Mandate</span>
            <h1>{html.escape(part['title'])}</h1>
            <h2 class="fl-part-subtitle">{html.escape(part['subtitle'])}</h2>
            {f'<p class="fl-part-tagline">{html.escape(part["tagline"])}</p>' if part.get("tagline") else ''}
          </div>
          {baton_html}
        </section>
        """
        body_sections.append(part_header_html)

        for ch in part["chapters"]:
            cid = ch["id"]
            toc_items.append(f'<li class="fl-toc-ch"><a href="#{cid}">{html.escape(ch["title"])}</a></li>')

            sec_html_list = []
            for sec in ch["sections"]:
              extra_print_card = ""
              if sec["id"] == "ch-8-sec-5":
                extra_print_card = """
                    <div class="fl-ch8-print-card print-only">
                      <img src="https://quickchart.io/qr?format=svg&margin=1&size=140&text=https%3A%2F%2Fmt-sin.ai%2Ffoundations%2Feducation.html%23ch-8-sec-5" alt="Chapter 8 Resource Directory QR" />
                      <div>
                        <strong>Scan to Open the Live Clickable Ministry &amp; Scientist Directory on Your Phone</strong><br/>
                        To keep this printed page uncluttered by 45+ raw web URLs and social handles, scan this QR code with your phone camera (or visit <strong>mt-sin.ai/foundations/education.html#ch-8-sec-5</strong>) for direct one-tap links to Answers in Genesis, PhD Scientist profiles, Turning Point USA, Living Waters, Grace to You, Hillsdale College, HSLDA, Master Books, and Apologia.
                      </div>
                    </div>
                    """
              sec_html_list.append(f"""
                <div id="{sec['id']}" class="fl-chapter-subsection">
                  <h3>{format_inline_md(sec['heading'])}</h3>
                  {render_blocks_html(sec['blocks'])}
                  {extra_print_card}
                </div>
                """)

            lab_html = ""
            if ch.get("lab"):
                lab = ch["lab"]
                lid = lab["id"]
                toc_items.append(f'<li class="fl-toc-lab"><a href="#{lid}">↳ Lab #{lab["lab_number"]} ({html.escape(lab["direction"])})</a></li>')
                lab_html = f"""
                <section id="{lid}" class="fl-lab-card fl-page-break-before" data-lab-num="{lab['lab_number']}">
                  <div class="fl-lab-header">
                    <span class="fl-lab-badge">{html.escape(lab['direction'])} Lab #{lab['lab_number']}</span>
                    <h3>{format_inline_md(lab['title'])}</h3>
                  </div>
                  <div class="fl-lab-body">
                    {render_blocks_html(lab['blocks'])}
                  </div>
                  <div class="fl-lab-actions no-print">
                    <button type="button" class="fl-btn fl-btn-primary" data-fl-print-lab="{lid}">🖨️ Print / Save Completed Lab #{lab['lab_number']}</button>
                    <button type="button" class="fl-btn fl-btn-light" data-fl-action="share-page" data-share-url="https://mt-sin.ai/fl/edu#{lid}" data-share-title="Lab #{lab['lab_number']}: {html.escape(lab['title'])} | What Does the Bible Say About Education?" data-share-desc="Interactive &amp; printable Sola Scriptura family/student lab worksheet from Foundations Library — 100% free to use, print, and share."><svg class="fl-icon-svg" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg> <span>Share Lab #{lab['lab_number']}</span></button>
                    <button type="button" class="fl-btn fl-btn-outline" data-fl-clear-lab="{lid}">Clear Lab #{lab['lab_number']} Inputs</button>
                  </div>
                </section>
                """

            ch_html = f"""
            <article id="{cid}" class="fl-chapter-article fl-page-break-before">
              <header class="fl-chapter-header">
                <h2>{format_inline_md(ch['title'])}</h2>
                {f'<p class="fl-chapter-subtitle">{format_inline_md(ch["subtitle"])}</p>' if ch.get("subtitle") else ''}
              </header>
              <div class="fl-chapter-intro">
                {render_blocks_html(ch['blocks'])}
              </div>
              {"".join(sec_html_list)}
              {lab_html}
            </article>
            """
            body_sections.append(ch_html)

    schema_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": ["Book", "LearningResource"],
                "@id": f"{EDU_CANONICAL_URL}#book",
                "name": "What Does the Bible Say About Education?: Foundational Truths for Parents and Students Survival Guide",
                "headline": "What Does the Bible Say About Education?",
                "alternativeHeadline": "Foundational Truths for Parents and Students Survival Guide",
                "author": [
                    {"@type": "Person", "name": "Rowley Shaw"},
                    {"@type": "Person", "name": "Patty Shaw"}
                ],
                "publisher": {
                    "@type": "Organization",
                    "name": "Mt. Sinai LLC",
                    "url": "https://mt-sin.ai/"
                },
                "contributor": [
                    {"@type": "Person", "name": "Ken Ham"},
                    {"@type": "Person", "name": "Patricia Engler"},
                    {"@type": "Organization", "name": "Answers in Genesis"}
                ],
                "inLanguage": "en-US",
                "isAccessibleForFree": True,
                "url": EDU_CANONICAL_URL,
                "sameAs": "https://mt-sin.ai/foundations/education.html",
                "educationalUse": ["Discipleship", "Worldview Training", "Homeschooling", "Student Apologetics"],
                "about": ["Biblical Education", "Sola Scriptura", "Creation Apologetics", "Deuteronomy 6", "Proverbs 19:27–29"]
            },
            {
                "@type": "FAQPage",
                "@id": f"{EDU_CANONICAL_URL}#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "Does the Bible speak about secular public education even though the words 'public school' are not in an English concordance?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Yes. God's Word addresses actions and mechanisms rather than 21st-century English buzzwords. Proverbs 19:27–29 issues a direct imperative command to cease listening (chadal) to formal instruction (musar) that causes one to stray from the words of knowledge—warning that judgments are prepared for scoffers (letsim)—and Proverbs 1:7 establishes that the fear of Yahweh is the beginning (reshith) of knowledge."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "When do most young people from Christian homes begin doubting the Bible?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "According to the national Already Gone study by Ken Ham and Britt Beemer (Answers in Genesis), over 83% of churchgoing youth who walk away began doubting the Bible in middle school (~40%) and high school (~44%), primarily triggered by evolutionary millions-of-years teaching in secular classrooms."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "How can a Christian student answer secular biology or geology test questions on evolution and millions of years without lying?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "By using the Attribution Frame (Daniel 1:17-20; 1 Peter 3:15-16): preface written test answers with 'According to the textbook's model...' or 'Secular uniformitarian geologists interpret...' This truthfully demonstrates mastery of the assigned course material while keeping a clear conscience before God."
                        }
                    }
                ]
            }
        ]
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>What Does the Bible Say About Education?: Foundational Truths for Parents &amp; Students | Foundations Library</title>
  <meta name="description" content="What Does the Bible Say About Education?: Foundational Truths for Parents and Students Survival Guide by Rowley and Patty Shaw (Mt. Sinai LLC), attributing Ken Ham, Patricia Engler, and Answers in Genesis." />
  <link rel="canonical" href="{EDU_CANONICAL_URL}" />
  <meta property="og:title" content="What Does the Bible Say About Education?: Foundational Truths for Parents &amp; Students" />
  <meta property="og:description" content="A Sola Scriptura survival guide for parents and students by Rowley and Patty Shaw (Mt. Sinai LLC), attributing Ken Ham, Patricia Engler, and Answers in Genesis." />
  <meta property="og:url" content="{EDU_CANONICAL_URL}" />
  <meta property="og:type" content="book" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;1,300;1,400;1,700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/foundations/fl-core.css?v=3" />
  <link rel="stylesheet" href="/foundations/fl-education.css" />
  <script type="application/ld+json">
{json.dumps(schema_ld, indent=2)}
  </script>
</head>
<body>

  <header class="fl-topbar no-print">
    <div class="fl-topbar-row1">
      <div class="fl-brand-group">
        <a href="/foundations/" class="fl-brand-title"><span class="fl-lbl-full">🏛️ Foundations Library</span><span class="fl-lbl-short">🏛️ FL</span></a>
        <span class="fl-topbar-sep">|</span>
        <a href="/365DBR/" target="_blank" rel="noopener" class="fl-dbr-link"><span class="fl-lbl-full">🕮 365DBR Daily</span><span class="fl-lbl-short">🕮 365DBR</span></a>
        <span class="fl-topbar-sep">|</span>
        <a href="/365DBR/bible.html" target="_blank" rel="noopener" class="fl-nav-link"><span class="fl-lbl-full">✝️ Multi-Translation Bible</span><span class="fl-lbl-short">✝️ Bible</span></a>
        <div id="fl-cobrand-box" class="fl-cobrand-banner"></div>
      </div>
      <div class="fl-top-actions">
        <a href="#support-fl" class="fl-btn fl-btn-support" title="Support Rowley &amp; Patty Shaw's independent writing"><span class="fl-lbl-full">❤️ Support FL 🏛️</span><span class="fl-lbl-short">❤️ FL</span></a>
        <button type="button" class="fl-btn fl-btn-light" data-fl-action="share-page" title="Freely share or co-brand this book"><svg class="fl-icon-svg" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg> <span class="fl-lbl-full">Share</span><span class="fl-lbl-short">Share</span></button>
        <button type="button" class="fl-btn fl-btn-light" data-fl-action="print-all-labs" title="Print only the 8 Family &amp; Student Lab Worksheets"><span class="fl-lbl-full">🖨️ Print All 8 Labs</span><span class="fl-lbl-short">🖨️ 8 Labs</span></button>
        <button type="button" class="fl-btn fl-btn-light" data-fl-action="print-page" title="Print full book and worksheets"><span class="fl-lbl-full">🖨️ Print</span><span class="fl-lbl-short">🖨️ Print</span></button>
      </div>
    </div>
    <div class="fl-topbar-row2">
      <button type="button" class="fl-btn fl-toc-toggle" data-fl-action="toggle-toc" aria-expanded="true" title="Toggle Table of Contents"><span class="fl-lbl-full">☰ Contents</span><span class="fl-lbl-short">☰ TOC</span></button>
      <span class="fl-topbar-sep">|</span>
      <a href="/foundations/{GOD_CANONICAL_SLUG}" class="fl-nav-link"><span class="fl-lbl-full">1: What About God? ↗</span><span class="fl-lbl-short">1: God ↗</span></a>
      <span class="fl-topbar-sep">|</span>
      <a href="#" class="fl-active-book" aria-current="page"><span class="fl-lbl-full">📖 Book 2: What Does the Bible Say About Education?<span class="fl-book-sub"> — Foundational Truths, Biblically Backed</span></span><span class="fl-lbl-short">📖 #2: Education</span></a>
    </div>
  </header>

  <div class="fl-layout">
    <aside id="toc-drawer" class="fl-sidebar no-print" aria-label="Book Table of Contents">
      <h3>Contents &amp; Labs</h3>
      <ul class="fl-toc-list">
        <li><a href="#about-resource">About &amp; Attribution</a></li>
        {"".join(toc_items)}
      </ul>
    </aside>

    <main class="fl-main">
      <div class="fl-hero-header">
        <h1>{html.escape(doc_data['metadata']['title'])}</h1>
        <p class="fl-hero-subtitle">{html.escape(doc_data['metadata']['subtitle'])}</p>
        <p class="fl-hero-meta">
          By <strong>Rowley and Patty Shaw</strong> (<em>Mt. Sinai LLC</em>) &bull;
          Attributing <strong>Ken Ham</strong>, <strong>Patricia Engler</strong>, and <strong>Answers in Genesis (AiG)</strong>, with <strong>Gemini</strong>
        </p>
      </div>

      {"".join(body_sections)}

      {load_support_footer_partial()}

      <div class="print-qr">
        <div class="print-qr-item">
            <div class="print-qr-title">Foundations Library</div>
            <img src="https://quickchart.io/qr?format=svg&margin=1&size=120&text=https%3A%2F%2Fmt-sin.ai%2Ffl%2F" alt="Foundations Library QR"/>
            <div class="print-qr-desc">100% free to read, print, duplicate &amp; share</div>
            <div class="print-qr-url">mt-sin.ai/fl/</div>
        </div>
        <div class="print-qr-item">
            <div class="print-qr-title">Book 1 Online</div>
            <img src="https://quickchart.io/qr?format=svg&margin=1&size=120&text=https%3A%2F%2Fmt-sin.ai%2Ffl%2Fgod" alt="Book Online QR"/>
            <div class="print-qr-desc">Tap any verse online for live Hebrew/Greek interlinear</div>
            <div class="print-qr-url">mt-sin.ai/fl/god</div>
        </div>
        <div class="print-qr-item">
            <div class="print-qr-title">365 Daily Bible Plan</div>
            <img src="https://quickchart.io/qr?format=svg&margin=1&size=120&text=https%3A%2F%2Fmt-sin.ai%2F365DBR%2F" alt="365DBR Daily QR"/>
            <div class="print-qr-desc">OT, NT, Psalms &amp; Proverbs (~15 min/day)</div>
            <div class="print-qr-url">mt-sin.ai/365DBR/</div>
        </div>
        <div class="print-qr-item">
            <div class="print-qr-title">Bible &amp; Interlinear Lookup</div>
            <img src="https://quickchart.io/qr?format=svg&margin=1&size=120&text=https%3A%2F%2Fmt-sin.ai%2F365DBR%2Fbible.html" alt="Multi-Translation Lookup QR"/>
            <div class="print-qr-desc">Hebrew/Greek + LSB &amp; KJV side-by-side</div>
            <div class="print-qr-url">mt-sin.ai/365DBR/bible.html</div>
        </div>
    </div>

  <!-- Live 365DBR Scripture Reader (100% Free & Non-Commercial) -->
  <aside id="bible-drawer" aria-hidden="true" inert>
    <div class="drawer-header">
      <span id="drawer-title">Scripture Reader</span>
      <div class="drawer-actions">
        <a id="drawer-ext" href="/365DBR/bible.html" target="_blank" rel="noopener">Open Full Tab ↗</a>
        <button class="drawer-close" id="drawer-close-btn" type="button">✕ Close</button>
      </div>
    </div>
    <iframe
      id="bible-frame"
      src="about:blank"
      title="365DBR Multi-Translation Bible">
    </iframe>
  </aside>

  <script src="/foundations/fl-core.js?v=3"></script>
</body>
</html>
"""

# ==============================================================================
# 7. MODULAR SINGLE-SOURCE SUPPORT FOOTER & ZERO-DUPLICATION SYNC
# ==============================================================================
SUPPORT_PARTIAL_PATH = BASE_DIR / "partials" / "support-footer.html"
HUB_INDEX_PATH = BASE_DIR / "index.html"

SHARE_BTN_SVG = '<svg class="fl-icon-svg" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>'

def load_support_footer_partial() -> str:
    if SUPPORT_PARTIAL_PATH.exists():
        return SUPPORT_PARTIAL_PATH.read_text(encoding="utf-8").strip()
    raise FileNotFoundError(f"Missing required partial: {SUPPORT_PARTIAL_PATH}")

def sync_support_footer_in_html(html_text: str) -> str:
    """Idempotently ensures exactly ONE #support-fl block exists using pure string slicing (zero regex)."""
    canonical_aside = load_support_footer_partial()
    html_text = html_text.replace("support-coffee", "support-fl")
    html_text = html_text.replace("fl-btn-coffee", "fl-btn-support")
    html_text = html_text.replace("data-coffee-link=", "data-support-link=")

    tag_Token = '<aside id="support-fl"'
    close_Token = "</aside>"

    first_pos = html_text.find(tag_Token)
    if first_pos != -1:
        # Strip ALL existing <aside id="support-fl"...>...</aside> blocks and insert exactly ONE at first_pos
        cleaned_parts = []
        cursor = 0
        inserted = False
        while True:
            pos = html_text.find(tag_Token, cursor)
            if pos == -1:
                cleaned_parts.append(html_text[cursor:])
                break
            # Back up over leading horizontal spaces on the same line so indentation stays identical
            line_start = pos
            while line_start > cursor and html_text[line_start - 1] in (" ", "\t"):
                line_start -= 1
            cleaned_parts.append(html_text[cursor:line_start])
            end_pos = html_text.find(close_Token, pos)
            if end_pos == -1:
                break
            after_close = end_pos + len(close_Token)
            if not inserted:
                cleaned_parts.append(canonical_aside)
                inserted = True
            else:
                # Also strip trailing newline from duplicate blocks
                if after_close < len(html_text) and html_text[after_close:after_close+2] == "\r\n":
                    after_close += 2
                elif after_close < len(html_text) and html_text[after_close] == "\n":
                    after_close += 1
            cursor = after_close
        return "".join(cleaned_parts)
    else:
        if "</main>" in html_text:
            return html_text.replace("</main>", canonical_aside + "\n  </main>", 1)
        elif '<aside id="bible-drawer"' in html_text:
            return html_text.replace('<aside id="bible-drawer"', canonical_aside + '\n\n<aside id="bible-drawer"', 1)
        return html_text

OT_BOOK_CODES = {
    "GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "RUT", "1SA", "2SA",
    "1KI", "2KI", "1CH", "2CH", "EZR", "NEH", "EST", "JOB", "PSA", "PRO",
    "ECC", "SNG", "ISA", "JER", "LAM", "EZK", "DAN", "HOS", "JOL", "AMO",
    "OBA", "JON", "MIC", "NAM", "HAB", "ZEP", "HAG", "ZEC", "MAL"
}

def _make_point_short_label(pt_num: int, text: str) -> str:
    clean = re.sub(r"\*+", "", text).strip()
    first_clause = re.split(r"[.;:—–]", clean)[0].strip()
    words = first_clause.split()
    if len(words) > 7:
        first_clause = " ".join(words[:7]) + "…"
    return f"Pt {pt_num}: {first_clause}"

def _render_god_refs_html(refs_md: str) -> tuple:
    """Converts markdown [Label](url) refs into HTML .refs links and extracts (ot_refs, nt_refs)."""
    s = refs_md.strip()
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1].strip()
    s = s.replace("http://localhost:8080/365DBR/", "/365DBR/")
    s = re.sub(r";\s*\|\s*", "; ", s)

    ot_refs = []
    nt_refs = []
    for m in re.finditer(r"\[([^\]]+)\]\(([^\)]+)\)", s):
        lbl, url = m.group(1).strip(), m.group(2).strip()
        m_bk = re.search(r"book=([A-Z0-9]+)", url)
        bk_code = m_bk.group(1) if m_bk else ""
        entry = {"label": lbl, "url": url, "book": bk_code}
        if bk_code in OT_BOOK_CODES:
            ot_refs.append(entry)
        else:
            nt_refs.append(entry)

    html_links = re.sub(
        r"\[([^\]]+)\]\(([^\)]+)\)",
        lambda m: f'<a href="{m.group(2).strip()}">{html.escape(m.group(1).strip())}</a>',
        s
    )
    return f"({html_links})", ot_refs, nt_refs

def parse_god_manuscript_to_json(raw_md: str) -> dict:
    lines = [l.strip() for l in raw_md.replace("\r\n", "\n").split("\n")]
    doc_data = {
        "schema_version": "1.2.0",
        "app": {
            "name": "Foundations Library",
            "abbr": "FL",
            "slug": "foundations",
            "storage_prefix": "fl_god_",
            "base_url": "https://mt-sin.ai/foundations/",
            "canonical_url": GOD_CANONICAL_URL,
            "short_url": "https://mt-sin.ai/fl/god",
            "sibling_education_url": EDU_CANONICAL_URL,
            "scripture_engine_url": "https://mt-sin.ai/365DBR/"
        },
        "metadata": {
            "id": "fl-book-god",
            "slug": "what-does-the-bible-say-about-god",
            "short_slug": "god",
            "title": "What We Know About God",
            "full_title": "What Does the Bible Say About God?: What We Know About God — Foundational Facts, Biblically Backed",
            "subtitle": "Foundational Facts, Biblically Backed",
            "authors": ["Rowley Shaw", "Patty Shaw"],
            "publisher": "Mt. Sinai LLC",
            "total_days": 8,
            "total_points": 40
        },
        "parts": [],
        "days": [],
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

    current_part = None
    current_day = None
    current_review = None
    pt_counter = 0
    input_counter = 0
    pending_pt_lines = []

    def ensure_part(title_str: str):
        nonlocal current_part
        p_num = len(doc_data["parts"]) + 1
        current_part = {
            "part_number": p_num,
            "id": f"part-{p_num}",
            "title": title_str,
            "day_ids": []
        }
        doc_data["parts"].append(current_part)

    for line in lines:
        if not line:
            continue
        if line.startswith("# ") and "What We Know" in line:
            continue
        if line.startswith("## ") and "Foundational Facts" in line:
            continue

        # Check for Day heading: ### Day N: ...
        m_day = re.match(r"^#{2,3}\s+Day\s+(\d+)\s*:\s*(.+)$", line, re.IGNORECASE)
        if m_day:
            day_num = int(m_day.group(1))
            day_title = f"Day {day_num}: {m_day.group(2).strip()}"
            if current_part is None:
                ensure_part("About God")
            current_day = {
                "day_number": day_num,
                "id": f"day-{day_num}",
                "part_id": current_part["id"],
                "part_title": current_part["title"],
                "title": day_title,
                "subtitle": "",
                "points": [],
                "review": None
            }
            current_part["day_ids"].append(current_day["id"])
            doc_data["days"].append(current_day)
            current_review = None
            continue

        # Check for Review heading: #### Day N Personal & Family Bible Study Review...
        m_rev = re.match(r"^#{3,4}\s+(.+Review.*)$", line, re.IGNORECASE)
        if m_rev and current_day is not None:
            d_num = current_day["day_number"]
            current_review = {
                "review_number": d_num,
                "id": f"review-{d_num}",
                "title": m_rev.group(1).strip(),
                "blocks": []
            }
            current_day["review"] = current_review
            continue

        # Check for Part heading (## About Us, ### About God, ### About the Bible..., ## About Redemption...)
        if re.match(r"^#{2,3}\s+About\s+", line, re.IGNORECASE):
            part_title = re.sub(r"^#+\s*", "", line).strip()
            ensure_part(part_title)
            current_review = None
            continue

        # Inside a Review block
        if current_review is not None:
            if line == "_____":
                input_counter += 1
                d_num = current_day["day_number"]
                q_idx = sum(1 for b in current_review["blocks"] if b["type"] == "review_input") + 1
                fid = f"fl_god_day{d_num}_q{q_idx}"
                prev_label = "Reflection Response:"
                if current_review["blocks"] and current_review["blocks"][-1]["type"] == "paragraph":
                    prev_label = current_review["blocks"].pop()["text"]
                current_review["blocks"].append({
                    "type": "review_input",
                    "input_id": fid,
                    "label": prev_label
                })
            else:
                current_review["blocks"].append({
                    "type": "paragraph",
                    "text": line
                })
            continue

        # Day subtitle line right after Day heading
        if current_day is not None and not current_day["points"] and not pending_pt_lines and line.startswith("**") and line.endswith("**"):
            current_day["subtitle"] = line.strip("*").strip()
            continue

        # Doctrinal Point & Scripture line
        if line.startswith("--"):
            pt_counter += 1
            if current_day is None:
                day_num = ((pt_counter - 1) // 5) + 1
                if current_part is None:
                    ensure_part("About God")
                current_day = {
                    "day_number": day_num,
                    "id": f"day-{day_num}",
                    "part_id": current_part["id"],
                    "part_title": current_part["title"],
                    "title": f"Day {day_num}",
                    "subtitle": "",
                    "points": [],
                    "review": None
                }
                current_part["day_ids"].append(current_day["id"])
                doc_data["days"].append(current_day)

            pt_text = " ".join(pending_pt_lines).strip()
            pending_pt_lines = []
            refs_raw = re.sub(r"^--\s*", "", line).strip()
            refs_html, ot_refs, nt_refs = _render_god_refs_html(refs_raw)
            current_day["points"].append({
                "point_number": pt_counter,
                "id": f"pt-{pt_counter}",
                "short_label": _make_point_short_label(pt_counter, pt_text),
                "text": pt_text,
                "refs_md": refs_raw,
                "refs_html": refs_html,
                "ot_refs": ot_refs,
                "nt_refs": nt_refs,
                "has_dual_witness": bool(ot_refs and nt_refs)
            })
        elif line.startswith("-"):
            pending_pt_lines = [re.sub(r"^-\s*", "", line).strip()]
        elif pending_pt_lines:
            pending_pt_lines.append(line)

    return doc_data

def build_god_html(doc_data: dict) -> str:
    toc_items = []
    body_parts = []
    rendered_parts = set()

    for day in doc_data["days"]:
        d_num = day["day_number"]
        d_id = day["id"]
        p_id = day["part_id"]
        p_title = day["part_title"]

        if p_id not in rendered_parts:
            rendered_parts.add(p_id)
            toc_items.append(f'<li class="fl-toc-part"><a href="#{p_id}">{html.escape(p_title)}</a></li>')
            body_parts.append(f'  <h2 id="{p_id}">{html.escape(p_title)}</h2>')

        toc_items.append(f'<li class="fl-toc-day"><a href="#{d_id}">{html.escape(day["title"])}</a></li>')

        pts_html = []
        for pt in day["points"]:
            pt_id = pt["id"]
            pt_num = pt["point_number"]
            toc_items.append(
                f'<li class="fl-toc-pt"><a href="#{pt_id}">{html.escape(pt["short_label"])}</a></li>'
            )
            pts_html.append(
                f'    <div id="{pt_id}" class="point"><span class="cross">†</span>'
                f'<span class="pt-num">{pt_num}.</span> { html.escape(pt["text"], quote=False) } '
                f'<span class="refs">{pt["refs_html"]}</span></div>'
            )

        rev_html = ""
        if day.get("review"):
            rev = day["review"]
            r_id = rev["id"]
            toc_items.append(
                f'<li class="fl-toc-lab"><a href="#{r_id}">↳ Day {d_num} Personal &amp; Family Review</a></li>'
            )
            rev_blocks_html = []
            for b in rev["blocks"]:
                if b["type"] == "paragraph":
                    rev_blocks_html.append(f'<p>{format_inline_md(b["text"])}</p>')
                elif b["type"] == "review_input":
                    fid = b["input_id"]
                    lbl = format_inline_md(b["label"])
                    rev_blocks_html.append(f"""
                    <div class="fl-lab-response-block">
                      <label for="{fid}" class="fl-response-label">{lbl}</label>
                      <textarea id="{fid}" class="fl-persist-input fl-textarea" data-storage-key="{fid}" rows="3" placeholder="Type your personal or family reflection here (saved automatically in this browser)..."></textarea>
                      <div class="fl-print-blank-line" data-print-for="{fid}">
                        <div>__________________________________________________________________________________________</div>
                        <div>__________________________________________________________________________________________</div>
                      </div>
                    </div>""")

            rev_html = f"""
    <section id="{r_id}" class="fl-lab-card" data-lab-num="{d_num}">
      <div class="fl-lab-header">
        <span class="fl-lab-badge">Day {d_num} Personal &amp; Family Review (Points {(d_num-1)*5+1}–{d_num*5})</span>
        <h4>{html.escape(rev["title"])}</h4>
      </div>
      <div class="fl-lab-body">
        {"".join(rev_blocks_html)}
      </div>
      <div class="fl-lab-actions no-print">
        <button type="button" class="fl-btn fl-btn-primary" data-fl-print-lab="{r_id}">🖨️ Print / Save Day {d_num} Review</button>
        <button type="button" class="fl-btn fl-btn-light" data-fl-action="share-page" data-share-url="https://mt-sin.ai/fl/god#{r_id}" data-share-title="Day {d_num} Review: {html.escape(day['title'])} | What We Know About God" data-share-desc="Interactive &amp; printable Sola Scriptura Daily Personal &amp; Family Bible Study Review from Foundations Library — 100% free to use, print, and share.">{SHARE_BTN_SVG} <span>Share Day {d_num} Review</span></button>
        <button type="button" class="fl-btn fl-btn-outline" data-fl-clear-lab="{r_id}">Clear Day {d_num} Inputs</button>
      </div>
    </section>"""

        sub_html = f'<p class="fl-day-sub">{html.escape(day["subtitle"])}</p>' if day.get("subtitle") else ""
        day_section_html = f"""
  <section id="{d_id}" class="fl-day-section">
    <header class="fl-day-header">
      <h3 class="fl-day-title">{html.escape(day["title"])}</h3>
      {sub_html}
    </header>
{chr(10).join(pts_html)}
{rev_html}
  </section>"""
        body_parts.append(day_section_html)

    support_html = load_support_footer_partial()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>What Does the Bible Say About God?: What We Know About God — Foundational Facts, Biblically Backed | Foundations Library</title>
  <link rel="canonical" href="{GOD_CANONICAL_URL}" />
  <meta name="description" content="A 40-point, 8-day foundational framework of Biblical truth and observational science, cross-referenced directly to the Legacy Standard Bible (LSB), KJV, and Original Hebrew/Greek.">
  <meta property="og:title" content="What We Know About God — Sola Scriptura Foundations" />
  <meta property="og:description" content="40 foundational truths of God, Creation, Mankind, and Salvation anchored directly in Scripture (LSB) with 8 Daily Personal &amp; Family Reviews." />
  <meta property="og:url" content="{GOD_CANONICAL_URL}" />
  <meta property="og:type" content="article" />
  <meta name="twitter:card" content="summary" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Cinzel:wght@400;600;700&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/foundations/fl-core.css?v=3">
  <link rel="stylesheet" href="/foundations/fl-god.css">
</head>
<body>
  <header class="fl-topbar no-print">
    <div class="fl-topbar-row1">
      <div class="fl-brand-group">
        <a href="/foundations/" class="fl-brand-title"><span class="fl-lbl-full">🏛️ Foundations Library</span><span class="fl-lbl-short">🏛️ FL</span></a>
        <span class="fl-topbar-sep">|</span>
        <a href="/365DBR/" target="_blank" rel="noopener" class="fl-dbr-link"><span class="fl-lbl-full">🕮 365DBR Daily</span><span class="fl-lbl-short">🕮 365DBR</span></a>
        <span class="fl-topbar-sep">|</span>
        <a href="/365DBR/bible.html" target="_blank" rel="noopener" class="fl-nav-link"><span class="fl-lbl-full">✝️ Multi-Translation Bible</span><span class="fl-lbl-short">✝️ Bible</span></a>
        <div id="fl-cobrand-box" class="fl-cobrand-banner"></div>
      </div>
      <div class="fl-top-actions">
        <a href="#support-fl" class="fl-btn fl-btn-support" title="Support Rowley &amp; Patty Shaw's independent writing"><span class="fl-lbl-full">❤️ Support FL 🏛️</span><span class="fl-lbl-short">❤️ FL</span></a>
        <button type="button" class="fl-btn fl-btn-light" data-fl-action="share-page" title="Freely share or co-brand this book">{SHARE_BTN_SVG} <span class="fl-lbl-full">Share</span><span class="fl-lbl-short">Share</span></button>
        <button type="button" class="fl-btn fl-btn-light" data-fl-action="print-all-labs" title="Print only the 8 Daily Personal &amp; Family Review Worksheets"><span class="fl-lbl-full">🖨️ Print All 8 Reviews</span><span class="fl-lbl-short">🖨️ 8 Reviews</span></button>
        <button type="button" class="fl-btn fl-btn-light" data-fl-action="print-page" title="Print full book and reviews"><span class="fl-lbl-full">🖨️ Print</span><span class="fl-lbl-short">🖨️ Print</span></button>
      </div>
    </div>
    <div class="fl-topbar-row2">
      <button type="button" class="fl-btn fl-toc-toggle" data-fl-action="toggle-toc" aria-expanded="true" title="Toggle Table of Contents"><span class="fl-lbl-full">☰ Contents</span><span class="fl-lbl-short">☰ TOC</span></button>
      <span class="fl-topbar-sep">|</span>
      <a href="#" class="fl-active-book" aria-current="page"><span class="fl-lbl-full">📖 Book 1: What We Know About God<span class="fl-book-sub"> — Foundational Facts, Biblically Backed</span></span><span class="fl-lbl-short">📖 #1: God</span></a>
      <span class="fl-topbar-sep">|</span>
      <a href="/foundations/{EDU_CANONICAL_SLUG}" class="fl-nav-link"><span class="fl-lbl-full">2: Biblical Education ↗</span><span class="fl-lbl-short">2: Education ↗</span></a>
    </div>
  </header>

  <div class="fl-layout">
    <aside id="toc-drawer" class="fl-sidebar no-print" aria-label="Book 1 Table of Contents">
      <h3>8-Day Study &amp; 40 Truths</h3>
      <ul class="fl-toc-list">
        {"".join(toc_items)}
      </ul>
    </aside>

    <main class="fl-main">
      <div class="container">
        <div class="page-hero">
          <h1>What We Know About God</h1>
          <p class="subtitle">Foundational Facts, Biblically Backed — 8-Day Personal &amp; Family Study Guide</p>
        </div>

{chr(10).join(body_parts)}

        {support_html}
      </div>

      <div class="print-qr">
        <div class="print-qr-item">
          <div class="print-qr-title">Foundations Library</div>
          <img src="https://quickchart.io/qr?format=svg&margin=1&size=120&text=https%3A%2F%2Fmt-sin.ai%2Ffl%2F" alt="Foundations Library QR"/>
          <div class="print-qr-desc">Free Sola Scriptura books &amp; family equipping guides</div>
          <div class="print-qr-url">mt-sin.ai/fl/</div>
        </div>
        <div class="print-qr-item">
          <div class="print-qr-title">Book 1 Online</div>
          <img src="https://quickchart.io/qr?format=svg&margin=1&size=120&text=https%3A%2F%2Fmt-sin.ai%2Ffl%2Fgod" alt="Book Online QR"/>
          <div class="print-qr-desc">Tap any verse online for live Hebrew/Greek interlinear</div>
          <div class="print-qr-url">mt-sin.ai/fl/god</div>
        </div>
        <div class="print-qr-item">
          <div class="print-qr-title">365 Daily Bible Plan</div>
          <img src="https://quickchart.io/qr?format=svg&margin=1&size=120&text=https%3A%2F%2Fmt-sin.ai%2F365DBR%2F" alt="365DBR Daily QR"/>
          <div class="print-qr-desc">OT, NT, Psalms &amp; Proverbs (~15 min/day)</div>
          <div class="print-qr-url">mt-sin.ai/365DBR/</div>
        </div>
        <div class="print-qr-item">
          <div class="print-qr-title">Bible &amp; Interlinear Lookup</div>
          <img src="https://quickchart.io/qr?format=svg&margin=1&size=120&text=https%3A%2F%2Fmt-sin.ai%2F365DBR%2Fbible.html" alt="Multi-Translation Lookup QR"/>
          <div class="print-qr-desc">Hebrew/Greek + LSB &amp; KJV side-by-side</div>
          <div class="print-qr-url">mt-sin.ai/365DBR/bible.html</div>
        </div>
      </div>
    </main>
  </div>

  <!-- Live 365DBR Scripture Reader (100% Free & Non-Commercial) -->
  <aside id="bible-drawer" aria-hidden="true" inert>
    <div class="drawer-header">
      <span id="drawer-title">Scripture Reader</span>
      <div class="drawer-actions">
        <a id="drawer-ext" href="/365DBR/bible.html" target="_blank" rel="noopener">Open Full Tab ↗</a>
        <button class="drawer-close" id="drawer-close-btn" type="button">✕ Close</button>
      </div>
    </div>
    <iframe
      id="bible-frame"
      src="about:blank"
      title="365DBR Multi-Translation Bible">
    </iframe>
  </aside>

  <script src="/foundations/fl-core.js?v=3"></script>
</body>
</html>
"""

def sync_book1_god_html(dry_run: bool = False):
    """Compiles raw/god_manuscript.md -> data/god.json and what-does-the-bible-say-about-god.html."""
    if not GOD_RAW_MD_PATH.exists():
        raise FileNotFoundError(f"Book 1 source manuscript not found at: {GOD_RAW_MD_PATH}")
    raw_md = GOD_RAW_MD_PATH.read_text(encoding="utf-8")
    god_data = parse_god_manuscript_to_json(raw_md)
    write_json_if_changed(GOD_JSON_OUT_PATH, god_data, dry_run=dry_run)

    html_out = build_god_html(god_data)
    html_out = sync_support_footer_in_html(html_out)
    write_if_changed(GOD_CANONICAL_PATH, html_out, dry_run=dry_run)

    if HUB_INDEX_PATH.exists():
        hub_content = HUB_INDEX_PATH.read_text(encoding="utf-8")
        hub_content = sync_support_footer_in_html(hub_content)
        write_if_changed(HUB_INDEX_PATH, hub_content, dry_run=dry_run)

# ==============================================================================
# 8. REDIRECT STUBS, GODADDY .HTACCESS & CASE-INSENSITIVE ROUTER (CSP-SAFE)
# ==============================================================================
def make_redirect_stub(target_path: str, title_label: str) -> str:
  canonical_full = f"https://mt-sin.ai{target_path}"
  return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Redirecting to {title_label} | Foundations Library (Mt. Sinai LLC)</title>
  <link rel="canonical" href="{canonical_full}" />
  <meta name="robots" content="noindex, follow" />
  <meta http-equiv="refresh" content="0; url={target_path}" />
</head>
<body style="font-family: Georgia, serif; padding: 40px; color: #1f1b18; background: #fdfbf7;">
  <p>Redirecting to <strong>{title_label}</strong> in the Mt. Sinai LLC Foundations Library...</p>
  <p><a href="{target_path}">Click here if you are not redirected automatically.</a></p>
</body>
</html>
"""


HTACCESS_CONTENT = r"""# ==============================================================================
# Foundations Library (apps/foundations/.htaccess) — Mt. Sinai LLC
# GoDaddy / Apache Case-Insensitive Router & CSP Header Override
# ==============================================================================
Options -MultiViews +FollowSymLinks
RewriteEngine On
RewriteBase /foundations/

# 0. Override Root CSP so 365DBR Iframe ('self') & Print QR Codes Load Cleanly
<IfModule mod_headers.c>
  Header set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https: https://quickchart.io; frame-src 'self'; frame-ancestors 'self'; connect-src 'self';"
</IfModule>

# 1. Enable Apache mod_speling if available on GoDaddy server (auto-fixes mixed case)
<IfModule mod_speling.c>
  CheckSpelling On
  CheckCaseOnly On
</IfModule>

# 2. Case-Insensitive [NC] 301 Redirects for Book 1 (What Does the Bible Say About God?)
RewriteCond %{REQUEST_URI} !^/foundations/what-does-the-bible-say-about-god\\.html$
RewriteRule ^(what-does-the-bible-say-about-god|what-we-know-about-god|what-we-know|what_we_know|what_do_we_know|god)(\\.html)?$ /foundations/what-does-the-bible-say-about-god.html [R=301,L,NC,QSA]

# 3. Case-Insensitive [NC] 301 Redirects for Book 2 (What Does the Bible Say About Education?)
RewriteCond %{REQUEST_URI} !^/foundations/what-does-the-bible-say-about-education\\.html$
RewriteRule ^(what-does-the-bible-say-about-education|biblical-education|education)(\\.html)?$ /foundations/what-does-the-bible-say-about-education.html [R=301,L,NC,QSA]

# 4. Fallback Case-Normalizer for any other future Foundations Library guide
RewriteRule ^support(\.html)?/?$ /foundations/#support-fl [R=302,L,NC,NE]
RewriteRule ^(coffee|support5)(\.html)?/?$ https://connect.intuit.com/portal/app/CommerceNetwork/view/scs-v1-455b9660e2924c238018ff5e2d3b67933b548fe02d4945ed9ccdb365515b6a6f28ed8416a246409d93f611b3a965160d-1?locale=EN_US&cta [R=302,L,NC,NE]
RewriteRule ^support3(\.html)?/?$ https://connect.intuit.com/pay/PattyShaw/scs-v1-c1c2a59720144473a27aee64ff2d9701e09df4cb5801458fb017d7b16833e957f51b78ed6ca2491c8fd5923d577d212f-0?locale=EN_US&cta=saveandcopylink [R=302,L,NC,NE]
RewriteRule ^support10(\.html)?/?$ https://connect.intuit.com/pay/PattyShaw/scs-v1-02fd4483942540d0a9766b7279d6912e6f9fcef4710e4c28a72b95be583e33f6a97dd9f96bd4431fa5640ebfc369d7bd-1?locale=EN_US&cta=saveandcopylink [R=302,L,NC,NE]
RewriteRule ^support25(\.html)?/?$ https://connect.intuit.com/pay/PattyShaw/scs-v1-dc9f5b03e1b24c53a659e8e409a0b2e66698a1f75d024e7f88de8b15c83afbee92e8ce95daff4bbcb59c12de14a4385a-0?locale=EN_US&cta=saveandcopylink [R=302,L,NC,NE]
RewriteRule ^support50(\.html)?/?$ https://connect.intuit.com/pay/PattyShaw/scs-v1-cc97092ddbce45b7a7bf9cdb0e07e11cb6f52f0dd12d40ae89554617e1e4a4f393af842986d94db0b6401b68127bbbeb-0?locale=EN_US&cta=saveandcopylink [R=302,L,NC,NE]

ErrorDocument 404 /foundations/404-case-router.html
"""

CASE_ROUTER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Routing | Foundations Library (Mt. Sinai LLC)</title>
  <meta name="robots" content="noindex, follow" />
  <link rel="stylesheet" href="/foundations/fl-core.css?v=3" />
</head>
<body data-fl-case-router="true" style="font-family: Georgia, serif; padding: 40px;">
  <h2>Mt. Sinai LLC — Foundations Library</h2>
  <p>Select a resource below:</p>
  <ul>
    <li><a href="/foundations/what-does-the-bible-say-about-god.html">1: What Does the Bible Say About God? (What We Know About God — Foundational Facts, Biblically Backed)</a></li>
    <li><a href="/foundations/what-does-the-bible-say-about-education.html">2: What Does the Bible Say About Education? (Foundational Truths for Parents &amp; Students)</a></li>
  </ul>
  <script src="/foundations/fl-core.js?v=3"></script>
</body>
</html>
"""

# ==============================================================================
# 9. MAIN EXECUTION PIPELINE
# ==============================================================================

MTSINAI_HTACCESS_PATH = BASE_DIR.parent / "mtsinai" / ".htaccess"
MONOREPO_HTACCESS_PATH = BASE_DIR.parent.parent / ".htaccess"

FL_ROOT_REWRITE_BLOCK = r"""
<IfModule mod_rewrite.c>
  # ?? Foundations Library Ultra-Short Print & QR Redirects (/fl/*)
  RewriteEngine On
  RewriteRule ^fl/?$ /foundations/ [R=301,L,NC,QSA]
  RewriteRule ^fl/god(\.html)?/?$ /foundations/what-does-the-bible-say-about-god.html [R=301,L,NC,QSA]
  RewriteRule ^fl/edu(\.html)?/?$ /foundations/what-does-the-bible-say-about-education.html [R=301,L,NC,QSA]
</IfModule>
"""

def sync_root_htaccess(dry_run: bool = False):
    if not MTSINAI_HTACCESS_PATH.exists():
        print(f" [!] Skipping root .htaccess sync: {MTSINAI_HTACCESS_PATH} not found.")
        return
    root_content = MTSINAI_HTACCESS_PATH.read_text(encoding="utf-8")
    if "RewriteRule ^fl/god" not in root_content:
        root_content = root_content.rstrip() + "\n" + FL_ROOT_REWRITE_BLOCK
    write_if_changed(MTSINAI_HTACCESS_PATH, root_content, dry_run=dry_run)
    write_if_changed(MONOREPO_HTACCESS_PATH, root_content, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(
        description="Foundations Library (FL) Compiler — Idempotent Builder"
    )
    parser.add_argument(
        "--target",
        choices=["all", "bks", "bk-1", "bk-2", "stubs", "htaccess"],
        default=None,
        help="Build scope: all, bks (all books), stubs (redirect stubs), or htaccess (routing)."
    )
    parser.add_argument(
        "--bk-1",
        action="store_true",
        help="Compile/sync Foundations Book 1 (What Does the Bible Say About God?)"
    )
    parser.add_argument(
        "--bk-2",
        action="store_true",
        help="Compile Foundations Book 2 (What Does the Bible Say About Education?)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report which files would be modified vs. unchanged without writing to disk."
    )
    args = parser.parse_args()

    target = args.target
    if target is None and not (args.bk_1 or args.bk_2):
        target = "bks"

    do_bk1 = args.bk_1 or (target in ("all", "bks", "bk-1"))
    do_bk2 = args.bk_2 or (target in ("all", "bks", "bk-2"))
    do_stubs = target in ("all", "stubs")
    do_htaccess = target in ("all", "htaccess")

    mode_label = "DRY-RUN" if args.dry_run else "WRITE"
    print(f"[FL Build Start — Mode: {mode_label} | bk1={do_bk1}, bk2={do_bk2}, stubs={do_stubs}, htaccess={do_htaccess}]")

    if do_bk2:
        if not RAW_MD_PATH.exists():
            raise FileNotFoundError(f"Source manuscript not found at: {RAW_MD_PATH}")
        raw_text = RAW_MD_PATH.read_text(encoding="utf-8")
        cleaned_md = clean_manuscript_text(raw_text)
        doc_data = parse_manuscript_to_json(cleaned_md)

        write_json_if_changed(JSON_OUT_PATH, doc_data, dry_run=args.dry_run)
        html_output = build_education_html(doc_data)
        write_if_changed(EDU_CANONICAL_PATH, html_output, dry_run=args.dry_run)

    if do_bk1:
        sync_book1_god_html(dry_run=args.dry_run)

    if do_stubs:
        stubs = [
            (BASE_DIR / "education.html", f"/foundations/{EDU_CANONICAL_SLUG}", "What Does the Bible Say About Education?"),
            (BASE_DIR / "god.html", f"/foundations/{GOD_CANONICAL_SLUG}", "What Does the Bible Say About God? (What We Know About God)"),
            (BASE_DIR / "what-we-know.html", f"/foundations/{GOD_CANONICAL_SLUG}", "What Does the Bible Say About God? (What We Know About God)"),
            (BASE_DIR / "what-we-know-about-god.html", f"/foundations/{GOD_CANONICAL_SLUG}", "What Does the Bible Say About God? (What We Know About God)"),
        ]
        for stub_path, target_url, label in stubs:
            write_if_changed(stub_path, make_redirect_stub(target_url, label), dry_run=args.dry_run)

        if REDIRECT_365DBR_PATH.parent.exists():
            write_if_changed(
                REDIRECT_365DBR_PATH,
                make_redirect_stub(f"/foundations/{GOD_CANONICAL_SLUG}", "What Does the Bible Say About God? (Foundations Library)"),
                dry_run=args.dry_run
            )

    if do_htaccess:
        write_if_changed(HTACCESS_PATH, HTACCESS_CONTENT, dry_run=args.dry_run)
        write_if_changed(CASE_ROUTER_PATH, CASE_ROUTER_HTML, dry_run=args.dry_run)
        sync_root_htaccess(dry_run=args.dry_run)

    print("[FL Build Complete]")


if __name__ == "__main__":
    main()
