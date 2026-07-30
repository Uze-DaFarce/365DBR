# 365DBR DEV Logs

This file records implementation work, decisions, verification results, and open questions from the 365DBR-DEV role.

## 2026-07-01 — Phase 1 Kickoff: Postgres Infra + v0.1 Schema Bootstrap

**Session context**:
- Read all mandated documents in order (INDEX.md, Project Blueprint, Data-Sources.md, 365DBR_AGENTS.md, Database-Schema.md, Migration-Plan.md, this role file).
- Git status checked (minor unrelated untracked file in HeIsRisen; 365DBR tree clean for edits).
- Current overriding priority: 100% on accurate 365DBR DB foundation. Production data rule respected (no real data used yet).
- User directive: Truth/Accuracy > Safety/Security > Performance. "We must do this right, or not do it at all."

**Actions completed**:
- Created canonical local dev setup (chosen as BEST for reproducibility and fidelity):
  - `docker-compose.yml` (root) — `postgres:16` with named volume, healthcheck, UTF8/C locale.
  - `db/` structure:
    - `requirements.txt` (psycopg[binary] + python-dotenv)
    - `.env.example`
    - `migrations/001_initial_schema.sql` — **exact** DDL + indexes + trigram extension + translations seed from Database-Schema.md v0.1. Includes `schema_migrations` table and heavy referencing comments.
    - `scripts/apply_migrations.py` — minimal, auditable plain-SQL applier with idempotency.
    - `scripts/seed_books.py` — **idempotent**, imports directly from `apps/365DBR/bible_common.py` (BIBLE_DATA + BOOK_NAMES) as single source of truth for 66 books, order_canonical, num_chapters, testament. Uses UPSERT.
    - `scripts/verify_schema.py` — strict smoke tests:
      - 66 books count
      - Full spot-checks of names, chapters, testament vs bible_common
      - Translations (LSV primary + correct bibleId, KJV)
      - All core tables present
      - Manual sample verse INSERT + SELECT for Hebrew (GEN.1.1) and Greek (JHN.1.1) patterns, with cleanup
      - Explicit Hebrew vs Greek awareness section
- Comprehensive `db/README.md` written with:
  - Step-by-step for Windows/PowerShell + Docker Desktop (recommended)
  - Native Postgres alternative
  - Reset procedures
  - Connection details
  - Rationale for choices (auditability, single source of truth for books, etc.)
- No changes to existing 365DBR pipeline, frontend, or tests.
- No ETL / population / daily data yet (strictly scoped to Phase 1).

**Verification approach**:
- All scripts are explicit and hard-failing on mismatch.
- Books seeding derives from the exact same constants used by the reading plan and validation logic.
- Schema is a faithful 1:1 implementation (plus minimal operational tables like schema_migrations).

**Current status vs INDEX.md TODO**:
- [x] Phase 1 handoff executed (infra + schema + seeds + basic validation).
- Local repeatable dev setup created.
- Verification scripts exist and enforce the required checks (66 books, translations, Hebrew/Greek samples).
- Documentation added (db/README.md + this log + setup files are self-documenting).

**How to run (summary for new session)**:
See the full guide in `db/README.md`.

Typical flow once Docker is available:
```powershell
docker compose up -d
cd db
pip install -r requirements.txt
python scripts/apply_migrations.py
python scripts/seed_books.py
python scripts/verify_schema.py
```

**Blockers / open items** (updated after live verify):
- Docker Desktop installed and running; Phase 1 verify **PASSED** (see entry below).
- No real production data population yet (Phase 2).
- No changes to existing Python pipeline or `apps/365DBR/tests/`.
- Optional Phase 1.1: explicit `verse_source_status` for KNOWN_OMISSIONS / misalignment (discussed; not required for Phase 1 success).

**Notes on decisions made for "doing it right"**:
- Chose plain numbered SQL + minimal Python applier over Alembic for Phase 1 (maximum auditability and simplicity).
- Books seed is Python-driven (not static SQL) to eliminate any possibility of drift from `bible_common.py`.
- Strong emphasis on verification that actually exercises the constants used by the rest of the system.
- Docker chosen as primary because it guarantees the exact Postgres version and configuration the schema was designed against.
- All connection logic supports both Docker and native installs.
- `.env` pattern documented clearly; secrets never committed.

---

## 2026-07-02 (session cont.) / live run — Phase 1 Verification PASSED

