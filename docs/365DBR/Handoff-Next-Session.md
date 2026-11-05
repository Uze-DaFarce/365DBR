Check-in and production, 2026-11-04. The owner is committing. Do not FTP unless asked.

`apps/365DBR/ws/manifest.json`, `ws/verse/`, and `ws/strong/` are gitignored. A commit does not contain the new STEPBible English. That English is only in the local `ws/` folder and the local database.

Production is GoDaddy `/public_html/365DBR/`. The public site never has a database. Security requires the cache to be written on this machine, then moved. Speed is a side effect.

- `index.html` and `bible.html` can go up first. `step_english` is optional, so these pages still work with the word-study pack already online. The new English appears after `ws/` is replaced.
- Replace the whole `ws/` folder for the new English: 409,219 tokens with `step_english`. Either order is safe. Put `ws/` beside the HTML files (`https://mt-sin.ai/365DBR/ws/manifest.json`).
- `strongs_optional.js` was not changed. Day packs in `data/` were not changed. Leave both unless a diff says otherwise.
- Do not upload `RAW/`, Python, `db/`, or Docker.

UI in those two HTML files: the selected word is one line with pipes; a flattened poetry line keeps a space between lines; changing the verse updates word study; a hit click moves the page and leaves the study on the same word; slot 1 marks that original word in amber. The pages were not clicked in a browser.

Data already in the local database and in local `ws/`: a whole verse of letters links in order even when the verse numbers differ. One cross-number link, STEPBible PSA.18.50 onto the tokens at 2SA.22.51. A samekh or pe after the sof pasuq is a section mark and is ignored. 1 Chronicles 12:8–10 carry their STEPBible English. No original word was moved.

Status as of 2026-10-28. Do not re-research this. The block above is the newer status.

Verse text
- KJV (translation_id 2) and LSV (translation_id 1) are local eBible. All 31,102 verses each. SHA-256 on every row. No KJV or LSV source_note cites api.bible. The 30-day api.bible duty does not apply to these rows.
- KJV zip: apps/365DBR/RAW/KJV/eBible/eng-kjv2006_usfm.zip sha256 BF907642B9A37530EBD9CEDF08273F62A7C2140E414205FD4B8208BE952B4B14. License: public domain outside the UK. UK print or import needs the Queen's Printers (Cambridge, Oxford, Collins). source_bible_id ebible:eng-kjv2006.
- LSV zip: apps/365DBR/RAW/LSV/eBible/englsv_usfm.zip sha256 8EA9837F3FD6B4281CC9F0D0FF27DA51A44FDF8379FCA88733D7A7BCE4BC15AD. License: CC BY-SA 4.0, Covenant Press / Covenant Christian Coalition, 2020. source_bible_id ebible:englsv. Every LSV strong attribute was dropped. The numbers do not sit on the matching words. Dash-only lines 3JN.1.15 and REV.12.18 were not merged.
- LSB, WEB, and YLT were not rewritten. original_tokens was not rewritten.
- Loader: apps/365DBR/load_ebible_kjv_lsv.py. Provenance: apps/365DBR/RAW/KJV/eBible/PROVENANCE.txt and the LSV PROVENANCE.txt beside it.

Thirteen KJV compounds
- A space between two \w tags was removed only where this same file spells the compound as one word: cannot, wherein, whereunto, whatsoever.
- Verses: ACT.4.16, ACT.4.20, ACT.5.39, COL.3.17, COL.3.23, 1TI.2.7, 1TI.5.25, 1TI.6.12, 2TI.1.11, 2TI.2.9, 2TI.2.13, HEB.6.17, HEB.9.5.
- Hebrews 9:5 "can" is G2076. The other "cannot" rows are G1410 + G3756.
- Acts 5:39 reads "cannot" and still has two tag rows: can/G1410 and not/G3756.
- 2 Timothy 2:9 reads "Wherein" and "evil doer". "evil" is untagged. "doer" is G2557. Leave those as two words.

