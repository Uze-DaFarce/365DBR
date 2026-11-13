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
      main_url = build_365dbr_url(book_code, ref)
      linked = (
          f'<a href="{main_url}" class="fl-scripture-link" '
          f'title="Open {book_name} {ref} in 365DBR Scripture Reader">{book_name} {ref}</a>'
      )

      if tail:
        parts = re.split(r"(\s*;\s*)", tail)
        for p in parts:
          if re.match(r"^\s*;\s*$", p):
            linked += p
          elif p.strip():
            sub_url = build_365dbr_url(book_code, p.strip())
            linked += (
                f'<a href="{sub_url}" class="fl-scripture-link" '
                f'title="Open {book_name} {p.strip()} in 365DBR Scripture Reader">{p}</a>'
            )
      return linked

    out.append(CITATION_REGEX.sub(_replace_match, tok))
  return "".join(out)

# ==============================================================================
# 3. SURGICAL MANUSCRIPT CLEANUP RULES
# ==============================================================================
def clean_manuscript_text(raw_text: str) -> str:
    text = raw_text.replace("\r\n", "\n").replace("\u00a0", " ")
    for esc, char in [(r"\#", "#"), (r"\!", "!"), (r"\~", "~"), (r"\_", "_"), (r"\[", "["), (r"\]", "]"), (r"\&", "&")]:
        text = text.replace(esc, char)
    text = text.replace("directed primary from Parent to Child", "directed primarily from Parent to Child")
    text = re.sub(r"\(Genesis 39:9\)\.Notice", "(Genesis 39:9). Notice", text)
    text = re.sub(r"^(\s*\d+\.\s+)\*\*\d+\.\s+", r"\1**", text, flags=re.MULTILINE)
    text = re.sub(r"^(\s*[\-\*]\s+)\*\*(\d+\.)\s+", r"\1**", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*1\.\s+\*\*Step 4:\s*Family Prayer\*\*", "**Step 4: Family Prayer**", text, flags=re.MULTILINE)
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
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
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
        "parts": []
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
def format_inline_md(text: str) -> str:
    s = html.escape(text, quote=False)
    s = re.sub(r"&lt;(https?://[^&>\s]+)&gt;", r'<a href="\1" target="_blank" rel="noopener" class="fl-ext-link">\1</a>', s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<a href="\2" target="_blank" rel="noopener" class="fl-ext-link">\1</a>', s)
    s = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
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
          "Everyone, after he has been fully trained (katartizō — καταρτίζω), will be like his teacher." — Luke 6:40
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
            html_out.append(f"<li>{format_inline_md(b['text'])}</li>")
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
                sec_html_list.append(f"""
                <div id="{sec['id']}" class="fl-chapter-subsection">
                  <h3>{format_inline_md(sec['heading'])}</h3>
                  {render_blocks_html(sec['blocks'])}
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
                    <button type="button" class="fl-btn fl-btn-primary" onclick="FLApp.printLab('{lid}')">🖨️ Print / Save Completed Lab #{lab['lab_number']}</button>
                    <button type="button" class="fl-btn fl-btn-outline" onclick="FLApp.clearLab('{lid}')">Clear Lab #{lab['lab_number']} Inputs</button>
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
                "about": ["Biblical Education", "Sola Scriptura", "Creation Apologetics", "Deuteronomy 6", "Proverbs 19:27"]
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
                            "text": "Yes. God's Word addresses actions and mechanisms rather than 21st-century English buzzwords. Proverbs 19:27 issues a direct imperative command to cease listening (chadal) to formal instruction (musar) that causes one to stray from the words of knowledge, and Proverbs 1:7 establishes that the fear of Yahweh is the beginning (reshith) of knowledge."
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
  <link rel="stylesheet" href="/foundations/fl-core.css" />
  <link rel="stylesheet" href="/foundations/fl-education.css" />
  <script type="application/ld+json">
{json.dumps(schema_ld, indent=2)}
  </script>
</head>
<body>

  <header class="fl-topbar no-print">
    <div class="fl-brand-group">
      <a href="/foundations/" class="fl-brand-title">🏛️ Foundations Library</a>
      <span class="fl-topbar-sep">›</span>
      <a href="/foundations/{GOD_CANONICAL_SLUG}" class="fl-nav-link">1: What About God ↗</a>
      <span class="fl-topbar-sep">|</span>
      <a href="#" class="fl-active-book" aria-current="page" title="Currently Reading: What Does the Bible Say About Education?">📖 2: What About Education?</a>
      <span class="fl-topbar-sep">|</span>
      <a href="/365DBR/" target="_blank" rel="noopener" class="fl-dbr-link">📖 365DBR Daily</a>
      <span class="fl-topbar-sep">|</span>
      <a href="/365DBR/bible.html" target="_blank" rel="noopener" class="fl-nav-link">Multi-Translation Bible</a>
      <div id="fl-cobrand-box" class="fl-cobrand-banner"></div>
    </div>
    <div class="fl-top-actions">
      <a href="#support-coffee" class="fl-btn fl-btn-coffee" title="Support Rowley &amp; Patty Shaw's independent writing">☕ Buy Your Brother a Coffee</a>
      <button type="button" class="fl-btn fl-btn-light" onclick="window.print()">🖨️ Print Full Book / Worksheets</button>
    </div>
  </header>

  <div class="fl-layout">
    <aside class="fl-sidebar no-print" aria-label="Book Table of Contents">
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

      <aside id="support-coffee" class="fl-support-footer no-print" aria-label="Voluntary Ministry Support">
        <p class="fl-support-text">
          <strong>☕ Support Independent Sola Scriptura Writing:</strong> All Scripture tools (<em>365DBR</em> &amp; the <em>Legacy Standard Bible</em>) are provided 100% free of charge and strictly non-commercial. Voluntary gifts solely support <strong>Rowley &amp; Patty Shaw's</strong> independent writing and server hosting.
        </p>
        <a href="#support-coffee" class="fl-btn fl-btn-coffee" data-coffee-link="pending">☕ Buy Your Brother a Coffee</a>
      </aside>

      <footer class="fl-print-footer">
        <p><strong>Foundations Library (Mt. Sinai LLC):</strong> {EDU_CANONICAL_URL} (Short Link: https://mt-sin.ai/foundations/education.html) &bull; <strong>365DBR Scripture Engine:</strong> https://mt-sin.ai/365DBR/</p>
      </footer>
    </main>
  </div>

  <!-- Live 365DBR Scripture Reader (100% Free & Non-Commercial) -->
  <aside id="bible-drawer" aria-hidden="true">
    <div class="drawer-header">
      <span id="drawer-title">365DBR Scripture Reader (LSB / KJV / Interlinear)</span>
      <div class="drawer-actions">
        <a id="drawer-ext" href="/365DBR/bible.html" target="_blank" rel="noopener">Open Full Tab ↗</a>
        <button class="drawer-close" id="drawer-close-btn" type="button">✕ Close</button>
      </div>
    </div>
    <iframe
      id="bible-frame"
      srcdoc="<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>365DBR Scripture Reader</title></head><body style='margin:0;padding:24px;background:#fdfbf7;color:#5c4028;font-family:Georgia,serif;font-size:15px;'>Select any Scripture reference link to compare Hebrew/Greek interlinear and literal English translations side-by-side.</body></html>"
      title="365DBR Multi-Translation Bible">
    </iframe>
  </aside>

  <script src="/foundations/fl-core.js"></script>
</body>
</html>
"""

# ==============================================================================
# 7. SURGICAL METADATA & CANONICAL SYNC FOR BOOK 1 (WHAT WE KNOW ABOUT GOD)
# ==============================================================================
def sync_book1_god_html():
    """Updates canonical URLs and <title> inside what-does-the-bible-say-about-god.html."""
    if not GOD_CANONICAL_PATH.exists():
        print(f" [!] Skipping Book 1 sync: {GOD_CANONICAL_PATH} not found yet.")
        return

    content = GOD_CANONICAL_PATH.read_text(encoding="utf-8")

    # 1. Update legacy /365DBR/What_We_Know.html URLs to canonical /foundations/what-does-the-bible-say-about-god.html
    content = content.replace("https://mt-sin.ai/365DBR/What_We_Know.html", GOD_CANONICAL_URL)
    content = content.replace("https://mt-sin.ai/foundations/what-we-know.html", GOD_CANONICAL_URL)
    content = content.replace("https://mt-sin.ai/foundations/what-we-know-about-god.html", GOD_CANONICAL_URL)

    # 2. Update <title> using Foundational Facts, Biblically Backed (no '40' or 'Points')
    new_title = "<title>What Does the Bible Say About God?: What We Know About God — Foundational Facts, Biblically Backed | Foundations Library</title>"
    content = re.sub(r"<title>.*?</title>", new_title, content, count=1, flags=re.IGNORECASE | re.DOTALL)

    # 3. Ensure <link rel="canonical"> exists and points to GOD_CANONICAL_URL
    if 'rel="canonical"' in content:
        content = re.sub(
            r'<link\s+rel="canonical"\s+href="[^"]*"\s*/?>',
            f'<link rel="canonical" href="{GOD_CANONICAL_URL}" />',
            content,
            flags=re.IGNORECASE
        )
    else:
        content = content.replace("</title>", f'</title>\n  <link rel="canonical" href="{GOD_CANONICAL_URL}" />', 1)

    # 4. Upgrade visible <h1> if it currently says just "What We Know"
    content = re.sub(
        r"(<h1[^>]*>)\s*What We Know\s*(</h1>)",
        r"\1What We Know About God\2",
        content,
        flags=re.IGNORECASE
    )

    # 5. Ensure relative bible.html links point to /365DBR/bible.html
    content = re.sub(r'href="(?:\./|/365DBR/)?bible\.html', 'href="/365DBR/bible.html', content)
    GOD_CANONICAL_PATH.write_text(content, encoding="utf-8")

# ==============================================================================
# 8. REDIRECT STUBS, GODADDY .HTACCESS & CASE-INSENSITIVE ROUTER
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
  <script>
    (function() {{
      var targetBase = "{target_path}";
      var search = window.location.search || "";
      var hash = window.location.hash || "";
      window.location.replace(targetBase + search + hash);
    }})();
  </script>
  <meta http-equiv="refresh" content="0; url={target_path}" />
</head>
<body style="font-family: Georgia, serif; padding: 40px; color: #1f1b18; background: #f7f4ef;">
  <p>Redirecting to <strong>{title_label}</strong> in the Mt. Sinai LLC Foundations Library...</p>
  <p><a id="fallback-link" href="{target_path}">Click here if you are not redirected automatically.</a></p>
  <script>
    document.getElementById("fallback-link").href = "{target_path}" + (window.location.search || "") + (window.location.hash || "");
  </script>
</body>
</html>
"""

HTACCESS_CONTENT = """# ==============================================================================
# Foundations Library (apps/foundations/.htaccess) — Mt. Sinai LLC
# GoDaddy / Apache Case-Insensitive & Short-Slug Funnel Router
# ==============================================================================
Options -MultiViews +FollowSymLinks
RewriteEngine On
RewriteBase /foundations/

# 1. Enable Apache mod_speling if available on GoDaddy server (auto-fixes mixed case)
<IfModule mod_speling.c>
  CheckSpelling On
  CheckCaseOnly On
</IfModule>

# 2. Case-Insensitive [NC] 301 Redirects for Book 1 (What Does the Bible Say About God? / What We Know About God)
RewriteCond %{REQUEST_URI} !^/foundations/what-does-the-bible-say-about-god\\.html$
RewriteRule ^(what-does-the-bible-say-about-god|what-we-know-about-god|what-we-know|what_we_know|what_do_we_know|god)(\\.html)?$ /foundations/what-does-the-bible-say-about-god.html [R=301,L,NC,QSA]

# 3. Case-Insensitive [NC] 301 Redirects for Book 2 (What Does the Bible Say About Education?)
RewriteCond %{REQUEST_URI} !^/foundations/what-does-the-bible-say-about-education\\.html$
RewriteRule ^(what-does-the-bible-say-about-education|biblical-education|education)(\\.html)?$ /foundations/what-does-the-bible-say-about-education.html [R=301,L,NC,QSA]

# 4. Fallback Case-Normalizer for any other future Foundations Library guide
ErrorDocument 404 /foundations/404-case-router.html
"""

CASE_ROUTER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Routing | Foundations Library (Mt. Sinai LLC)</title>
  <meta name="robots" content="noindex, follow" />
  <script>
    (function() {
      var path = window.location.pathname || "";
      var lower = path.toLowerCase().replace(/_/g, "-");
      var search = window.location.search || "";
      var hash = window.location.hash || "";

      if (lower.indexOf("god") !== -1 || lower.indexOf("what-we-know") !== -1) {
        window.location.replace("/foundations/what-does-the-bible-say-about-god.html" + search + hash);
        return;
      }
      if (lower.indexOf("education") !== -1) {
        window.location.replace("/foundations/what-does-the-bible-say-about-education.html" + search + hash);
        return;
      }
      if (path !== lower) {
        window.location.replace(lower + search + hash);
      }
    })();
  </script>
</head>
<body style="font-family: Georgia, serif; padding: 40px; color: #1f1b18; background: #f7f4ef;">
  <h2>Mt. Sinai LLC — Foundations Library</h2>
  <p>Select a resource below:</p>
  <ul>
    <li><a href="/foundations/what-does-the-bible-say-about-god.html">What Does the Bible Say About God?: What We Know About God (Foundational Facts, Biblically Backed)</a></li>
    <li><a href="/foundations/what-does-the-bible-say-about-education.html">What Does the Bible Say About Education?: Foundational Truths for Parents &amp; Students</a></li>
  </ul>
</body>
</html>
"""

# ==============================================================================
# 9. MAIN EXECUTION PIPELINE
# ==============================================================================
def main():
    if not RAW_MD_PATH.exists():
        raise FileNotFoundError(f"Source manuscript not found at: {RAW_MD_PATH}")

    raw_text = RAW_MD_PATH.read_text(encoding="utf-8")
    cleaned_md = clean_manuscript_text(raw_text)
    doc_data = parse_manuscript_to_json(cleaned_md)

    # 1. Write Canonical JSON Data Layer (data/education.json)
    JSON_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT_PATH.write_text(json.dumps(doc_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # 2. Write Book 2 Canonical SEO Guide (what-does-the-bible-say-about-education.html)
    html_output = build_education_html(doc_data)
    EDU_CANONICAL_PATH.write_text(html_output, encoding="utf-8")

    # 3. Sync Book 1 Canonical SEO Guide (what-does-the-bible-say-about-god.html)
    sync_book1_god_html()

    # 4. Write All 1-Hop Alias Stubs
    stubs = [
        (BASE_DIR / "education.html", f"/foundations/{EDU_CANONICAL_SLUG}", "What Does the Bible Say About Education?"),
        (BASE_DIR / "god.html", f"/foundations/{GOD_CANONICAL_SLUG}", "What Does the Bible Say About God? (What We Know About God)"),
        (BASE_DIR / "what-we-know.html", f"/foundations/{GOD_CANONICAL_SLUG}", "What Does the Bible Say About God? (What We Know About God)"),
        (BASE_DIR / "what-we-know-about-god.html", f"/foundations/{GOD_CANONICAL_SLUG}", "What Does the Bible Say About God? (What We Know About God)"),
    ]
    for stub_path, target_url, label in stubs:
        stub_path.write_text(make_redirect_stub(target_url, label), encoding="utf-8")

    # 5. Write 1-Hop Legacy /365DBR/What_We_Know.html Redirect Stub -> /foundations/what-does-the-bible-say-about-god.html
    if REDIRECT_365DBR_PATH.parent.exists():
        REDIRECT_365DBR_PATH.write_text(
            make_redirect_stub(f"/foundations/{GOD_CANONICAL_SLUG}", "What Does the Bible Say About God? (Foundations Library)"),
            encoding="utf-8"
        )

    # 6. Write GoDaddy Apache .htaccess & 404 Case-Insensitive Router
    HTACCESS_PATH.write_text(HTACCESS_CONTENT, encoding="utf-8")
    CASE_ROUTER_PATH.write_text(CASE_ROUTER_HTML, encoding="utf-8")

    total_chapters = sum(len(p["chapters"]) for p in doc_data["parts"])
    total_labs = sum(1 for p in doc_data["parts"] for c in p["chapters"] if c.get("lab"))
    print("[FL Build Complete]")
    print(f" - JSON Data Layer : {JSON_OUT_PATH} ({len(doc_data['parts'])} Parts, {total_chapters} Chapters, {total_labs} Labs)")
    print(f" - Book 1 Canonical: {GOD_CANONICAL_PATH}")
    print(f" - Book 2 Canonical: {EDU_CANONICAL_PATH}")
    print(f" - 1-Hop Stubs     : education.html, god.html, what-we-know.html, what-we-know-about-god.html, /365DBR/What_We_Know.html")
    print(f" - GoDaddy Routing : {HTACCESS_PATH} + {CASE_ROUTER_PATH}")

if __name__ == "__main__":
    main()