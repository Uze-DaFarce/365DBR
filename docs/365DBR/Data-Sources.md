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

## Original-language sources (api.bible — used by local fetch pipeline)

| Role | Edition | api.bible id |
|------|---------|--------------|
| OT original | Westminster Leningrad Codex (hboWLC) | `0b262f1ed7f084a6-01` |
| NT original | **Greek Textus Receptus (GRCTR)** | `3aefb10641485092-01` |
| English | KJV, LSV (parallels) | `de4e12af7f28f599-01`, `01b29f4b342acc35-01` |

**Changed**: NT primary switched from critical Greek (SBLGNT-class `7644de2e4c5188e5-01`) to **GRCTR** for truth/alignment with KJV verse inventory and S.I. integrity. Constants live in `apps/365DBR/bible_common.py` (`NT_GREEK_ID`, `OT_HEBREW_ID`).

**Last documented**: 2026-07-02 (GRCTR switch)

See also: docs/INDEX.md (365DBR section) and the relational DB migration plans.