KJV English Strong's tags
- Migration 008_kjv_english_strong_tags is applied. schema_migrations has that version.
- Table kjv_english_strong_tags: 348,884 rows, edition eng-kjv2006.
- word_order counts \w and \+w spans, not every English word.
- These are KJV English-word tags from that file. They are not a WLC or TR alignment and they are not certified. They must not be copied onto original_tokens.
- 2 Thessalonians 3:18: grace G5485, our G2257, Lord G2962, Jesus G2424, Christ G5547, with G3326, you G5216, all G3956, Amen G0281. "be" is \add and has no row.
- apply_migrations.py failed: DATABASE_URL does not parse (host was read as eRSs@localhost). 008 was applied with docker exec psql. The loader connects through db/.env and works.

Not done
- Public day packs were not re-exported. https://mt-sin.ai/365DBR/ still serves the previous JSON.
- stage1_ingest_lsb_web_ylt.py, stage1_part2_execute.py, and stage3_export_and_ui.py were deleted on 2026-11-04 at the owner's request. Do not restore them. fetch_readings.py and fetch_omissions_cache.py are in apps/365DBR/reference/retired-api-bible/ and must not be run. They call api.bible and can overwrite day JSON.
- Do not run publish_365dbr.ps1 -Init unless asked, and only after the new HTML/JS are known to be on the server.

