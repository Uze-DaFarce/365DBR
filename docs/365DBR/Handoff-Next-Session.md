# 365DBR-DEV — Next Session Handoff

**Date frozen**: 2026-08-25  
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
- Phase 1–3: Postgres 16, schema 001–003, full 365 ETL, verify historically green
- NT: GRCTR 3aefb10641485092-01; OT: WLC 0b262f1ed7f084a6-01
- Phase 4 Option A: db/query + query_db.py + serve_query_api.py (:8765)
- English-primary BCV + verseOrgIds; titles → annotations; trust api.bible and verify
- Empty-original dual-claim wipe fixed; residual empties ≈4
- Word study UI original-first; feature-detect
- Phase 5 minimal curated speaker/theme annotations (source_tag curated-manual-phase5-v1)
- **Static Word study publish for GoDaddy ($0)**: export_word_study_static.py → apps/365DBR/ws/
  - Client probes same-origin ws/manifest.json on production (CSP-safe; no 127.0.0.1)
  - Live API still preferred on localhost when up

## Env
- Prefer primary monorepo: `D:\Users\uzeda\Mt. Sinai LLC\monorepo` on **main**
- docker compose up -d (or docker start mt-sinai-365dbr-postgres); db/.env; never commit secrets
- PowerShell: quote days --day "0131"; no && use ;

## Key commands
docker compose up -d
python db/scripts/export_word_study_static.py
# FTP apps/365DBR/ws/ + strongs_optional.js → https://mt-sin.ai/365DBR/
python db/scripts/serve_query_api.py
cd apps/365DBR; python -m http.server 5500
python db/scripts/test_query_stress_phase4.py --dual-read-limit 60 --seed 7
python db/scripts/test_annotations_phase5.py
python db/scripts/audit_empty_originals.py

## First actions this session
1. git status on main; Docker up; confirm ws/manifest.json exists (or re-export)
2. Propose ONE minimal next increment; align if ambiguous
3. Implement, test, document INDEX + DEV-Logs; check in on main when done

## Recommended next increments (pick one)
P. Confirm owner FTP’d ws/ + strongs_optional.js; spot-check Aa on mt-sin.ai
C2. Expand Phase 5 curated annotations (source + basis always)
G. Surface speaker/theme annotations in Word study panel (static or API)
D. Option B loadDailyBread from DB ONLY if small + AGENTS verified
E. Free/open EN↔token alignment research only when prioritized
F. Small polish only if owner reports a concrete bug

Constraints: no LSB until 316 unblocked; do not invent EN↔Strong's maps; no global source_verse_id token wipe; static JSON primary for daily reader until Option B deliberate; GoDaddy = static (no live Postgres on shared host).

Bible primary. Docs secondary memory.
```

---

## State snapshot (2026-08-25)

### Locked decisions
| Decision | Detail |
|----------|--------|
| User-facing BCV | Modern English (KJV/LSV-compatible) |
| Live reader | Static JSON primary |
| Word study on GoDaddy | **Static `ws/` packs** (same-origin); not cPanel MySQL; not paid VPS required |
| Live API | Localhost / future cheap VPS (~$5–12/mo) when wanted |
| Token clear | Never global `DELETE WHERE source_verse_id = X` |
| Annotation ranges | `verse_order` (migration 003) |

### Publish Word study (owner)
1. `python db/scripts/export_word_study_static.py` (Docker up)
2. FTP `apps/365DBR/ws/` → `/365DBR/ws/`
3. FTP `apps/365DBR/strongs_optional.js` → `/365DBR/`
4. Hard-refresh; Aa should appear; no CSP localhost errors

### Last known green
```
static export: 66 books, ~31097 verses, ~8625 Strong's files, ~91 MB
stress / dual-read / annotations: historically PASS
GitHub main: includes static Word study commit
```

### Do not
- Invent English↔token alignment
- Port to cPanel MySQL for the Bible DB
- Reintroduce global source_verse_id day clear
- Treat local-only Word study as “done product” without FTP of `ws/`

---

**Bible is primary. Docs are secondary memory.**
