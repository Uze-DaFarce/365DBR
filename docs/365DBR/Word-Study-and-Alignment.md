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
- **Source Files:** `RAW/STEPBible-Data/Translators Amalgamated OT+NT/` (`TAHOT` for Hebrew WLC; `TAGNT` for Greek TR).
- **Why It Is Deterministic:** Scholars manually aligned every single Hebrew and Greek token row 1-to-1 with its exact contextual English translation column in that specific verse.
- **Implementation Plan:**
  1. Add `english_token_gloss TEXT` to `original_tokens` (Migration `008`).
  2. Parse the exact contextual English column from `TAHOT` / `TAGNT` matched by `(verse_id, word_order)`.
  3. Expose `english_token_gloss` in `v_interlinear_tokens` and `ws/verse/{BOOK}.json`.
  4. **UI Labeling:** Explicitly label it as *"STEPBible Contextual Token Translation"* (distinct from the general Strong's lexicon headword gloss and distinct from LSB/KJV/LSV/WEB/YLT prose).

### Path B: Explicit USX `<w s="Hxxxx|Gxxxx">` Tags (`KJV` and `WEB` Only)
- **Source Files:** `RAW/KJV` and `RAW/WEB` USX XML files wrap English words directly in `<w s="G0976">The book</w>` tags.
- **Scope Limitation:** Only `KJV` and `WEB` have word-level `<w s="...">` tags in their source files. `LSB`, `LSV`, and `YLT` do **not** have word-level Strong's markup. Therefore, exact word highlighting inside a rendered English translation may **only** be rendered on `KJV` or `WEB` using parsed `<w s="...">` spans—never guessed on `LSB`, `LSV`, or `YLT`.