**User-run output (excerpt)**:
```
======================================================================
VERIFICATION SUMMARY
  Books in DB          : 66
  Expected             : 66
  Translations         : LSV (primary), KJV
  Sample inserts       : Hebrew + Greek OK (rolled back)
  All structural checks: PASSED
======================================================================
```

**Confirmed**:
- Local Postgres 16 via Docker Compose is up.
- Schema v0.1 applied; books seed accurate (66); LSV primary + KJV present.
- Sample Hebrew (GEN.1.1) and Greek (JHN.1.1) insert/query patterns OK.
- Minor bug in verify summary (`double fetchone`) fixed earlier in session; re-run clean.

**Phase 1 success criteria (from role)**: MET for infra + schema + seeds + smoke validation.  
**Not in scope / still open**: Phase 2 sample population from prod (e.g. 0701), omissions ETL table (optional), frontend, full 365.

**Bible is primary. All artifacts serve faithful representation of the text.**

---

## 2026-07-13 — Phase 2 kickoff: sample day ETL (local GRCTR/WLC)

**Context**: Phase 1 complete. NT original switched to GRCTR; local day packs refreshed. User has API credits remaining; began Phase 2 population.

**Implemented**:
- `db/etl/parse_passage.py` — Hebrew Strong's word walk; Greek verse surface → tokens; KJV/LSV parallel text
- `db/scripts/populate_day.py` — transactional day load; `--source local|prod|auto`; integrity via `bible_common.validate_content_integrity` before insert
- `db/scripts/verify_population.py` — verse counts, token counts, LSV/KJV sample text match, Hebrew/Greek reconstruct checks

**Verified days (source=local, all PASS)**:
| Day | Verses | Tokens | Notes |
|-----|--------|--------|--------|
| 0123 | 86 | 1234 | GEN + MAT (GRCTR) + PSA + PRO |
| 0702 | 84 | 1265 | 2KI + ACT (GRCTR) + PSA + PRO |
| 0823 | 87 | 1440 | EST + ROM.14.1–23 (TR fix) + PSA + PRO |

**Source policy**: Prefer **local** verified fetches (GRCTR + WLC). Production URL optional until FTP catches up. `omissions_cache` not used in ETL.

**PowerShell note**: Quote day ids (`--day "0702"`) so leading zeros are not stripped.

**Next**: more days / full 365 when ready; Phase 3 broader reconciliation.

---

## 2026-07-14 — Phase 3 kickoff: verify_db.py + TR count fixes

**Implemented**: `db/scripts/verify_db.py` — full reconciliation:
1. Seeds (66 books, LSV/KJV)
2. Book-level ids vs `BIBLE_DATA` (missing/extra)
3. Daily plan 365 × 4
4. Translation coverage
5. Hebrew Strong's 100%; Greek tokens present
6. TR samples (MAT.17.21, JHN.5.4, ACT.8.37, ROM.16.24–27; no ROM.14.24–26)
7. Day load perf baseline (~194ms for 0101 LSV)
8. S.I. smokes (H430, GEN.1.1, JHN.1.1)
9. Local JSON LSV spot-check

**Findings fixed/in progress**:
- `BIBLE_DATA` ACT ch8 **39→40** (TR includes 8:37; ACT.8.40 is real end of chapter)
- Plan gap: **EXO.6.30** skipped (0131 ended at 6:29). `readings.json` fixed to `EXO.4.30-EXO.6.30`; needs **re-fetch 0131** + `populate_day --day 0131` for full canonical coverage
- Re-ran `export_bible_meta.py` after ACT fix

**Status**: Phase 3 tool green on almost everything; sign-off blocked only on EXO.6.30 until 0131 refresh.

---

## 2026-07-16 — Phase 3 PASS + Phase 4 Option A (DB query layer)

**Context**: User session as 365DBR-DEV. Phase 1–2 already done; Phase 3 reconcile was previously blocked on EXO.6.30. Current DB snapshot fully reconciles.

**Phase 3 verification (this session)**:
```
python db/scripts/verify_db.py
→ PASSED: 56  FAILED: 0  WARNINGS: 0
→ OVERALL: PASS
```
- verses=31167 (full BIBLE_DATA coverage)
- LSV=KJV=30785; ACT ch8=40 TR; ROM 14=23 / 16=27
- Hebrew Strong's 100%; Greek tokens present (GRCTR)
- JSON↔DB LSV spot 0101/0702/1225 mismatches=0
- Day 0101 LSV load ~55ms

