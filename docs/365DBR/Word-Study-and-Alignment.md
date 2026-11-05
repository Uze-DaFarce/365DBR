# Word Study & English-to-Original Alignment Policy
**Last Updated:** 2026-10-28

## 1. Strict Honesty & Transparency Rule (Zero Guessing)
Under our Sola Scriptura integrity standard, **we never guess or use regex heuristics** (such as stem-matching a dictionary gloss against an English verse string) to claim which English word translates a Hebrew or Greek token.
- `highlightGloss` and unverified English token labels were intentionally removed because English translations like `LSB`, `LSV`, and `YLT` do not contain word-level Strong's tags, making regex highlighting prone to false positives.

## 2. What Ships in Production Today (`static_pack_v2`)
- **OT & NT Original Tokens (`apps/365DBR/ws/verse/{BOOK}.json`):** Every verse across all 66 books includes ordered Hebrew (`WLC`) or Greek (`TR`) surface tokens with their verified Strong's number (`H####` / `G####`), lemma, and morphology.
- **Strong's Concordance Packs (`apps/365DBR/ws/strong/{STRONG}.json`):** Clicking any tagged Hebrew or Greek word displays its Strong's number, lexical root (`lex_word`), transliteration, occurrence count across Scripture, and every verse occurrence in parallel English translations.

## 3. How to Add Deterministic English Word Mapping (Stage 4 Approved Specification)
There are exactly **two honest, 100% deterministic sources** in our local `RAW/` repositories that require zero guessing:

### Path A: STEPBible Contextual Token Translation (`TAHOT` & `TAGNT`)
- **Source files:** `apps/365DBR/RAW/STEPBible/Translators Amalgamated OT+NT/` (four `TAHOT` files, two `TAGNT` files). There is no `RAW/STEPBible-Data/` directory.
- **Loaded 2026-11-04** into `stepbible_token_rows` by `apps/365DBR/load_stepbible_tokens.py` (migration `009`). The contextual English is the `english` column. `dstrong` is the tag printed on that STEPBible row.
- **Link rule:** `original_token_id` is set only when the letters match one `original_tokens` row in that verse. A 2026-11-04 audit rechecked all 348,088 links: the letters match. 1,182 of them are out of sequence, so same-occurrence is not yet proved for those. Do not export them. Rows with a parenthetical alternate verse stay unlinked. Do not join on `(verse_id, word_order)`. Do not copy these values onto `original_tokens`.
- TAHOT follows Qere and adds material. TAGNT is an amalgam, not pure TR. Hebrew candidates are text types that start with `L` or `Q`. Greek candidates are text types that contain uppercase `K`.
- **UI, when a later session exports it:** label the English *"STEPBible Contextual Token Translation"*, distinct from the Strong's lexicon headword and from LSB/KJV/LSV/WEB/YLT prose.

### Path B: Explicit USX `<w s="Hxxxx|Gxxxx">` Tags (`KJV` and `WEB` Only)
- **Source Files:** `RAW/KJV` and `RAW/WEB` USX XML files wrap English words directly in `<w s="G0976">The book</w>` tags.
- **Scope Limitation:** Only `KJV` and `WEB` have word-level `<w s="...">` tags in their source files. `LSB`, `LSV`, and `YLT` do **not** have word-level Strong's markup. Therefore, exact word highlighting inside a rendered English translation may **only** be rendered on `KJV` or `WEB` using parsed `<w s="...">` spans—never guessed on `LSB`, `LSV`, or `YLT`.