Still true, and still broken
- Greek original_tokens.strong_number is not certified. The deleted stage1_part2_execute.py had filled gaps with a match window, a prefix test, most_common, and TR_EXACT_OVERRIDES. There is no strong_norm column. Proof: 2TH.3.18 ἡμῶν is stored as G3165; the lexicon entry for G3165 is μέ ("me"). The KJV English tag for "our" is G2257. The STEPBible English on that token is "of us". Those are different facts. G2424G is on 977 Greek tokens and is absent from strongs_lexicon. v_interlinear_tokens uses left(strong_number, 5). 533 Greek rows are compounds such as G0846+G2532. Hebrew strong_number was not overwritten by that script. The suffix restore did not write any Strong's number.
- Do not start a fuzzy or majority Strong's rebuild. A number printed on that word in a named file is a source tag. A matcher, a vote, or a shifted overlay is a guess and must not be stored as Strong's.
- Stage 4 Path A is loaded (2026-11-04). Table stepbible_token_rows: 305,648 TAHOT + 141,746 TAGNT = 447,394 word rows. Migration 009. Loader apps/365DBR/load_stepbible_tokens.py. Audit apps/365DBR/audit_token_sources.py.
- Referees on disk: Hebrew is apps/365DBR/RAW/OSHB/wlc (WLC 4.20, the file TAHOT names as its base). Greek is apps/365DBR/RAW/GRCTR USX running text. Footnotes stay out of the verse body. Style d is a colophon. HEB_WLC is the same Leningrad text in another file, not a second manuscript. There is no Aleppo file here. Do not treat a different edition's disagreement as corruption.
- Link check, 2026-11-04: all 348,088 original_token_id values match the token's letters and verse. 0 failures. 319 tokens carry two STEPBible rows, and those rows agree on the letters. 1,182 links are out of sequence. A later לך can point at the only earlier לך token. Letter identity is checked. Same-occurrence is not, for those 1,182. Do not show them as alignments until they are classified.
- OSHB vs original_tokens on the same verse id: 16,923 of 23,012 verses are consonant-exact. 6,072 OSHB words are absent from that token verse. 5,162 of those are still in stepbible_token_rows, unlinked. Song of Solomon 8:14 is the pattern: OSHB and TAHOT both have לְ/ךָ, and original_tokens does not. The unlinked row was kept. 1 Chronicles 12 shows a verse-number offset (OSHB 12:10 is the token text of 12:9), so a raw "replaced word" count is not letter corruption. 1,833 TAHOT L rows differ from OSHB by a trailing section-mark samekh.
- GRCTR verse body vs Greek tokens: 7,474 of 7,856 verses exact. 2 Thessalonians 3:18 colophon is Πρὸς Θεσσαλονικεῖς δευτέρα ἐγράφη ἀπὸ Ἀθηνῶν, and the six unlinked TAGNT K rows are that colophon. TAGNT also preserves real edition variants (for example ἑλλησι / ἔθνεσιν) and movable nu. Keep both labeled.
- Suffix restore 2026-11-04 (`restore_oshb_suffixes.py`, reader `oshb_wlc.py`). 5,260 OSHB suffix pronouns inserted into 4,236 verses. New rows have strong_number NULL, lemma NULL, morph from the OSHB `<w>`, and extra.source `oshb-wlc-4.20`. Hebrew tokens 299,420 to 304,680. Greek stayed 140,111. Song 8:14 consonants match OSHB, including לְ/ךָ with no Strong's number. 1 Chronicles 12 was not changed. The 1,144 neighbor-verse offsets (1,004 at verse-1, 140 at verse+1) were not touched. Letter link after the insert: 352,337 linked, 9,321 no letter match, 57,970 ambiguous. Shared-token English agrees on 139 and disagrees on 169. Disagreeing tokens were left unlabeled.
- Local `ws/` export 2026-11-04 (`db/scripts/export_word_study_static.py`). 66 books, 444,791 tokens, 351,824 with `step_english`. The key is omitted unless every linked STEPBible row on that token has the same English. Label: STEPBible contextual English. highlightGloss was not written. Not uploaded. `get_connection()` reads `db/.env` first because the container env password is rejected. Do not FTP unless asked.
- Text match 2026-11-04 (`load_stepbible_tokens.py --link-only`). Verse numbers are an index. A whole verse whose letters match in order is linked even when `heb_ref` is set and even when the token verse number differs. One such cross-number link: STEPBible PSA.18.50 (מגדיל, "making great") to tokens at 2SA.22.51. Tokens at PSA.18.50 read מגדל and stayed unlinked to that gloss. ס or פ after sof pasuq is a section mark and is ignored. 1CH.12.8–10 now carry their STEPBible English, including Ezer, the/ chief, Obadiah, the/ second, Eliab, the/ third. Single-word rows that still have `heb_ref` and do not sit in a full-verse match stay unlinked. No original_tokens row was moved. Greek colophon words at 2TH.3.18 stay unlinked. Do not treat a cross-number full-verse link as corruption. Local `ws/` was exported again after that link: 409,219 tokens with `step_english`. Not uploaded.
- highlightGloss is gone and must stay gone. Gloss is not the English of a WLC/TR occurrence. Word Study hit text follows the Focal slot only. Compare text is slot 2 only.
- Aa is on for Hebrew and Greek in the UI. Greek numbers are still not certified.
- Test verses are never Genesis 1:1 or Matthew 1:1.
- finish_all.py and patch_export.py are deleted.
- Verse table has 31,305 rows. Protestant English is the 31,102 translation rows. REV.12.18 still exists with 0 translations and 0 tokens. LUK.17.37, ACT.15.41, and ACT.24.27 have English and zero Greek tokens.
- translations ids: 1 LSV, 2 KJV, 5 LSB, 6 WEB, 7 YLT. No ids 3 or 4.
- bible_common.py PARALLEL_IDS and db/etl/parse_passage.py still name the old api.bible ids. Do not rewrite applied migration 001.
- verify_schema.py expects the eBible ids, inserts GEN.1.1, and does not know about kjv_english_strong_tags. Do not run it.
- verify_bookmark_word_study.py still expects no NT Aa and uses Matthew 1:1.
- 365dbr_dev is a superuser. Roles were not split.
- "Immutable" means a loaded file hash plus verse hash stays frozen. A correction is a new snapshot. KJV and LSV cells are allowed to change when the local file proves the change.
# 365DBR & S.I. (Scriptural Intelligence) — Master Agent & Grok Build Briefing
**Last Updated:** 2026-10-28 (Stages 1–3 Complete & Live in Production)

## 1. CRITICAL ARCHITECTURAL REALITY (READ FIRST)
- **GoDaddy Hosting is NOT a Blocker:** Do NOT assume we must migrate off GoDaddy to proceed with the database or Scriptural Intelligence (S.I.).
- **Local Master DB + Pre-Computed Static Export ($0 Runtime):**
  - Our authoritative Tier-1 S.I. relational database (`mt_sinai_365dbr` in local Docker PostgreSQL) is 100% operational on the developer workstation.
  - Production `365DBR` on GoDaddy runs entirely from deterministic, pre-computed static JSON packs (`apps/365DBR/data/<MMDD>/canonical_map.json` and `apps/365DBR/ws/{verse,strong}/*.json`) compiled directly from the local Postgres database and USX ASTs.
  - Meanwhile, the S.I. Tier-1 Database, Tier-2 API (`db/query/`), and Tier-3 Immutable Logic Engine are developed and verified locally against Docker Postgres with zero cloud hosting dependency.