**Phase 4 deliverable (Option A — low risk)**: Optional DB-backed query capability **without** changing live reader.

| Artifact | Role |
|----------|------|
| `db/query/connection.py` | Shared `DATABASE_URL` / `.env` connection |
| `db/query/day_load.py` | `load_day`, `load_verse`, `search_strong`, `dual_read_day` |
| `db/scripts/query_db.py` | CLI: `day` / `verse` / `strong` / `dual-read` |
| `db/scripts/test_query_phase4.py` | Smoke tests against live local DB + local packs |

**verseMap contract (for future Option B readiness)**:
- Keys: BCV strings; translation keys lowercase (`lsv`, `kjv`) + `original`
- English `text` is a **flattened string** (not array) — matches `loadDailyBread` post-flatten
- `original.tokens[]` carries Strong's for Hebrew; Greek surface words (strong often null)
- **No changes** to `index.html` / `bible.html` / `playVerse` this increment

**Verified**:
```
python db/scripts/test_query_phase4.py   # ALL PASS
python db/scripts/query_db.py dual-read --day "0101,0702,1225" --source local
→ DUAL-READ OVERALL: PASS (210+168+170 English cells checked, 0 mismatches)
python db/scripts/query_db.py strong --num H430 --limit 5 --compact
→ 2245 verses (Elohim)
```

**Docs updated**: `docs/INDEX.md` TODO, `db/README.md` Phase 4 section, this log.

**Not done / next Phase 4 increments**:
- No browser UI Strong's tooltip yet
- No HTTP API (CLI + library only)
- Option B (DB as `loadDailyBread` source) deferred until needed + AGENTS audio verify
- No LSB

**Git note**: Working tree already had Phase 3 artifacts unstaged (`verify_db.py`, bible_meta, readings.json, etc.). New files under `db/query/` + scripts.

**Bible is primary. Static JSON remains primary for daily UX. DB is optional capability + truth diagnostic.**

---

## 2026-07-16 (cont.) — Phase 4.2 local query HTTP API

**Context**: Phase 4.1 CLI checked in as `1b39639`. Continue Option A with thin local read-only HTTP surface; no frontend / `loadDailyBread` changes.

**Deliverable**:
| Artifact | Role |
|----------|------|
| `db/scripts/serve_query_api.py` | stdlib `ThreadingHTTPServer`; default `127.0.0.1:8765` |
| `db/scripts/test_query_api_phase4.py` | In-process server + real DB endpoint smoke |

**Endpoints** (JSON, CORS `*` for local UI experiments only):
- `GET /health`
- `GET /verse/{BCV}` — translations + original tokens / Strong's
- `GET /strong/{num}?limit=N`
- `GET /day/{MMDD}?compact=1` — verseMap-compatible (flattened string `text`)
- `GET /dual-read/{MMDD}?source=local|prod` — 200 match / 409 mismatch

**Constraints respected**:
- Static JSON still primary for live reader
- No edits to `index.html` / `bible.html` / audio path
- Fail-fast: DB connect check at startup; bad Strong's → 400; unknown path → 404

**Verified**:
```
python db/scripts/test_query_api_phase4.py  # ALL PASS (13 checks)
python db/scripts/test_query_phase4.py      # ALL PASS (regression)
```

**Docs**: INDEX TODO 4.2 checked; `db/README.md` Phase 4.2 section; Migration-Plan progress.

**Next**: optional browser Strong's panel that feature-detects `http://127.0.0.1:8765` (or future hosted API) without making DB required for daily reading. Option B still deferred.

**Bible is primary.**

---

## 2026-07-16 (cont.) — dual-read 0228 diagnosis + clearer API report

**User hit**: `http://127.0.0.1:8765/dual-read/0228?compact=1` → incomplete-looking `{` (actually HTTP **409** body; dual-read failed).

**Root cause (truth / data, not server crash)**:
- Plan day 0228 PSA = `PSA.31.19–31.25` (Hebrew WLC / BIBLE_DATA = **25** verses in ch. 31).
- Local pack English (LSV/KJV) for that file is labeled **`PSA.31.18–31.24`** (English 24-verse numbering / superscription drift).
- ETL `populate_day.py` only stores English when `verseId ∈ original verse_ids` for that day → drops spillover `PSA.31.18` English and never stores English for plan `PSA.31.25`.
- DB: `PSA.31.18` and `PSA.31.25` have **original tokens** but **no LSV/KJV** rows. Same pattern likely at other Psalm superscription boundaries (e.g. `PSA.31.11` also empty English).

