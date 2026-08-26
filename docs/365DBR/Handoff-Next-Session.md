# 365DBR-DEV — Next Session Handoff

**Date frozen**: 2026-08-26  
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
4. docs/365DBR/Hosting-and-Runtime.md (CANONICAL: no live DB on GoDaddy)
5. docs/365DBR/Verse-Identity-and-Alignment.md
6. docs/365DBR_AGENTS.md + docs/365DBR/Word-Study-and-Alignment.md
7. docs/365DBR/Data-Sources.md (prod https://mt-sin.ai/365DBR/data/MMDD/; local packs gitignored)
8. db/README.md + docs/365DBR/DEV-Logs.md (latest entries only)
9. docs/365DBR/Migration-Plan.md (Phase 4–5 only; Option B / cutover blocked by hosting)
10. docs/Git-For-You.md (main-only for owner)

Skip full Blueprint/schema re-read unless design choice requires it.

## What’s done (do not redo)
- Phase 1–3: Postgres 16, schema 001–003, full 365 ETL, verify historically green
- NT: GRCTR 3aefb10641485092-01; OT: WLC 0b262f1ed7f084a6-01
- Phase 4 Option A: db/query + query_db.py + serve_query_api.py (:8765) — local only
- English-primary BCV + verseOrgIds; titles → annotations; trust api.bible and verify
- Empty-original dual-claim wipe fixed; residual empty ≈ REV.12.18 placeholder only
- Word study UI original-first; feature-detect local API; production uses static ws/
- Phase 5 minimal curated speaker/theme annotations (source_tag curated-manual-phase5-v1)
- Psalm superscription anchors + multi-claim org splits; audit_psalms PASS
- Reader: USFM titles stored as entry.titles[]; **Heading shown once on focal English** in index + bible (not compare/original)
- **Static Word study for GoDaddy ($0)**: export_word_study_static.py → apps/365DBR/ws/

## Hosting freeze (do not fight this)
- Public site is GoDaddy shared hosting. It cannot run PostgreSQL or a live API.
- Do not port the Bible DB to cPanel MySQL. Do not start Option B / public API.
- Local Docker Postgres = workshop (ETL, verify, export). Production = static files.
- Canonical: docs/365DBR/Hosting-and-Runtime.md

## Env
- Prefer primary monorepo: `D:\Users\uzeda\Mt. Sinai LLC\monorepo` on **main**
- docker compose up -d (or docker start mt-sinai-365dbr-postgres); db/.env; never commit secrets
- PowerShell: quote days --day "0131"; no && use ;

## Key commands
docker compose up -d
python db/scripts/export_word_study_static.py
# FTP apps/365DBR/ws/ + index.html + bible.html + strongs_optional.js → https://mt-sin.ai/365DBR/
python db/scripts/serve_query_api.py
cd apps/365DBR; python -m http.server 5500
python db/scripts/test_query_stress_phase4.py --dual-read-limit 60 --seed 7
python db/scripts/test_annotations_phase5.py
python db/scripts/audit_empty_originals.py
python db/scripts/audit_psalms.py

## First actions this session
1. git status on main
2. Default increment: surface the 15 speaker/theme annotations in Word study (static-safe) unless owner names a production bug
3. Implement, test, document INDEX + DEV-Logs; check in on main when done

## Recommended next increments (pick one — all $0 / static-hosting-safe)
G. Surface the 15 Phase 5 speaker/theme annotations in the Word study panel (payload already has annotations[]; UI ignores them)
C2. Expand Phase 5 curated annotations (source + basis always) — local DB then re-export after G
E. Free/open EN↔token alignment research only when prioritized (no paid RI)
F. Small polish only if owner reports a concrete bug

Do NOT pick: Option B loadDailyBread-from-DB; live public API; cPanel MySQL port; waiting on a VPS.

Constraints: no LSB until 316 unblocked; do not invent EN↔Strong's maps; no global source_verse_id token wipe; static JSON primary for daily reader; GoDaddy = static only.

Bible primary. Docs secondary memory.
```

---

## State snapshot (2026-08-26)

### Locked decisions
| Decision | Detail |
|----------|--------|
| User-facing BCV | Modern English (KJV/LSV-compatible) |
| Live reader | **Static JSON primary** (not a production DB) |
| Public hosting | **GoDaddy shared** — no live Postgres, no live API. See `Hosting-and-Runtime.md` |
| Word study on GoDaddy | **Static `ws/` packs** (same-origin); not cPanel MySQL; not paid VPS |
| Local Postgres | Workshop only (ETL, verify, export static files) |
| Option B / Phase 6 cutover | **Blocked** until affordable Postgres-capable hosting |
| Token clear | Never global `DELETE WHERE source_verse_id = X` |
| Annotation ranges | `verse_order` (migration 003) |

### Publish (owner — $0)
1. `python db/scripts/export_word_study_static.py` (Docker up)
2. FTP `apps/365DBR/ws/` → `/365DBR/ws/`
3. FTP `apps/365DBR/index.html`, `bible.html`, `strongs_optional.js` → `/365DBR/`
4. Hard-refresh; Aa should appear; Psalm titles should not glue onto v.1; no CSP localhost errors

### Last known green (local)
```
Psalm audit: PASS (0 mis-anchored superscriptions, 0 Psalm empties)
empty originals: residual 1 (REV.12.18 placeholder '-')
static export: 66 books, ~31097 verses, ~8625 Strong's files
stress / dual-read / annotations: historically PASS
```

Psalm titles + Word study: **on main, published, owner-approved** (2026-08-26).

### Do not
- Invent English↔token alignment
- Port to cPanel MySQL for the Bible DB
- Reintroduce global source_verse_id day clear
- Treat local-only Word study as “done product” without FTP of `ws/`
- Start Option B or a public API until hosting can run Postgres

---

**Bible is primary. Docs are secondary memory.**