## 2. NON-NEGOTIABLE SOLA SCRIPTURA & INTEGRITY RULES
1. **Textual Authority:** Original Hebrew WLC (`OSHB`) and Greek Textus Receptus (`TR` / `GRCTR`), alongside `LSB`, `LSV`, `KJV`, `WEB`, and `YLT`.
2. **Zero Guessing / Zero Heuristic Alignment:** Never use regex stem-matching (e.g., `highlightGloss`) or approximate word guessing to highlight or map English words to Hebrew/Greek tokens. Every mapping must be 100% deterministic, traceable to a primary source column/tag, and transparently labeled.
3. **Zero Artificial Verse Padding:** Exactly `31,102` canonical verses. Never insert placeholder text for versification differences.

## 3. COMPLETED STATE THROUGH STAGE 3 (LIVE IN PROD)
- **Stage 1 (Canonical Spine, 5 Translations, Original Tokens):**
  - `verses`: `31,102` canonical rows (`LUK.17.37`, `ACT.15.41`, `ACT.24.27` restored; bogus `REV.12.18` removed).
  - `verse_translations`: `155,510` rows (`LSB`, `LSV`, `KJV`, `WEB`, `YLT` x `31,102`) with enforced `text_sha256`.
  - `original_tokens`: `439,531` rows (`299,420` Hebrew WLC + `140,111` Greek TR) with 100% normalized Strong's (`strong_norm`).
  - `verse_alignments` (`31,102` rows) & `data_sources` (`7` authoritative provenance records).
- **Stage 2 (Strong's Lexicon & Production SQL Views):**
  - `strongs_lexicon`: `22,716` entries (`11,681` Hebrew `TBESH` + `11,035` Greek `TBESG`), 100% token join coverage.
  - Views: `v_interlinear_tokens` and `v_daily_reading_verses` tracked through migration `007_stage2_interlinear_and_reading_views.sql`.
- **Stage 3 (Static Export Pipeline & 3-Slot UI in `index.html` and `bible.html`):**
  - All 365 `apps/365DBR/data/<MMDD>/canonical_map.json` files contain `HEB` (original WLC/TR), `LSB`, `KJV`, `LSV`, `WEB`, and `YLT`.
  - Static Word Study packs (`apps/365DBR/ws/verse/*.json` for all 66 books and `apps/365DBR/ws/strong/*.json` for OT + NT Strong's numbers) are exported and deployed.
  - Both `index.html` and `bible.html` feature 3-slot parallel reading (Slot 1 Original Hebrew/Greek, Slot 2 Compare dropdown, Slot 3 Focal dropdown) working across both mobile (narrow) and desktop (wide) views, plus OT & NT Strong's Word Study.

## 4. CURRENT WORKFLOW 
- **DB-Backed Compilation:** Never overwrite `canonical_map.json` using the legacy 2-translation `compile_site.py` pipeline alone. The database exporter is `apps/365DBR/stage3_export_and_ui.py`. `finish_all.py` and `patch_export.py` were one-shot scripts and have been deleted. They reinserted `highlightGloss`.
-  KJV and LSV verse text are local eBible as of 2026-10-28. No row cites api.bible. WEB, YLT, LSB, and WLC were already local. Do not refresh those verses on a 30-day cycle.

## 5. NEXT UP: STAGE 4 & S.I. TRANSITION ROADMAP
1. **Deterministic Token-to-English Alignment (Stage 4 Path A):** Loaded 2026-11-04 into `stepbible_token_rows` from `apps/365DBR/RAW/STEPBible/Translators Amalgamated OT+NT/`. See the status block at the top of this file. Do not write those values onto `original_tokens`. KJV English `<w>` tags already sit in `kjv_english_strong_tags` and are not a WLC/TR alignment.
2. **Monthly `api.bible` DB Sync Script:** Automate checking `api.bible` monthly into `verse_translations` + regenerating static daypacks only when SHA-256 hashes change.
3. **S.I. Tier-2 & Tier-3 Logic Engine:** Build deterministic cross-reference, lexical concordances, and Sola Scriptura verification queries on top of `mt_sinai_365dbr`.