**Fixes this session**:
- `dual_read_day`: classify **plan** vs **spillover**; global lookup for spillover; report `plan_missing_english`.
- API: dual-read always **HTTP 200** with `ok: true|false` (full JSON in browser); honor `?compact=1`.

**Restart required** for running `serve_query_api.py` to pick up code.

**Open (next increment)**: Psalm Hebrew↔English verse alignment in ETL (do not silently drop English; document superscription mapping). Not fixed by dual-read reporting alone.

---

## 2026-07-20 — Fix dual-read 0228 / PSA.31.18 missing English

**User report**: dual-read 0228 `ok:false` with `PSA.31.18` LSV+KJV `missing_in_db`.

**Cause**:
1. Day plan PSA is `31:19–25` (Hebrew/WLC; ch. 31 has **25** verses).
2. api.bible English parallels for that file are labeled `31:18–24` (English **24**-verse chapter / superscription drift).
3. ETL skipped any parallel `verseId` not in the original-language verse set → **dropped real LSV/KJV text** for `PSA.31.18`.

**Fix**:
- `populate_day.py`: store English for every **canonical** BCV (`verse_order_map`); log spillover cells.
- Re-populated `0225–0228` from local packs.
- `dual_read_day`: plan vs spillover classification; hard-fail only when JSON English is missing/mismatched in DB; plan-missing-English is informational.
- `query_db.py` dual-read CLI updated for new report keys.

**Verified**:
```
python db/scripts/query_db.py dual-read --day "0228" --source local  → PASS (160 cells)
PSA.31.18 now has LSV + KJV in DB
verify_population 0228 PASS
```

**Note (still open)**: Full-corpus re-populate still needed for days not yet re-run with alignment.

**Bible is primary.**

---

## 2026-07-20 — English-primary alignment via api.bible `verseOrgIds` (not API blame)

**User correction**: Do not attribute versification differences to api.bible errors without proof. Past issues have been ours (params, filters, ignoring fields). Trust and verify.

**Root cause of PSA.31 dual-read / “mismatch”** (ours):
- Fetch already uses `use-org-id=true`.
- English parallels carry `verseId` (modern English) + `verseOrgIds` (original/org for same content).
- ETL stored Hebrew under org ids and English under English ids, **ignored `verseOrgIds`**, and sometimes dropped English cells.

**Verified from local pack** (api.bible payload is coherent):
```text
PSA.31 English: verseId PSA.31.18, verseOrgIds [PSA.31.19]
→ same content; two numbering systems, not corruption.
```

**Implemented**:
- `docs/365DBR/Verse-Identity-and-Alignment.md` — principles + watch-list
- `db/migrations/002_verse_alignment.sql` — `verse_alignments`, `original_tokens.source_verse_id`
- `db/etl/parse_passage.py` — org→English map from `verseOrgIds`; titles from style `d`/`s`; English-primary tokens
- `populate_day.py` — alignments + title annotations; English storage keys
- `load_day` — plan org range → English display set via `verse_alignments`

**Verified after re-populate 0101,0126,0212,0227,0228**:
```text
dual-read 0228/0101/0126/0212 → PASS
PSA.31.18 original Hebrew now “mute lying lips…” matching English (was wrongly “let me not be ashamed” under bare BCV equality)
PSA.18.2→PSA.18.1 map; superscription annotation on PSA.18 / PSA.23
```

**Follow-up**: `populate_day.py --all --source local` to realign full 365; optional live UI later (static JSON still primary).

**Bible is primary. Numbering serves readers. Alignment from the payload, not invented offsets.**

---

## 2026-07-27 — FK fix for English-only BCVs + real-world stress tests

**User report**: `--all` populate 327 OK / **38 failed** with  
`original_tokens_verse_id_fkey` on keys like `GEN.31.55`, `EXO.8.29`, `MAL.4.*` pattern edges.

**Cause (ours, not api.bible)**: English-primary remap correctly produced Protestant BCVs that are **outside** Hebrew-oriented `BIBLE_DATA` chapter lengths (e.g. GEN.31 max 54 in inventory). Populate only `ensure_verse`’d ids **in** the map → no `verses` row → FK on token insert.

