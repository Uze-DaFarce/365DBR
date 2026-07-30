# 365DBR-DEV — Next Session Handoff

**Date frozen**: 2026-07-29  
**Priority**: Truth/Accuracy > Safety > Performance. Bible is Tier-1 truth.  
**Branch policy**: Owner works on **main** only (`docs/Git-For-You.md`). Agents handle git.

**Copy the “Session start prompt” block into a new agent session.**

---

## Session start prompt (paste this)

```
You are 365DBR-DEV for Mt. Sinai monorepo. Bible is Tier-1 truth. Truth/Accuracy > Safety > Performance.

## Read first (only these — do not re-research Phases 1–3 history)
1. docs/Roles/365DBR-DEV.md (role + principles; Phase 1 “do not ETL” is obsolete)
2. docs/INDEX.md (Current Phase + TODO tracker)
3. docs/365DBR/Handoff-Next-Session.md (this file)
4. docs/365DBR/Verse-Identity-and-Alignment.md
5. docs/365DBR_AGENTS.md + docs/365DBR/Word-Study-and-Alignment.md
6. docs/365DBR/Data-Sources.md (prod https://mt-sin.ai/365DBR/data/MMDD/; local packs gitignored)
7. db/README.md + docs/365DBR/DEV-Logs.md (latest entries only)
8. docs/365DBR/Migration-Plan.md (Phase 4–5 only)
9. docs/Git-For-You.md (main-only for owner)

Skip full Blueprint/schema re-read unless design choice requires it.

## What’s done (do not redo)
- Phase 1–3: Postgres 16, schema 001+002, full 365 ETL, verify historically green
- NT: GRCTR 3aefb10641485092-01; OT: WLC 0b262f1ed7f084a6-01
- Phase 4 Option A: db/query + query_db.py + serve_query_api.py (:8765)
- English-primary BCV + verseOrgIds; titles → annotations; trust api.bible and verify
- Empty-original dual-claim wipe fixed (safe populate clear); residual empties ≈4
- audit_empty_originals.py + stress section I (dual-claim regression)
- Word study UI: feature-detect API (ON when /health OK, no opt-in); original-first
- Owner tested index.html + bible.html — looks good
- Free-path English-hover Strong’s documented (no paid RI budget)
- Phase 5 minimal: 15 curated speaker/theme annotations (source_tag curated-manual-phase5-v1)
- migration 003: annotation ranges by verse_order (not lexical BCV)
- query: speaker / theme / annotations / si-demo (CLI + API)

## Env
- Prefer primary monorepo: `D:\Users\uzeda\Mt. Sinai LLC\monorepo` on **main**
- docker compose up -d; db/.env + DATABASE_URL; never commit secrets
- PowerShell: quote days --day "0131"; no && use ;

## Key commands
docker compose up -d
python db/scripts/apply_migrations.py
python db/scripts/seed_annotations.py
python db/scripts/serve_query_api.py
cd apps/365DBR; python -m http.server 5500
# then http://127.0.0.1:5500/index.html and bible.html
python db/scripts/test_query_stress_phase4.py --dual-read-limit 60 --seed 7
python db/scripts/test_annotations_phase5.py
python db/scripts/audit_empty_originals.py
python db/scripts/query_db.py si-demo --speaker God --strong H430 --compact

## First actions this session
1. git status on main; Docker up; quick smoke (stress or dual-read + annotations test + API health)
2. Propose ONE minimal next increment; align if ambiguous
3. Implement, test, document INDEX + DEV-Logs; check in on main when done

## Recommended next increments (pick one)
C2. Expand Phase 5 curated annotations (more high-certainty speaker/theme; always source + basis)
D. Option B loadDailyBread from DB ONLY if small + AGENTS verified + dual-read green
E. Free/open EN↔token alignment research only when prioritized (no paid sources)
F. Small polish only if owner reports a concrete bug
G. Optional: surface annotations in Word study panel (read-only; static JSON still primary)

Constraints: no LSB until 316 unblocked; do not invent EN↔Strong's maps; no global source_verse_id token wipe on populate clear; static JSON primary for daily reader until Option B deliberate.

Bible primary. Docs secondary memory.
```

---

## State snapshot (2026-07-29)

### Locked decisions
| Decision | Detail |
|----------|--------|
| User-facing BCV | Modern English (KJV/LSV-compatible) |
| Original wording | `verseOrgIds` → English id; keep `source_verse_id` |
| Live reader | Static JSON primary |
| Word study | Original-first when API up; improve EN-hover only with free/open data |
| Token clear | Never global `DELETE WHERE source_verse_id = X` |
| Annotation ranges | `verse_order` (migration 003), not lexical BCV string compare |
| Phase 5 seed | Sparse curated only; every row needs `source` + textual basis |

### How to smoke-test apps
1. `docker compose up -d`
2. `python db/scripts/apply_migrations.py` (001–003)
3. `python db/scripts/seed_annotations.py` (if annotations empty)
4. `python db/scripts/serve_query_api.py` (Word study + annotation endpoints)
5. `cd apps/365DBR; python -m http.server 5500`
6. http://127.0.0.1:5500/index.html and bible.html  
7. Readings: local `data/MMDD/` or fallback prod `https://mt-sin.ai/365DBR/data/`

### Key paths
| Path | Role |
|------|------|
| `apps/365DBR/strongs_optional.js` | Word study client |
| `apps/365DBR/index.html` / `bible.html` | Readers + Aa Word study |
| `db/scripts/serve_query_api.py` | Local API :8765 |
| `db/scripts/populate_day.py` | ETL + safe token clear |
| `db/scripts/audit_empty_originals.py` | Dual-claim empty audit |
| `db/seeds/phase5_curated_annotations.json` | Curated speaker/theme seed |
| `db/scripts/seed_annotations.py` | Idempotent annotation seeder |
| `db/query/annotations.py` | Phase 5 query helpers |
| `docs/365DBR/Word-Study-and-Alignment.md` | Word study + free alignment roadmap |

### Last known green
```
populate --all: 365 OK (after wipe fix)
empty originals: dual_claim=0 residual≈4
stress dual-read sample: PASS
owner UI test: index + bible + Word study OK
phase5 seed: 15 rows; test_annotations_phase5 PASS
si-demo God+H430: GEN.1.3, GEN.1.26
```

### Do not
- Invent English↔token alignment
- Pay for reverse interlinear unless owner budgets later
- Option B without AGENTS audio verify
- Reintroduce global source_verse_id day clear
- Seed annotations without `source` + textual basis
- Rely on lexical BCV `start <= end` for multi-digit ranges

---

**Bible is primary. Docs are secondary memory.**
