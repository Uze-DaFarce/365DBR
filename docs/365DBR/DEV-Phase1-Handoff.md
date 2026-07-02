# Handoff Prompt: 365DBR DEV — Phase 1 (DB Infra + Schema Bootstrap)

**Context**: This is a clean, self-contained handoff from Database PM / Architect. The Top-Level goal of the current phase is delivered: initial schema, tech rec, migration strategy, and this handoff plan. See full status in `docs/INDEX.md`.

**YOU MUST BEGIN BY READING THESE (use read_file tool, in order)**:
1. `docs/INDEX.md` (full — especially Database Strategy, Current Phase, TODO tracker, Next Steps)
2. `docs/Project Blueprint_ Scriptural Intelligence (SI).md`
3. `docs/365DBR/Data-Sources.md` (CRITICAL: only https://mt-sin.ai/365DBR/data/ MMDD/ is authoritative; repo data/ is placeholder)
4. `docs/365DBR_AGENTS.md`
5. `docs/365DBR/Database-Schema.md` (target v0.1 DDL, ERD, decisions, principles)
6. `docs/365DBR/Migration-Plan.md` (full phases, ETL sketch, risks, success criteria)
7. `docs/Roles/365DBR-DEV.md` (your role rules)

Also review git status for unmerged changes before any edit.

**Current overriding priority**: 100% on 365DBR DB foundation for S.I. Bible (Tier 1) is absolute truth. Fail fast on any data corruption or deviation from prod.

## Scoped Task for This Handoff: Phase 1 — Infrastructure + Schema Bootstrap

Implement **only** the items below. Deliver small, reviewable increments. Do not jump to ETL/population or frontend changes yet.

### 1. Environment Setup (Postgres)
- Add simple local dev setup: `docker-compose.yml` (or documented commands) for `postgres:16` (or latest 16.x) with persistent volume.
- DB name: `mt_sinai_365dbr`, user/pass for local dev (document; use .env or similar, never commit secrets).
- Connection string / config example (Python or env).
- Verify connectivity from the workspace (e.g. psql or Python script).
- Note hosting considerations for later (shared env / CSP if API added; keep simple for now).

### 2. Schema Implementation
- Create `db/` or `migrations/` folder in repo root or under apps/365DBR/ (propose structure, keep simple).
- Implement the **exact** v0.1 DDL from `Database-Schema.md` (or minor non-breaking tweaks only after discussion).
  - Include: books, verses, translations, verse_translations (with tsvector), original_tokens, annotations, cross_references, daily_readings, daily_passages, data_sources.
- Seed data:
  - `books`: use the BIBLE_DATA / OT/NT lists from `bible_common.py`. Populate all 66 with correct order_canonical, testament, num_chapters (from existing constants).
  - `translations`: LSV (primary=true, source bibleId 01b29f4b342acc35-01), KJV (de4e12af7f28f599-01). Add comments for future LSB etc.
- Add basic indexes as listed in schema doc.
- Create a `schema_version` or use alembic/migrations table entry for v0.1.

**Migrations tooling**: Recommend starting with plain numbered SQL scripts + a simple Python apply script (or introduce Alembic if clean fit). Keep auditable. Document how to reset/re-apply.

### 3. Basic Validation + Smoke Tests
- After apply: run queries that confirm:
  - 66 books.
  - Verse counts per book match BIBLE_DATA expectations (reuse helpers).
  - Translations rows present.
  - Sample verse insert test (manually or script) for e.g. GEN.1.1.
- Enhance or create a `tests/test_db_schema.py` (or extend existing test_*.py) that runs against local DB.
- **Use only production data patterns** for any test data (no reliance on repo placeholders).
- Run existing Python tests if they touch data (e.g. `python tests/test_day_and_easter.py`).

### 4. Documentation & Handoff Back
- Update `docs/365DBR/Database-Schema.md` or add notes if any implementation deviations.
- Add a `docs/365DBR/DEV-Logs.md` entry or section (date + what was done + any open questions).
- Provide clear "how to run" instructions (init DB, apply schema, verify).
- At end: report exact status against the TODO tracker in INDEX.md. List blockers, counts, verification results.
- Prepare for Phase 2 handoff (ETL population from prod e.g. 0701 + validation against JSON source).

### Constraints (Non-Negotiable)
- **Production data only** for anything real (when you reach verification/populate). See Data-Sources.md.
- Respect `365DBR_AGENTS.md` (no breaking verseMap assumptions yet — this phase is backend only).
- Improve, do not discard, test infrastructure.
- Git hygiene: check status before edits.
- All changes must serve faithful representation of the Biblical text.
- Radical precision: if something in schema doc is ambiguous, ask / note rather than assume.
- Keep scope to Phase 1. Do not implement ETL, annotations seeding, or UI yet.

### Deliverables
- Working local Postgres with full v0.1 schema applied + seeds.
- Reproducible setup instructions (README or in docs/365DBR/).
- Verification script/output showing books + sample verses + translations loaded correctly.
- Updated docs with implementation notes.
- Clean status for Top-Level / PM to advance tracker.

### Success for this increment
- Schema matches design doc.
- Seeds accurate (books from existing constants).
- Local dev repeatable in <5 min for a new environment.
- All validation queries pass.
- No impact on current 365DBR static/JSON pipeline.

**When complete**: Provide summary + link to verification. Update INDEX TODO status via the Lead. Then await next scoped handoff (Phase 2 sample ETL).

**Bible is primary. Docs are secondary memory. Use prod data. Document updates in docs/.**

If questions or blockers during execution, surface immediately with precise references to the docs above.

(Prepared by Database PM 2026-07-01. Reference this file + the schema/migration docs.)