**Fixes**:
1. `populate_day.ensure_verse` for **all** display/source ids (not only BIBLE_DATA keys).
2. Do **not** overwrite `verse_order` on conflict (had clobbered `REV.22.1` = `REV.21.27` order → broken ranges).
3. `load_day`: per-source alignment resolve (map if present else keep plan BCV) — never replace whole day with partial map subset.
4. `repair_verse_order.py` — re-apply canonical order from `BIBLE_DATA`.
5. **`test_query_stress_phase4.py`**: month-ends, leap-ish days, English edges, offset alignments, 60-day dual-read sample, complex plans — **not** only 0101/GEN.1.1/JHN.1.1. Smoke suite retargeted to non-toy days.

**Verified**:
```
populate --all: 365 OK / 0 failed
stress: PASS (60/60 dual-read, ~10k cells; load_day 1231=71; GEN.31.55 present)
dual-read 1231,0117,0222,0319,0819 PASS
```

**Bible is primary.**

---

## 2026-07-27 — Empty-original English edge audit + cross-day token wipe fix

**Increment**: Option B from handoff (Truth/Accuracy) — tighten English BCVs with LSV/KJV but `tokens=0`.

**Audit** (`db/scripts/audit_empty_originals.py`):
| Class | Before fix | After fix + full re-populate |
|-------|------------|------------------------------|
| English + text, tokens=0 | **181** | **4** |
| dual-claim (tokens under source BCV from *other* org) | **143** | **0** |
| orphan_align (align source has no tokens) | 34 | 0 |
| residual (splits / placeholder) | — | 4 |

**Root cause (ours, not api.bible)**: `populate_day.py` cleared tokens with  
`DELETE FROM original_tokens WHERE source_verse_id = %s` for every id in the day.  
Adjacent plan days share org ids as *provenance* (e.g. day **0117** stores `GEN.31.55` tokens with `source_verse_id=GEN.32.1`; day **0118** owns English `GEN.32.1` from org `GEN.32.2`). The later day wiped the earlier English-primary tokens.

**Fix**: Clear only (1) tokens for this day’s English display `verse_id`s, and (2) stale unmapped rows still parked under pure org BCVs (`verse_id = src AND source_verse_id IS NULL OR = src`). Never global-delete by `source_verse_id` alone.

**Residual 4 (not dual-claim wipe — leave unless separate design)**:
- `REV.12.18` — LSV text `'-'` (placeholder / omission); self-align empty
- `PSA.13.6`, `ISA.64.2`, `NEH.7.69` — English text with no inbound `verseOrgIds` map (org id claimed by previous English verse; English split / first-wins 1:1 map)

**Verified**:
```
populate --all: 365 OK / 0 failed
audit_empty_originals: fixable=0 residual=4
GEN.31.55 tokens=12 after 0117 then 0118
stress (+ section I dual-claim): PASS
dual-read 0228,1231,0117: PASS
```

**Artifacts**: `audit_empty_originals.py`; stress section I; `populate_day.py` clear logic.

**Bible is primary.**

---

## 2026-07-27 — Phase 4 optional Strong's UI (feature-detect API)

**Increment**: Option A from handoff — browser Strong's without making DB required for daily reading.

**Deliverable**:
| Artifact | Role |
|----------|------|
| `apps/365DBR/strongs_optional.js` | Probe `/health`, `fetchVerseDetail`, `fetchStrongHits`; base via `?queryApi=` or `localStorage 365dbr_query_api` (default `http://127.0.0.1:8765`) |
| `index.html` / `bible.html` | H# button on focal slot (only if probe succeeds); bottom panel tokens + click Strong's → hit list |

**Constraints respected (AGENTS)**:
- `loadDailyBread` / `verseMap` flatten / `playVerse` **untouched**
- Static JSON remains primary; panel is enrichment only
- Panel closes when audio starts; Escape closes; no UI if API absent (prod-safe)

**How to try**:
```
python db/scripts/serve_query_api.py
# serve apps/365DBR over http, open index.html or bible.html
# active verse → H# → tokens; click H#### for corpus hits
```

