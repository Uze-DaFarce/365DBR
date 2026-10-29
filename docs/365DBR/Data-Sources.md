# 365DBR Data Sources

## Critical Rule
**The real Bible data is never in the repository.** 

The folder `apps/365DBR/data/` in this repo contains **only placeholder, example, and invalid data**. It is not to be used for any real work, analysis, or database population.

## Production Data Location (Source of Truth)
All real data lives exclusively on the production site:

Base URL: `https://mt-sin.ai/365DBR/data/`

### Structure
- Data is organized by date in `MMDD` folders (e.g., `0630` for June 30).
- For any given day:
  - `manifest.json` — metadata for the day's readings.
  - One or more passage `.json` files (named by book range, e.g., `BOOK.start-BOOK.end.json`).
  - Optional `index.html` — static HTML snapshot for crawlers and AI that cannot execute JavaScript.

### Example (2026-06-30)
- Manifest: https://mt-sin.ai/365DBR/data/0630/manifest.json
- Passages:
  - https://mt-sin.ai/365DBR/data/0630/2KI.13.1-2KI.14.29.json
  - https://mt-sin.ai/365DBR/data/0630/ACT.7.7-ACT.7.27.json
  - https://mt-sin.ai/365DBR/data/0630/PSA.78.47-PSA.78.53.json
  - https://mt-sin.ai/365DBR/data/0630/PRO.16.13-PRO.16.15.json
- Static: https://mt-sin.ai/365DBR/data/0630/index.html

### Manifest Format (example)
```json
{
  "label": "2KI 13:1 – 14:29, ACT 7:7–27, PSA 78:47–53, PRO 16:13–15",
  "files": [
    "2KI.13.1-2KI.14.29.json",
    "ACT.7.7-ACT.7.27.json",
    "PSA.78.47-PSA.78.53.json",
    "PRO.16.13-PRO.16.15.json"
  ]
}
```

Each passage JSON follows the standard api.bible content structure (paragraphs, characters with Strong's numbers, verse IDs, etc.).

## Usage Rules
- **Always** fetch from the production URLs above when you need real data.
- The repo data must **never** be treated as authoritative Bible text.
- This applies to:
  - Relational database population/migration
  - S.I. (Scriptural Intelligence) data ingestion
  - Analysis, testing, or verification
  - Any feature that displays or processes actual scripture

## Relation to 365DBR App
- The interactive app (`/365DBR/index.html` and `/bible.html`) loads from these prod data endpoints (or compiled static versions).
- The static `data/MMDD/index.html` versions are specifically for search engines and AI crawlers.
- **Production runtime is these static files on GoDaddy.** There is no live database behind `mt-sin.ai`. Local Docker Postgres is populated *from* this production JSON (or local mirrors of it) and can **export** Word study packs (`ws/`) back to the same host. See `docs/365DBR/Hosting-and-Runtime.md`.

## Original-language sources (api.bible — used by local fetch pipeline)

| Role | Edition | api.bible id |
|------|---------|--------------|
| OT original | Westminster Leningrad Codex (hboWLC) | `0b262f1ed7f084a6-01` |
| NT original | **Greek Textus Receptus (GRCTR)** | `3aefb10641485092-01` |
| English | KJV, LSV (parallels) | `de4e12af7f28f599-01`, `01b29f4b342acc35-01` |

**Changed**: NT primary switched from critical Greek (SBLGNT-class `7644de2e4c5188e5-01`) to **GRCTR** for truth/alignment with KJV verse inventory and S.I. integrity. Constants live in `apps/365DBR/bible_common.py` (`NT_GREEK_ID`, `OT_HEBREW_ID`).

**Last documented**: 2026-08-26 (hosting freeze: production remains these static URLs; local DB is not the public source)

See also: `docs/INDEX.md` (365DBR section), `docs/365DBR/Hosting-and-Runtime.md`, and the relational DB migration plans (local workshop only until paid Postgres hosting).


---

## Production Status Update (2026-10-28 — Stages 1–3 Complete)
- **Authoritative Database (`mt_sinai_365dbr`):**
  - `verses`: `31,102` canonical rows (`LUK.17.37`, `ACT.15.41`, `ACT.24.27` restored; bogus `REV.12.18` removed).
  - `verse_translations`: `155,510` rows (`LSB`, `LSV`, `KJV`, `WEB`, `YLT` x `31,102`) with SHA-256 verification (`text_sha256`).
  - `original_tokens`: `439,531` rows (`299,420` Hebrew WLC + `140,111` Greek TR) there is no strong_norm column, Greek strong_number is not certified, and KJV/LSV verse text now comes from the eBible zips above. Point the Strong’s path at apps/365DBR/RAW/STEPBible/Translators Amalgamated OT+NT/.
  - `strongs_lexicon`: `22,716` entries (`11,681` Hebrew `TBESH` + `11,035` Greek `TBESG`), 100% token join coverage.
  - `verse_alignments`: `31,102` rows; `data_sources`: `7` registered corpora; `schema_migrations`: `001` through `007` applied.
  - Views: `v_interlinear_tokens` and `v_daily_reading_verses`.
- **GoDaddy Static Hosting & S.I. Architecture Alignment:**
  - GoDaddy static hosting is **not** a blocker for S.I. development. The local PostgreSQL database serves as the Tier-1 S.I. Master Spine and compiles deterministic static JSON packs (`apps/365DBR/data/<MMDD>/canonical_map.json` and `apps/365DBR/ws/{verse,strong}/*.json`) for $0 static hosting while Tier-1/2/3 S.I. engineering proceeds locally.
- **Monthly `api.bible` Refresh Workflow:**
  - Rather than overwriting `canonical_map.json` from scratch with the legacy `fetch_readings.py -> inject_lsb.py -> compile_site.py` chain, there is no strong_norm column, Greek strong_number is not certified, and KJV/LSV verse text now comes from the eBible zips above. Point the Strong’s path at apps/365DBR/RAW/STEPBible/Translators Amalgamated OT+NT/ and re-run the DB+AST static exporter so all 5 English translations (`LSB`, `KJV`, `LSV`, `WEB`, `YLT`) and `HEB`/`GRK` data remain intact.
