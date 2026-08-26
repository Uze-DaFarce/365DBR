# Mt. Sinai LLC Monorepo - Knowledge Base Index

**Primary Source of Truth**: The Word of God (the Bible, 66 books, read contextually).

**Secondary Source**: This `docs/` knowledge base — for project history, technical details, agent learnings, and S.I. development. Use to avoid repetition of information.

**Current Focus (as of 2026-08-26)**: 100% on 365DBR as a **static** public product on GoDaddy, using local Postgres only as a workshop (ETL / verify / export). Other apps (HeIsRisen/m, mtsinai, dbdkids) kept in mind for cross-app interactions, constraints (CSP, shared hosting), and potential future reuse, but not the active priority unless urgent.

**Hosting freeze**: Production **cannot** run a relational database on GoDaddy shared hosting. Do not transition the live reader to Postgres, cPanel MySQL, or a public query API until the owner can afford a host that actually runs PostgreSQL. Canonical: [docs/365DBR/Hosting-and-Runtime.md](./365DBR/Hosting-and-Runtime.md).

## Current Documentation Structure
- `docs/INDEX.md` (this file) — Master hub.
- `docs/Roles/` — Specialized session prompts:
  - Top-Level-Program-Lead.md (big picture, maintains top-level TODO/progress, coordinates specialists, aware of agent styles like Bolt/Sentinel/Palette)
  - Database-PM.md (DB design, migration planning, data model for 365DBR + S.I.)
  - 365DBR-DEV.md (implementation, code changes, following architecture)
- `docs/365DBR/` — Primary focus area.
  - `Data-Sources.md` — Critical: Production data only (repo data is placeholder).
  - `Hosting-and-Runtime.md` — Canonical: GoDaddy = static files; no live DB on shared hosting.
  - `365DBR_AGENTS.md` — Code constraints (moved from mtsinai).
- `docs/Agents/` — Historical Jules agent prompts (Bolt, Palette, Sentinel) with still-relevant principles extracted.
- `docs/Project Blueprint_ Scriptural Intelligence (SI).md` — Core S.I. vision ("Deep Thought").
- `docs/Past-Agents-Knowledge-Organization.md` — Plan for .jules journals.
- Other: Cross-cutting (e.g., SUB_SITES.md summarized if needed), app summaries for awareness.

See full file list via tools or `docs/` directory.