**Verified**: API `/health`, `/verse/GEN.1.1` (tokens + Strong's), `/strong/H430` smoke OK. Code review: playVerse/loadDailyBread markers intact.

**Fix (same day)**: esm.sh/run cannot resolve `import … from './strongs_optional.js'` (rewrites to `script-0.tsx/strongs_optional.js`). Switched to classic `<script src="strongs_optional.js">` + `window.__DBR_STRONGs__` (same pattern as `bible_meta.js`).

**UX pass (same day)**: End-user word study — human refs (`2 Kings 10:17`), no API/org/token jargon, flowing RTL original line, hover highlight + click search; results strip only after a word is chosen. Button **Aa** “Word study”.

**Product park (same day, later reversed)**: Had considered opt-in only; owner kept Word study **on** (API feature-detect) as correct and helpful. English-hover remains a **future free/open-data** goal — see `Word-Study-and-Alignment.md` (no paid reverse-interlinear budget).

---

## 2026-07-28 — Word study re-enabled (no opt-in); free alignment roadmap

**Owner**: Leave Word study available with real data (feature-detect API). Improve toward English-word hover **when possible without spending money**.

**Code**: `strongs_optional.js` — no `wordStudy` gate; probe = `/health` only.

**Docs**: `docs/365DBR/Word-Study-and-Alignment.md` (current vs desired; free/open avenues).

**Bible is primary.**

---

## 2026-07-28 — Session close: check-in on main + handoff

**Owner**: Testing index/bible + Word study looked good. Check in to **main**; button up next session.

**This session deliverables (committed)**:
- Safe `populate_day` token clear (cross-day wipe fix); `audit_empty_originals.py`; stress section I
- Word study: `strongs_optional.js` + index/bible UI (feature-detect API, original-first, human refs)
- Docs: Word-Study-and-Alignment.md (free/open EN-hover roadmap; no paid RI budget)

**Next session**: paste prompt from `Handoff-Next-Session.md`. Suggested pick: **C** Phase 5 minimal annotations.

**Bible is primary.**

---

## 2026-07-29 — Phase 5 minimal: curated speaker/theme annotations

**Session start**: Read handoff-only set. Smoke green before code:
- `audit_empty_originals`: dual_claim=0 residual=4
- stress dual-read sample (20) + section I: **PASS**
- query API `/health` OK
- git clean @ `73771a5` (same tip as main)

**Increment (pick C)**: Phase 5 minimal curated annotations — no LSB, no Option B, no invented EN↔token maps.

**Deliverables**:
| Artifact | Role |
|----------|------|
| `db/seeds/phase5_curated_annotations.json` | 15 rows (8 speaker + 7 theme); every row has `source` + basis |
| `db/scripts/seed_annotations.py` | Idempotent replace by `source_tag=curated-manual-phase5-v1` |
| `db/migrations/003_annotations_range_order.sql` | Drop broken lexical BCV CHECK; trigger validates `verse_order` |
| `db/query/annotations.py` | covering-verse / speaker / theme / `si_demo_query` |
| `query_db.py` + `serve_query_api.py` | CLI + HTTP: speaker, theme, annotations, si-demo |
| `load_verse` | includes range-covering speaker/theme on verse payload |
| `test_annotations_phase5.py` | seed + range + S.I. demo smoke |

**Schema note (ours)**: `CHECK (start_verse_id <= end_verse_id)` is **lexical** and rejects real ranges (e.g. `MAT.5.3` > `MAT.5.12` as text). Fixed via migration 003 + `verse_order` trigger. Queries expand ranges by `verse_order`, not string compare.

**Curated seed (high-certainty only)**:
- Speakers: God (GEN.1.3, GEN.1.26), YHWH (GEN.12.1–3, EXO.20.1–17), Jesus (MAT.5.3–12 Beatitudes, JHN.14.6, MAT.28.18–20, REV.22.20)
- Themes: Creation, Abrahamic covenant promise, Law/Decalogue, Messianic suffering (ISA.53.4–6), Gospel/salvation (JHN.3.16), Resurrection (MAT.28.1–10), Shepherd care (PSA.23)

**Verified**:
```
apply_migrations → 003 applied
seed_annotations → 15 inserted (speaker=8 theme=7)
test_annotations_phase5 → PASS
query_db speaker Jesus → 4 ranges
si-demo God + H430 → GEN.1.3, GEN.1.26
ETL superscription/title preserved (205)
```

**How to run**:
```powershell
python db/scripts/apply_migrations.py
python db/scripts/seed_annotations.py
python db/scripts/test_annotations_phase5.py
python db/scripts/query_db.py speaker --name Jesus --compact
python db/scripts/query_db.py si-demo --speaker God --strong H430 --compact
```

**Not in this increment**: Option B loadDailyBread; LSB; free EN↔token alignment; frontend annotation UI; full-Bible speaker tagging.

**Bible is primary.**