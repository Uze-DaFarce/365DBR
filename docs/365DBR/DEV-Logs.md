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
