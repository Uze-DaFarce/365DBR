# Mt. Sinai LLC Monorepo - Knowledge Base Index

**Primary Source of Truth**: The Word of God (the Bible, 66 books, read contextually).

**Secondary Source**: This `docs/` knowledge base — for project history, technical details, agent learnings, and S.I. development. Use to avoid repetition of information.

**Current Focus (as of 2026-07-01)**: 100% on 365DBR until its data is fully leveraged for the S.I. ("LLM"). Other apps (HeIsRisen/m, mtsinai, dbdkids) kept in mind for cross-app interactions, constraints (e.g., CSP, shared hosting), and potential future reuse, but not the active priority unless urgent.

## Current Documentation Structure
- `docs/INDEX.md` (this file) — Master hub.
- `docs/Roles/` — Specialized session prompts:
  - Top-Level-Program-Lead.md (big picture, maintains top-level TODO/progress, coordinates specialists, aware of agent styles like Bolt/Sentinel/Palette)
  - Database-PM.md (DB design, migration planning, data model for 365DBR + S.I.)
  - 365DBR-DEV.md (implementation, code changes, following architecture)
- `docs/365DBR/` — Primary focus area.
  - `Data-Sources.md` — Critical: Production data only (repo data is placeholder).
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
- Transition from static JSON to highly relational database.
- Foundation for S.I. (daily immersion + semantic/contextual data).

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
- Highly relational design.
- Multiple paths in and out.
- **Far beyond** simple Book/Chapter/Verse.
- Chapters and verses are man-made additions (vary between translations).
- Must handle:
  - Original Hebrew/Greek text.
  - Contextual metadata: speaker, subject, timing, audience, etc.
  - Multiple translations.
- Will support rich semantic queries for S.I. (e.g., "What did Jesus say about X?").
- **Status**: Major discussion pending. Research done months ago but notes lost. To be documented iteratively (Document > Research > Re-document).

See also:
- [365DBR_AGENTS.md](./365DBR_AGENTS.md) for code stability constraints (verseMap, audio playback, verification).
- [Data-Sources.md](./365DBR/Data-Sources.md) for the critical production data access rules (repo data is placeholder only).

---

## Database Strategy

**Note**: Dedicated session completed 2026-07-01 (see role-driven analysis). Research refresh + initial design produced.

- Must be **highly relational** (implemented in design).
- Support complex queries across translations, original languages, and contextual metadata (original_tokens + annotations + ranges).
- Key challenges addressed in design:
  - Man-made chapter/verse divisions → verse alignment for practicality + tokens + annotations for literary/context independence.
  - Need for speaker, subject, timing, literary context, etc. → dedicated `annotations` + `cross_references` tables with ranges.
  - Multiple entry points (text search, semantic, thematic, speaker-based, etc.) → tsvector, strongs indexes, range queries, daily + plan tables.
- Integration with 365DBR for daily reading + S.I. backend (daily_readings + daily_passages + verse_translations).
- Tech: **PostgreSQL** recommended (rationale + trade-offs in docs). Matches Blueprint.
- **Current artifacts** (read these):
  - `docs/365DBR/Database-Schema.md` (DDL, ERD mermaid, decisions, S.I. alignment, v0.1 scope).
  - `docs/365DBR/Migration-Plan.md` (phases 0-6, ETL sketch from prod data only, validation, risks, success criteria, handoff guidance).

**Status**: Initial schema + high-level migration plan complete. Ready for prototyping / DEV handoff on Phase 1 (infra + schema bootstrap). See full details and iterative updates in the 365DBR/ docs above.

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

---

## Short & Long-Term Goals

### Short-Term
- Stabilize documentation in `docs/` to eliminate repetition. (Centralization largely complete.)
- Complete LSB access (pending Diana M / 316 Publishing).
- Add WEB data support.
- Relational DB design + initial schema/migration plan complete (2026-07-01 session); move to prototyping + sample population.
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

**Last Updated**: 2026-07-28 (Phase 4 Option A + Word study checked in on main; ready for Phase 5 or next pick)

**Current Phase**: Phase 4 Option A **solid** (DB query, dual-read, Word study original-first). Static JSON primary for live reader. **Next**: see `docs/365DBR/Handoff-Next-Session.md` (recommend Phase 5 minimal annotations, or Option B only if deliberate).

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
- [ ] Improve Word study toward English-word hover when **free/open** alignment data exists (no paid reverse interlinear budget).
- [ ] Option B `loadDailyBread` from DB only if small + AGENTS verified.
- [ ] Residual empty originals (English split / first-wins map / REV.12.18 placeholder) — optional multi-English→one-org design later.
- [ ] Iterate schema from feedback; seed minimal annotations for speaker/theme demo.
- [ ] LSB integration (blocked pending 316 Publishing clarification); add WEB etc.
- [ ] Full rich metadata + S.I. query prototypes; dual-write / cutover later.
- Blockers: LSB access finalization; any hosting/DB provisioning details.

**Next Steps (explicit)**:
1. ~~Phase 1–3~~ done (schema + full 365 load + reconciliation PASS).
2. ~~Phase 4 Option A backend~~ done (CLI, local API, English-primary alignment, 365 re-populate, stress tests).
3. ~~Empty-original dual-claim wipe~~ done (safe clear + re-populate; residual 4 documented).
4. ~~Optional Strong's UI~~ done (feature-detect API; static primary).
5. Phase 4 follow-up: optional English-split token sharing; Option B only if AGENTS verified.
6. Phase 5 when ready: minimal speaker/theme annotations for S.I. demos.
7. Keep 100% focus on 365DBR until data fully leveraged for S.I. LSB still blocked.

**Handoff guidance**: New sessions: read `docs/365DBR/Handoff-Next-Session.md` first (scoped next work), then `docs/Roles/365DBR-DEV.md` + INDEX + Verse-Identity + latest DEV-Logs. Prefer stress tests over toy 0101/GEN.1.1. Trust api.bible; verify with payload fields before blaming API.

This document will be maintained as the single source of truth to minimize repetition. Never repeat analysis — reference the 365DBR/ files.