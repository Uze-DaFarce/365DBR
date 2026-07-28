# 365DBR-DEV — Next Session Handoff (post Phase 4 Option A)

**Date frozen**: 2026-07-27  
**Priority**: Truth/Accuracy > Safety > Performance. Bible is Tier-1 truth.  
**Copy the “Session start prompt” block below into a new agent session.**

---

## Session start prompt (paste this)

```
You are 365DBR-DEV for Mt. Sinai monorepo. Bible is Tier-1 truth. Truth/Accuracy > Safety > Performance.

## Read first (only these — do not re-research Phases 1–3 history)
1. docs/Roles/365DBR-DEV.md (role + principles; Phase 1 “do not ETL” is obsolete)
2. docs/INDEX.md (Current Phase + TODO tracker)
3. docs/365DBR/Handoff-Next-Session.md (this file — full state + next options)
4. docs/365DBR/Verse-Identity-and-Alignment.md (English-primary + verseOrgIds — non-negotiable)
5. docs/365DBR_AGENTS.md (verseMap / loadDailyBread / playVerse / audio — non-negotiable)
6. docs/365DBR/Data-Sources.md (prod https://mt-sin.ai/365DBR/data/MMDD/; local packs gitignored)
7. db/README.md + docs/365DBR/DEV-Logs.md (latest entries only)
8. docs/365DBR/Migration-Plan.md (Phase 4–5 only)

Skip full Blueprint/schema re-read unless design choice requires it.

## What’s done (do not redo)
- Phase 1–3: Postgres 16 docker, schema 001+002, seeds, full 365 ETL, verify_db OVERALL PASS historically
- NT original: GRCTR 3aefb10641485092-01; OT: WLC 0b262f1ed7f084a6-01 (bible_common.py)
- Phase 4 Option A: db/query + query_db.py + serve_query_api.py (127.0.0.1:8765)
- English-primary BCV: store/display modern English verseId; original tokens remapped via api.bible verseOrgIds (NOT invented Psalm offsets)
- Titles/superscriptions → annotations (type superscription/title); do not blame api.bible without repro
- Full re-populate --all: 365/365 OK after ensure_verse for English-only BCVs (GEN.31.55, MAL.4.1, etc.)
- Tests: test_query_stress_phase4.py (prefer over toy 0101/GEN.1.1); repair_verse_order.py if order clobbered
- Live index.html / bible.html / loadDailyBread UNTOUCHED — static JSON still primary

## Env
- Prefer primary monorepo: `D:\Users\uzeda\Mt. Sinai LLC\monorepo` on **main** only (see docs/Git-For-You.md). Agent handles git; user does not manage branches.
- docker compose up -d (postgres, DB mt_sinai_365dbr)
- db/.env + DATABASE_URL; never commit secrets
- PowerShell: quote days --day "0131"; no && use ;
- apps/365DBR for fetch/check; monorepo root for db/scripts/*

## Key commands
docker compose up -d
python db/scripts/apply_migrations.py
python db/scripts/repair_verse_order.py
python db/scripts/populate_day.py --day "MMDD" --source local
python db/scripts/populate_day.py --all --source local --continue-on-error
python db/scripts/verify_db.py
python db/scripts/query_db.py dual-read --day "0228,1231,0117" --source local
python db/scripts/serve_query_api.py
python db/scripts/test_query_stress_phase4.py --dual-read-limit 60 --seed 7
python db/scripts/test_query_phase4.py
python apps/365DBR/export_bible_meta.py   # after BIBLE_DATA changes
python apps/365DBR/check_data_integrity.py

## First actions this session
1. git status; confirm Docker up; smoke: test_query_stress_phase4.py (or dual-read sample) — NOT only 0101/GEN.1.1
2. Propose ONE minimal next increment; get alignment if ambiguous
3. Implement, test with hard days (month-ends, English edges, MAL.4 / PSA offset), document INDEX + DEV-Logs

## Recommended next increments (pick one; small + reviewable)
A. Optional Strong’s UI in bible.html/index.html that feature-detects http://127.0.0.1:8765 (or future API); MUST keep static JSON primary; verify playVerse/audio per AGENTS.md
B. Tighten empty-original English edge rows (some English BCVs have LSV/KJV but tokens=0) — content alignment audit, not blame API
C. Phase 5 minimal: seed a few curated annotations (speaker/theme) with source field; no LSB
D. Option B loadDailyBread from DB ONLY if small + AGENTS verified + dual-read green on stress sample

Constraints: no LSB until 316 Publishing unblocked; improve tests with real local packs; fail fast on data corruption.

Bible primary. Docs secondary memory.
```

---

## State snapshot (2026-07-27)

### Architecture decisions (locked)
| Decision | Detail |
|----------|--------|
| User-facing BCV | Modern English (KJV/LSV-compatible) |
| Original wording | Aligned via payload `verseOrgIds` → English id; keep `source_verse_id` |
| Titles | `annotations` superscription/title — not long-term “glue into v1 only” model |
| api.bible | Trust and verify; past “numbering bugs” were ETL/params/ignored fields |
| Live reader | Static JSON primary until Option B deliberately chosen |

### Key paths
| Path | Role |
|------|------|
| `db/migrations/001_initial_schema.sql` | Core schema |
| `db/migrations/002_verse_alignment.sql` | `verse_alignments`, `original_tokens.source_verse_id` |
| `db/etl/parse_passage.py` | Parse + org→English + titles |
| `db/scripts/populate_day.py` | ETL; ensures English-only BCVs |
| `db/query/` | `load_day`, `load_verse`, `search_strong`, `dual_read_day` |
| `db/scripts/query_db.py` | CLI |
| `db/scripts/serve_query_api.py` | Local read-only API :8765 |
| `db/scripts/repair_verse_order.py` | Fix clobbered `verse_order` |
| `db/scripts/test_query_stress_phase4.py` | Real-world tests |
| `docs/365DBR/Verse-Identity-and-Alignment.md` | Identity principles |

### Last verification (do re-run after pull)
```
populate --all: 365 OK / 0 failed
stress --dual-read-limit 60: PASS (~10k cells)
dual-read hard days (1231, 0117, 0222, 0319, 0819): PASS
```

### Open / known minor
- Some English edge BCVs may show LSV/KJV with `tokens=0` (original under mapped source history) — audit optional.
- Greek Strong’s largely absent in current GRCTR token data (surface tokens only).
- LSB blocked (316 Publishing).
- Detached HEAD / branch policy: attach commits to intended branch when checking in.

### Do not
- Re-bootstrap Phase 1 schema from scratch without need
- Treat repo `apps/365DBR/data/` placeholders as authority (local packs are real fetches gitignored; prod URL is published authority)
- Invent Psalm ±1 offsets when `verseOrgIds` present
- Change `verseMap` / `playVerse` without AGENTS verification
- Use only 0101 / GEN.1.1 / JHN.1.1 as proof of correctness

---

**Bible is primary. Docs are secondary memory.**
