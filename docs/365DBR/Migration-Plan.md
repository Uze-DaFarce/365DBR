# 365DBR Relational Database Migration Plan (High-Level)

**Phase**: DB design discussions and prototyping kickoff (2026-07-01 context).  
**Owner**: Database PM / Architect (this design); handoff scoped work to 365DBR DEV.  
**Goal**: Turn current static JSON pipeline (Python + api.bible → date-based prod data/) into a durable, queryable relational foundation that powers both daily 365DBR reading **and** advanced S.I. ("Deep Thought") features.

**Must read before any implementation or changes**:
- `docs/INDEX.md`
- `docs/Project Blueprint_ Scriptural Intelligence (SI).md`
- `docs/365DBR/Data-Sources.md` (production data rule is absolute)
- `docs/365DBR/Database-Schema.md` (the target)
- `docs/365DBR_AGENTS.md` (verseMap / audio / verification constraints)
- Relevant code: `apps/365DBR/{bible_common.py, fetch_readings.py, generate_readings.py, index.html, ...}`

## Current State (Pre-Migration)

- **Data pipeline**: 
  - `generate_readings.py` + `BibleNavigator` + verse counts in `bible_common.py` → `data/readings.json` (365 days).
  - `fetch_readings.py` (with API key) → fetches using Hebrew/Greek + parallels (KJV, LSV) → writes atomic JSON to `data/MMDD/*.json` + manifest.
  - Client (`index.html`): fetches manifest + files (local fallback → prod https://mt-sin.ai/365DBR/data/), `processResults`/`walkItems` → `verseMap` (BCV keys + multi-trans + original flattened text) → render + audio.
- **Output**: Static files served for 365DBR + static HTML snapshots for crawlers/AI.
- **Strengths**: Working daily plan, strong validation/integrity (omissions injection, cross-book splits, verse counts), LSV primary, Strong's in original.
- **Gaps** (why migrate): JSON files are not relational, no rich context, limited query power, hard to maintain multiple translations or add S.I. metadata, no single source of truth for advanced use.
- Authoritative source for population: **only** https://mt-sin.ai/365DBR/data/ (MMDD folders). Repo `apps/365DBR/data/` = placeholders only. See Data-Sources.md.

## Target State

- PostgreSQL DB with schema from Database-Schema.md (books, verses, translations, verse_translations, original_tokens, annotations, cross_references, daily_readings + daily_passages, provenance).
- Data faithfully ingested: full original tokens + Strong's + LSV (primary) + other parallels texts, aligned at verse level.
- 365 daily plan represented relationally.
- Extension points for speaker/audience/timing/literary/theme/semantic metadata (initially sparse; curated over time).
- Dual support during transition: static JSON continues to work; DB becomes source for new features + eventual replacement.
- Strict validation at every step (counts, ranges, book membership, provenance).
- Clear rollback / re-run path.

## High-Level Phases & Milestones

### Phase 0: Preparation (this session + immediate follow-up)
- [x] Core docs read + data analysis complete.
- [ ] Create DB-Schema.md + Migration-Plan.md (this file) + update INDEX.md.
- [ ] Tech setup research refresh (PG version, hosting fit, Python client libs).
- [ ] Identify seed data set (e.g. recent days like 0701 + a few historical for validation; later bulk all 365).
- Handoff: Database PM produces scoped DEV prompt referencing these docs + schema.

### Phase 1: Infrastructure & Schema Bootstrap (DEV implementable)
- Provision Postgres (local: Docker `postgres:16`; later managed).
- Run schema DDL (v0.1 from Database-Schema.md) + seed `books` + `translations` (LSV primary, KJV).
- Add Alembic (or simple `migrations/` numbered .sql) for versioned changes.
- Add basic indexes + tsvector setup.
- Validation: simple smoke queries + row counts.
- **Deliverable**: Empty-but-valid DB + migration scripts runnable from repo.
- **DEV scope note**: Provide exact DDL + seed data scripts + "run this to init" instructions.

### Phase 2: ETL / Population from Production Data (core migration work)
- New or extended Python: `etl/populate_db.py` (or integrate into fetch tools).
  - Load `readings.json` plan.
  - For target day(s): fetch manifest + passage JSONs **from production URLs only** (or use local mirror of prod snapshots if created).
  - Parse:
    - Main content → books/verses (ensure exist) + original_tokens (walk for strong + word text + order).
    - Parallels → verse_translations for matching keys (LSV, KJV).
  - Reuse / port logic from `bible_common.py`: `validate_content_integrity`, `extract_verse_ids`, `inject_missing_verses`, `count_expected_verses`, BIBLE_DATA, KNOWN_OMISSIONS handling.
  - Populate daily_readings + daily_passages from plan + ranges (parse api_format into start/end verse_ids).
  - Compute verse_order (global).
  - Atomic / transactional per day or batch.
  - Provenance: record data_sources rows (url, fetch_date).
- Strict guards: fail entire run on any mismatch (verse count, book, range containment, missing strongs where expected). No silent data loss.
- Test population on small set (e.g. 0701 + 0101 + one PSA/PRO).
- **Initial data target**: All 365 days (or priority slice) + full Bible coverage where ranges hit.
- Handle: cross-book ranges already split in pipeline; Hebrew book code normalizations.
- **Deliverable**: Reproducible population script + verified row counts matching expectations (e.g. "X tokens for PRO.16.16-17").
- Future: Make fetch_readings.py optionally write to DB (dual write) or deprecate JSON writes.

### Phase 3: Validation, Integrity & Reconciliation
- Cross-check: DB verse counts per book vs BIBLE_DATA.
- Compare sample texts: LSV from DB == LSV from prod JSON (normalized).
- Strongs roundtrip sample.
- Re-run with omissions injection.
- Add DB constraints mirroring pipeline (e.g. triggers or CHECKs for known ranges).
- Performance baseline: query time for a day load vs current JSON.
- **Tools**: Enhance `check_data_integrity.py` or new `verify_db.py` that hits both sources.
- **Deliverable**: Signed-off "data matches production + validation passes" report. Update docs.

### Phase 4: 365DBR Integration (daily experience + browser)
- Option A (low risk): Keep current static JSON serving for 365DBR. Add optional DB-backed endpoints or pre-generate enhanced JSON from DB.
- Option B: Client or thin server layer queries DB for `loadDailyBread` equivalent (return same verseMap shape initially for zero frontend break).
- Respect 365DBR_AGENTS.md: any change to data shape for audio/playVerse must be verified.
- Add features powered by DB early: e.g. "show Strong's for this verse", "search strong H1234 across plan", speaker filter (once annotations seeded).
- Update compile_site.py / static generation if needed to pull from DB.
- **Constraint**: Daily reading must remain functional and fast throughout. Audio, navigation, focus, accessibility unchanged or improved.
- **DEV scope**: Small, reviewable increments. Always test with prod data dates.

### Phase 5: Rich Metadata & S.I. Enablement
- Curate / import annotations (speakers, chronology, themes, cross-refs).
  - Start small: obvious cases (e.g. "Jesus" for direct quotes in Gospels via known ranges; "God" for "And God said"; Psalm attributions from headings).
  - Sources: public domain cross-ref collections, manual review against literal text (primary = Bible), verified wisdom after Tier 1.
  - Store in annotations + cross_references.
- Add more translations (LSB when available: new fetch parallel + alignment check + populate).
- Literary units, setting, audience.
- Expose advanced queries (SQL views + later S.I. query builder).
- **Metrics**: Enable sample "Deep Thought" style queries, e.g. "list all verses where speaker=Jesus containing strong for 'love' or theme mercy".

### Phase 6: Cutover, Deprecation, Ops
- Switch primary source to DB for new S.I. components.
- Maintain static snapshots or JSON export for 365DBR compatibility / offline / crawlers as needed.
- Backup strategy, read replicas if scale.
- Monitoring for data drift (if pipeline continues).
- Deprecate old JSON writes after confidence high.
- Full audit log / provenance for every token/text.

## ETL Design Sketch (Key Implementation Notes for DEV)

- Prefer production HTTPS fetches (with caching of fetched JSONs locally for re-runs).
- Or: one-time mirror of relevant prod data/ folders into a controlled `data/prod-snapshots/` (never commit full Bible text to git? – follow existing patterns; repo already has some).
- Parsing: reuse/port `walkItems` or `processContent` logic from index.html + bible_common. **Branch on bibleId or testament**:
  - Hebrew (OT/PSA/PRO): walk for `char` with `strong`, extract per-word tokens + surface.
  - Greek (NT): extract running text; split to tokens on whitespace/punct for surface (strongs typically absent in current SBLGNT source data). See Database-Schema.md "OT vs NT / Hebrew vs Greek Specifics".
- For verse text in translations: join with appropriate separator (space for English, '' for original).
- Idempotent: use UPSERT (ON CONFLICT) so re-runs are safe.
- Transactions per logical unit (day or book).
- Logging + dry-run mode.
- Example flow pseudocode:
  ```
  for day in targets:
      manifest = fetch_prod(f".../data/{day}/manifest.json")
      for f in manifest.files:
          raw = fetch_prod(...)
          validate(raw)
          for vid in extract_verse_ids(...):
              ensure_verse(vid)
          insert_tokens_from_content(raw.data.content, 'hebrew' or 'greek')
          for par in parallels:
              insert_translation_text(par, matched_trans)
      insert_daily_from_plan(day)
  ```

## Risks, Blockers & Mitigations

- **Data access (LSB)**: Pending LLC clarification from 316 Publishing. Mitigation: design schema to accept new bibleIds easily; populate LSV/KJV first. LSB blocked until resolved.
- **Alignment drift**: New translations or variants may have verse differences. Mitigation: strict validation + separate alignment table later.
- **Rich metadata quality**: Speaker/setting attribution is interpretive. Mitigation: source field, multiple possible values, Tier 1 priority (always show the actual text + attribution as derived). Bible text never altered.
- **Volume / perf**: ~365*avg ~150 verses/day * words/verse + tokens = manageable (< few million rows). PG handles easily.
- **Frontend coupling**: verseMap flattening + audio. Mitigation: keep output shape compatible; verify with Playwright/tests per AGENTS.md.
- **Hosting / CSP / shared env**: Other apps constraints. DB access via backend API layer later if client-only model changes.
- **Past notes lost**: Starting fresh – this plan + schema are the record. Update iteratively.
- **Git / worktree**: Always check status. Changes only in scoped PRs.

## Rollback & Reproducibility

- Schema: down migrations or recreate from DDL + seeds.
- Data: re-run ETL from same prod snapshot date (record the MMDD used).
- Keep raw prod JSON mirrors for audit.
- Version everything (schema_migrations table, etl run logs in data_sources).

## Success Criteria (for this phase + overall)

- DB contains accurate LSV + original + strongs for at least one full day matching prod exactly.
- 365 plan rows + passages present and queryable.
- Sample S.I. queries possible (e.g. "verses with strong H1234 in LSV text").
- All existing validations pass in ETL.
- Documentation updated (INDEX + these files).
- DEV has clear, scoped next tasks (see Handoff section).
- No breakage to live 365DBR.

## Immediate Next Steps (as of 2026-07-01)

(See INDEX.md for the master TODO tracker.)

1. Database PM: this design complete + INDEX update.
2. Coordinate with Top-Level Program Lead: review schema/plan.
3. Hand off Phase 1 (infra + schema) to 365DBR DEV with self-contained prompt (load docs first).
4. DEV executes Phase 1; report back with verification.
5. Iterate: populate sample day(s) → validation → schema tweaks.
6. Seed initial annotations (small curated set) for S.I. demo value.
7. Expand translations when LSB access confirmed.
8. Re-document after each milestone.

**Blockers right now**: None for design/prototyping. LSB for full trans support.

**When handing off to DEV**: Provide focused prompt that instructs: read the 5 core docs + Database-Schema.md + Migration-Plan.md first, then implement only the scoped piece.

Update this file + INDEX.md after every significant step. Never repeat prior analysis here; reference.

**Last updated**: 2026-07-01 (initial high-level plan produced in dedicated DB design session).
