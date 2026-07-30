# Verse Identity & Alignment (English-primary, original-faithful)

**Status**: Adopted 2026-07-20 (Phase 4 foundation).  
**Priority**: Truth/Accuracy > Safety > Performance.

## api.bible stance (trust and verify)

We **trust api.bible as the content source** unless we catch a concrete, reproduced error in their payload.

Observed past failures have been **ours** (wrong bibleId, wrong params, ignoring fields, ETL filters), not proven api.bible text corruption.

### Critical field we previously under-used

With `use-org-id=true` (see `fetch_readings.py`), English parallels include:

| Field | Meaning |
|--------|---------|
| `verseId` | **Modern English** edition numbering (KJV/LSV-style) |
| `verseOrgIds` | **Original-language organization** id(s) for the same content span |

Example (local pack `0228` / PSA.31, verified):

```text
KJV/LSV text node:
  verseId:      PSA.31.18          ← English numbering (user-facing)
  verseOrgIds:  [PSA.31.19]        ← WLC/org numbering for the same words
```

That is **alignment data**, not “api.bible got the verse wrong.” Hebrew MT and English Protestant Bibles often number Psalms differently (superscription counted as v.1 in Hebrew, not in English). api.bible encodes both.

**Rule**: Do not invent offset heuristics when `verseOrgIds` is present. Prefer the map the payload already provides. Verify with spot-checks; only then question the API.

## Principles (product + theology of numbering)

1. **Scripture text is Tier 1.** Hebrew/Greek wording (and Strong’s where present) must not be invented or silently dropped.
2. **Chapter/verse numbers are later, human, and not uniform** across editions. They are a filing system, not the text.
3. **User-facing primary key = modern English numbering** (KJV-compatible / LSV as shipped): what English readers mean by “Psalm 31:18.”
4. **Original words attach by content alignment** to that English verse — via `verseOrgIds` when available — not by string-equality of BCV alone.
5. **Psalm superscriptions / titles** (“A Psalm of David…”) are **title metadata**, not ideally fused into the body of v.1 forever. Prefer structured title fields; do not treat title-as-v1 numbering as “English must become Hebrew.”
6. **Do not renumber Hebrew in the DB to fake English labels.** Keep source (org) ids as provenance; display under English ids.

## Storage model

```text
verses.id                     English-primary BCV when aligned (else source BCV)
verse_translations.verse_id   English verseId from parallels
original_tokens.verse_id      English-primary after org→English map
original_tokens.source_verse_id   Org/source id before map (provenance)
verse_alignments              (english_verse_id, source_verse_id, source_system)
annotations                   annotation_type = 'superscription' | 'title' (USFM-like d/s)
```

Daily plan ranges may still be requested in **org** form for Hebrew fetches (`use-org-id=true`). `load_day` resolves plan org ranges → English display ids through `verse_alignments`.

## Titles

- Extract USFM-like paras (`style` in `d`, `s`, `s1`, `s2`, `ms`, …) into `annotations`.
- KJV often ships title as separate `style=d`; some LSV verses embed a title phrase in v.1 body. Store structured titles when present; do not strip LSV body text without a verified rule (trust the edition payload).

## Watch-list (similar issues)

| Symptom | Check first (usually us) | Then verify API |
|---------|--------------------------|-----------------|
| English/Hebrew “same” BCV, different meaning | Did ETL use `verseId` only and ignore `verseOrgIds`? | Compare payload fields side by side |
| Missing English for a day | Did we filter parallels to original-only ids? | Is the text under a different `verseId` with org map? |
| Psalm title in audio/v1 | Title appended in post-process or edition body? | Is there a separate `style=d` node? |
| Count mismatch ±1 on Psalms | Superscription / English 24 vs org 25 | Payload `verseOrgIds` chain |
| “api.bible wrong” claim | Wrong bibleId, range, `use-org-id`, parallels list | Reproduce with minimal curl + same params |

## Related code

- Fetch: `apps/365DBR/fetch_readings.py` (`use-org-id`, `include-titles`)
- Parse/ETL: `db/etl/parse_passage.py`, `db/scripts/populate_day.py`
- Query: `db/query/day_load.py`
- Schema: `db/migrations/002_verse_alignment.sql`

## Populate clear rule (cross-day safety)

When re-loading a day, **do not** delete all tokens that mention a `source_verse_id` used by that day. Adjacent days share org ids as provenance only (e.g. `GEN.31.55` ← org `GEN.32.1` on day 0117; English `GEN.32.1` ← org `GEN.32.2` on day 0118). A global `DELETE … WHERE source_verse_id = X` wipes the earlier English-primary tokens.

Safe clear: delete by this day’s **display** `verse_id`s; only remove stale rows still parked under pure org BCVs (`verse_id = org` and `source_verse_id` null or equal org). See `populate_day.py` and `audit_empty_originals.py`.

## Residual empty originals (expected small)

After the wipe fix, a handful of English BCVs may still have LSV/KJV with `tokens=0` (e.g. English split of one org verse, first-wins org→English map; or placeholder text like LSV `REV.12.18` = `-`). Dual-claim empties (tokens living under the claimed source BCV from a *different* org) should stay at **0**.

## Non-goals (this increment)

- Changing live `index.html` / `loadDailyBread` (static JSON remains primary for UI).
- Full `BIBLE_DATA` rewrite to English-only counts (plan still uses existing constants; alignment bridges display).
- Claiming api.bible errors without a minimal reproducible case.

Bible is primary. Numbering serves readers. Alignment serves truth.