## Key Sections
- [Project Overview & Locations](#project-overview--locations)
- [Scriptural Intelligence (S.I.)](#scriptural-intelligence-si)
- [365DBR](#365dbr)
- [Database Strategy](#database-strategy)
- [Documentation Principles](#documentation-principles)
- [Knowledge from Past Work (.jules)](#knowledge-from-past-work-jules)
- [Outdated Items & Fixes](#outdated-items--fixes)
- [Short & Long-Term Goals](#short--long-term-goals)

---

## Project Overview & Locations

### Deployed Locations (as of 2026-06-30)
- **Corporate Website**: https://mt-sin.ai/
- **365DBR (Daily Bible Reading + Browser)**:
  - Main app: https://mt-sin.ai/365DBR/index.html
  - Bible Browser: https://mt-sin.ai/365DBR/bible.html
  - Static version (for AI/crawlers): https://mt-sin.ai/365DBR/data/0630/index.html (example date-based static output)
- **HeIsRisen (Easter Game)**:
  - Desktop: https://mt-sin.ai/HeIsRisen/
  - Mobile: https://mt-sin.ai/m/
- **daybydaykids.com**: Related/redirected content (see other apps).
- **New**: apps/dbdkids (in progress, no documentation yet).

### Source Control
- GitHub: https://github.com/Uze-DaFarce/365DBR (monorepo hosted under this name)
- Primary local: D:\Users\uzeda\Mt. Sinai LLC\monorepo
- AI worktree: Separate git worktree for safe editing.

**Note**: All other translations to date accessed via api.bible. LSB access pending via app.library.bible after LLC clarification from 316 Publishing.

---

## Scriptural Intelligence (S.I.)

**Full Name**: Scriptural Intelligence  
**Codename**: "Deep Thought" (from Project Blueprint)

### Mission
To provide a logical, truthful alternative to secular AI by filtering all reality through the unchanging Word of God.

### High-Level Success Criteria
- A completely secure, validated application usable like current AI tools.
- Primary "LLM" is the Word of God (Bible, literal from Hebrew/Greek) instead of "consensus of reddit" or majority worldviews.
- Far less complicated in core functions.
- Never lies or states illogical nonsense as fact due to human consensus.
- Consensus of man is only used *after* all Biblical validation checks pass.
  - Example: Practical queries like "How many quarts of which oil and what filter for a 2014 Acura MDX oil change?" can use verified external data post-Biblical filter.
- Anchored in Biblical authority while being practically useful.

See full blueprint: [Project Blueprint_ Scriptural Intelligence (SI).md](./Project%20Blueprint_%20Scriptural%20Intelligence%20(SI).md)

---

## 365DBR

### Current Focus
- Daily structured Bible reading plan (<15 min/day).
- Multi-translation support.
- **Public product is static JSON + static Word study packs** on GoDaddy shared hosting. A live relational database is **not** the production runtime and cannot be until paid Postgres-capable hosting exists. See [Hosting-and-Runtime.md](./365DBR/Hosting-and-Runtime.md).
- Local Docker Postgres remains the workshop for accuracy work and static export (foundation for S.I. later).

### Data Sources (Critical)
**The real data is NOT in the repository.** 
- The `apps/365DBR/data/` folder in the repo contains only placeholder, example, and invalid data.
- **Real production data lives only at** `https://mt-sin.ai/365DBR/data/`
  - Date-based folders (MMDD), e.g. for June 30: `https://mt-sin.ai/365DBR/data/0630/`
  - `manifest.json` — lists the day's passages and files.
  - Individual passage JSON files, e.g.:
    - `https://mt-sin.ai/365DBR/data/0630/2KI.13.1-2KI.14.29.json`
    - `https://mt-sin.ai/365DBR/data/0630/ACT.7.7-ACT.7.27.json`
    - `https://mt-sin.ai/365DBR/data/0630/PSA.78.47-PSA.78.53.json`
    - `https://mt-sin.ai/365DBR/data/0630/PRO.16.13-PRO.16.15.json`
  - Static HTML for crawlers/AI: e.g. `https://mt-sin.ai/365DBR/data/0630/index.html`
- **Always** fetch from production for real Bible content, analysis, DB population, or validation. The repo data should never be treated as authoritative.

### Key Technical Details (Current)
- Data pipeline: Python scripts (generate_readings.py, fetch_readings.py from api.bible, compile_site.py).
- Frontend: React (esm.sh, no traditional build) in bible.html + index.html.
- Current primary: LSV (Literal Standard Version).
- Static output available for crawlers/AI.

### Translation Plans
- **LSB (Legacy Standard Bible)**: Permission obtained, but **not yet integrated**.
  - Waiting on clarification from Diana M (316 Publishing) regarding LLC setup on app.library.bible.
- Planned expansions (when access/affordable):
  - WEB (World English Bible) — referenced but no data yet.
  - NKJV
  - ESV

### Database Requirements (High-Level)
- Highly relational design **for the local workshop and future S.I.** — not for the current public host.
- Multiple paths in and out.
- **Far beyond** simple Book/Chapter/Verse.
- Chapters and verses are man-made additions (vary between translations).
- Must handle:
  - Original Hebrew/Greek text.
  - Contextual metadata: speaker, subject, timing, audience, etc.
  - Multiple translations.
- Will support rich semantic queries for S.I. (e.g., "What did Jesus say about X?") **once a host can run PostgreSQL**.
- **Status (2026-08-26)**: Local schema + full 365 load + query layer **done**. Public cutover **blocked** by GoDaddy shared hosting. Do not port to cPanel MySQL. See [Hosting-and-Runtime.md](./365DBR/Hosting-and-Runtime.md).

See also:
- [365DBR_AGENTS.md](./365DBR_AGENTS.md) for code stability constraints (verseMap, audio playback, verification).
- [Data-Sources.md](./365DBR/Data-Sources.md) for the critical production data access rules (repo data is placeholder only).

---

## Database Strategy

**Runtime freeze (2026-08-26)**: The public 365DBR site stays on **static files**. Local PostgreSQL is the workshop. Do not treat “move production onto a database” as active work. Canonical: [docs/365DBR/Hosting-and-Runtime.md](./365DBR/Hosting-and-Runtime.md).

**Note**: Dedicated design session completed 2026-07-01. Phases 1–5 **local** work is implemented. Production cutover (Phase 4 Option B / Phase 6) is **blocked by hosting cost**, not by schema unreadiness.

- Must be **highly relational** (implemented locally).
- Support complex queries across translations, original languages, and contextual metadata (original_tokens + annotations + ranges) — **on the PC / future paid host**, not on GoDaddy.
- Key challenges addressed in design:
  - Man-made chapter/verse divisions → verse alignment for practicality + tokens + annotations for literary/context independence.
  - Need for speaker, subject, timing, literary context, etc. → dedicated `annotations` + `cross_references` tables with ranges.
  - Multiple entry points (text search, semantic, thematic, speaker-based, etc.) → tsvector, strongs indexes, range queries, daily + plan tables.
- Integration with 365DBR today: **export** (static `data/` + `ws/`) from the local DB. Live `loadDailyBread` from DB is Option B and is frozen.
- Tech: **PostgreSQL** for the workshop and for any future paid host. **Not** cPanel MySQL. Matches Blueprint when hosting allows.
- **Current artifacts** (read these):
  - `docs/365DBR/Hosting-and-Runtime.md` (what actually runs in production vs locally).
  - `docs/365DBR/Database-Schema.md` (DDL, ERD mermaid, decisions, S.I. alignment, v0.1 scope).
  - `docs/365DBR/Migration-Plan.md` (phases 0-6; Option B / Phase 6 blocked until Postgres-capable hosting).

**Status**: Local schema + 365 ETL + query API + static Word study export complete. Public site remains static on GoDaddy. Next work must ship as static files until hosting changes.

---

## Documentation Principles

- **Shared docs**: Root `docs/` folder.
- **App-specific docs**: `docs/<app-name>/` (e.g., `docs/365DBR/`, future `docs/dbdkids/`).
- Goal: One place for all documentation to capture cross-app interactions and big-picture goals.
- Reduce repetition: Capture answers, decisions, constraints, and learnings here.
- Process: Document > Research > Re-document (iterative refactoring).

Current central files:
- `docs/INDEX.md` (this file)
- `docs/365DBR_AGENTS.md`
- `docs/Project Blueprint_ Scriptural Intelligence (SI).md`

---

## Knowledge from Past Work (.jules) & Agent Prompts

The `.jules/` directory contains detailed journals from previous scheduled agent work (Bolt, Palette, Sentinel, etc.).

See:
- [Past Agents Knowledge Organization Plan](Past-Agents-Knowledge-Organization.md)
- [Agents/ folder](Agents/) for preserved agent prompts and instructions

**Key Categories**:
- Performance & Optimization (Bolt)
- Accessibility & UX Patterns (Palette)
- Security & Validation (Sentinel)

**Status**: Review complete. Extraction in progress. Agent prompts are preserved here for institutional knowledge and because many rules (testing discipline, data sources, git hygiene, priorities) remain relevant.

See also:
- `.jules/bolt.md` (Bolt's running journal of critical learnings)
- [docs/Agents/Bolt-Agent-Prompt.md](Agents/Bolt-Agent-Prompt.md) (full original prompt + still-relevant rules)
- `.jules/palette.md` (Palette's running journal of critical learnings)
- [docs/Agents/Palette-Agent-Prompt.md](Agents/Palette-Agent-Prompt.md) (full original prompt + still-relevant rules)
- `.jules/sentinel.md` (Sentinel's running journal of critical learnings)
- [docs/Agents/Sentinel-Agent-Prompt.md](Agents/Sentinel-Agent-Prompt.md) (full original prompt + still-relevant rules)

**Note on Agent Prompts**: Full historical prompts from Jules agents are preserved here for institutional knowledge. Many rules (production data, test improvement, git hygiene, validation, UX standards, hallucination guardrails) remain relevant to 365DBR and S.I. Outdated sections (e.g., pre-Easter HeIsRisen focus) are annotated in each file.

## Current Documentation Structure (as of 2026-07-01)

- `docs/INDEX.md` (this file) — Master hub for shared knowledge.
- `docs/365DBR/` — 365DBR-specific (focus area until S.I. data is leveraged).
  - `Data-Sources.md` — Production data access (repo data is placeholder only).
  - `Hosting-and-Runtime.md` — Canonical production freeze (GoDaddy = static; local Postgres = workshop).
  - `365DBR_AGENTS.md` — Critical code constraints for 365DBR.
- `docs/Agents/` — Historical agent prompts and knowledge.
- `docs/Project Blueprint_ Scriptural Intelligence (SI).md` — Core S.I. vision ("Deep Thought").
- `docs/Past-Agents-Knowledge-Organization.md` — Plan for organizing .jules journals.
- Root-level shared files and app-specific subfolders as needed.

**Prioritization Note (per user)**: 100% focus on 365DBR until its data can be fully leveraged for the S.I. "LLM". Other apps (HeIsRisen, mtsinai, dbdkids) should be kept in mind for cross-app interactions and constraints, but urgent work is on 365DBR. Bible is primary source of truth; this docs/ is secondary.

---

## Outdated Items & Fixes (as of 2026-06-30)

### README.md (Root)
- **Fixed in this update**: Updated app list, added dbdkids mention, corrected paths, added links to current deployments, referenced centralized `docs/`, noted translation status and S.I. direction.
- Still references old lowercase "365dbr" in some places — being cleaned.
- Lacks current translation expansion plans and DB migration status.

### Translation Reality
- Still using LSV via api.bible as primary.
- LSB integration blocked pending LLC clarification from 316 Publishing.
- Future: WEB (data needed), NKJV, ESV (cost/access).

### Scattered Knowledge
- **Fix**: Centralized in `docs/`. All future documentation goes here.
- Cross-app interactions (e.g., CSP for sub-sites, shared learnings) now captured at root.

### .jules Journals
- Rich but scattered historical notes.
- **Fix in progress**: Extract, organize, and reference in `docs/` for efficiency.

### Other
- Some code/docs still assume LSV-only or old data pipeline.
- AGENTS.md moved from apps/mtsinai/ to docs/365DBR_AGENTS.md (completed).
- **“Transition 365DBR to a relational database” as production work is obsolete (2026-08-26).** Public site stays static on GoDaddy. See `docs/365DBR/Hosting-and-Runtime.md`.

---

## Short & Long-Term Goals

### Short-Term
- Stabilize documentation in `docs/` to eliminate repetition. (Centralization largely complete.)
- Complete LSB access (pending Diana M / 316 Publishing).
- Add WEB data support.
- Local relational DB (schema + 365 ETL + query/export) complete; **production cutover frozen** until Postgres-capable hosting is affordable. Meanwhile ship static JSON + `ws/` packs on GoDaddy.
- Review and integrate key .jules learnings (data/validation patterns already extracted to relevant docs).
- Update all references (README, etc.) to point to docs/. Expand 365DBR/ docs as design evolves.

### Long-Term (S.I. Focused)
- Build "Deep Thought" — secure, validated Scriptural Intelligence app.
- Core: Bible as primary "model" with strict tiered validation (Bible > Science > Wisdom).
- 365DBR as foundational data source (daily reading + rich contextual DB).
- Advanced capabilities: Speaker/subject/timing-aware queries, multi-translation context, semantic search beyond chapter/verse.
- Practical overlay: Man-consensus only for post-Biblical validated needs.
- Local/secure execution.
- Support for multiple projects (365DBR, dbdkids, etc.).

See full details in [Project Blueprint_ Scriptural Intelligence (SI).md](./Project%20Blueprint_%20Scriptural%20Intelligence%20(SI).md)

---

**Last Updated**: 2026-08-26 (title display: one Heading on focal English in index + bible)

**Current Phase**: **Static production freeze.** Psalm titles + Word study published. Titles now show **once** as Heading on the focal English slot in both readers (not on compare/original). LSV/KJV verse body is not altered. Option B / live API **blocked by budget**. **Next**: surface the 15 speaker/theme annotations in Word study, or owner FTP of this title UI — see `docs/365DBR/Handoff-Next-Session.md`.

**TODO / Progress Tracker (365DBR → S.I. DB foundation)**:
- [x] Read required docs + git + prod data analysis (manifests 0701/0630 + Hebrew + **NT Greek** passages).
- [x] Current model analysis (api.bible nested + verseMap BCV processing, 365-day plan, pipeline integrity). Explicit contrast: Hebrew (strong-tagged words) vs Greek (running text, no strongs in current sources).
- [x] Tech recommendation (PostgreSQL) + initial highly-relational schema (books/verses/tokens/translations/annotations/daily) documented. NT/Greek handling section + updates added after review.
- [x] High-level migration plan (6 phases...) + risks. ETL notes updated for Greek/Hebrew token parsing branch.
- [x] Phase 1 handoff merged directly into `docs/Roles/365DBR-DEV.md` (new sessions start by reading the role file; it now includes full scoped Phase 1 task + required docs list). Separate handoff file reduced to redirect note.
- [x] Phase 1 implemented: Docker Postgres 16, `db/migrations/001_initial_schema.sql`, apply/seed/verify scripts, 66 books + LSV/KJV seeds; `verify_schema.py` **PASSED**.
- [x] Phase 2 sample population: `db/scripts/populate_day.py` + `verify_population.py`; days **0123, 0702, 0823** PASS (local GRCTR + WLC; LSV/KJV text match; Hebrew Strong's + Greek tokens).
- [x] Phase 2 full load: **365/365 days** populated from local packs (`--all --source local`); spot-verify PASS (0101, 0615, 1225, 1231).
- [x] Phase 3 tool: `db/scripts/verify_db.py` (book counts, plan, TR samples, Strong's, perf, S.I. smoke, JSON spot).
- [x] Phase 3 sign-off: `verify_db.py` **OVERALL PASS** (56/56); full canonical coverage; LSV=KJV=30785; TR samples OK.
- [x] Phase 4.1 Option A: `db/query/` + `query_db.py` (day / verse / Strong's / dual-read); smoke `test_query_phase4.py` PASS; commit `1b39639`.
- [x] Phase 4.2 Option A: local read-only HTTP API `serve_query_api.py` (127.0.0.1:8765) + `test_query_api_phase4.py` PASS; **still no frontend change**.
- [x] Verse identity: English-primary + `verseOrgIds` alignment (`002_verse_alignment.sql`, parse/populate/load_day); titles → annotations; sample days re-populated; dual-read PASS. **Do not blame api.bible without repro** — trust and verify.
- [x] Full 365 re-populate with alignment: **365/365 OK** after English-only BCV `ensure_verse` FK fix; `repair_verse_order.py`; stress tests (`test_query_stress_phase4.py`) month-ends/alignment edges — not only 0101/GEN.1.1.
- [x] Empty-original audit: dual-claim cross-day wipe fixed in `populate_day` clear; 181→4 residual; `audit_empty_originals.py` + stress section I.
- [x] Query API + browser Word study (feature-detect API; original-first; on when API up). See `docs/365DBR/Word-Study-and-Alignment.md`.
- [x] Phase 5 minimal: curated speaker/theme annotations (`phase5_curated_annotations.json`, seed script, migration 003 range-by-verse_order, query + si-demo). Sparse demo only — not full-Bible tagging.
- [x] Static Word study publish path for GoDaddy: `export_word_study_static.py` → `apps/365DBR/ws/`; CSP-safe (no localhost probe on production).
- [x] Psalm titles + multi-claim English splits: `audit_psalms` PASS; reader stores USFM titles in `entry.titles[]` (not glued into v.1).
- [x] **Hosting freeze documented**: no live relational DB on GoDaddy shared hosting (`docs/365DBR/Hosting-and-Runtime.md`).
- [x] Owner FTP of latest `ws/` + `index.html` / `bible.html` / `strongs_optional.js` after Psalm/title work; spot-checked on mt-sin.ai (2026-08-26).
- [x] Title display: one Heading on focal English in `index.html` + `bible.html`; no duplicate on compare. LSV/KJV body left as in the data.
- [ ] Surface Phase 5 speaker/theme annotations in Word study UI (export already includes `annotations[]`; panel does not render them).
- [ ] Improve Word study toward English-word hover when **free/open** alignment data exists (no paid reverse interlinear budget).
- [ ] Residual empty originals (REV.12.18 placeholder) — optional later design.
- [ ] Expand curated annotations (more speakers/themes; still require `source` + textual basis).
- [ ] LSB integration (blocked pending 316 Publishing clarification); add WEB etc.
- [ ] Option B `loadDailyBread` from DB — **FROZEN** until Postgres-capable hosting is affordable **and** AGENTS audio verified. Do not start.
- [ ] Full rich metadata + deeper S.I. query prototypes; dual-write / cutover — **FROZEN** (same hosting blocker).
- Blockers: **GoDaddy cannot run this database** (budget); LSB access finalization.

**Next Steps (explicit)**:
1. ~~Phase 1–3~~ done (schema + full 365 load + reconciliation PASS).
2. ~~Phase 4 Option A backend~~ done (CLI, local API, English-primary alignment, 365 re-populate, stress tests).
3. ~~Empty-original dual-claim wipe~~ done (safe clear + re-populate; residual placeholder documented).
4. ~~Optional Strong's UI~~ done (feature-detect local API; static `ws/` on production).
5. ~~Phase 5 minimal annotations~~ done (15 curated rows + si-demo query; expand when ready).
6. ~~Psalm title/alignment + static Word study~~ done, checked in on main, published, owner-approved.
7. Until new hosting: only static-safe increments. **Next: show the 15 speaker/theme annotations in Word study.**
8. Option B / public API / Phase 6: **do not schedule** until the owner can afford a host that runs PostgreSQL.
9. Keep 100% focus on 365DBR. LSB still blocked.

**Handoff guidance**: New sessions: read `docs/365DBR/Handoff-Next-Session.md` first (scoped next work), then `docs/365DBR/Hosting-and-Runtime.md` (no live DB on GoDaddy), then `docs/Roles/365DBR-DEV.md` + INDEX + Verse-Identity + latest DEV-Logs. Prefer stress tests over toy 0101/GEN.1.1. Trust api.bible; verify with payload fields before blaming API.

This document will be maintained as the single source of truth to minimize repetition. Never repeat analysis — reference the 365DBR/ files.