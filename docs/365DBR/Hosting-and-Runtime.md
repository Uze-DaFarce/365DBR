# 365DBR Hosting and Runtime (canonical freeze)

**Frozen**: 2026-08-26  
**Priority**: Truth/Accuracy > Safety > Performance. Bible is Tier-1 truth.

This file is the single source of truth for **where 365DBR actually runs**. Other docs should reference it rather than re-arguing hosting.

---

## Locked decision

**The public site never has a database.** Security is the reason. The database stays on this machine. Work here writes a cache of static files, and those files are what move to production. Faster pages are a side effect of that cache.

The public host is GoDaddy shared hosting (FTP + static files + CSP on `mt-sin.ai`). That plan also cannot run PostgreSQL, a persistent Python process, or a public query API. A future host that could run a database still serves the exported cache. The Bible database stays off the public site.

Local Docker Postgres remains the **authoring, verification, and export** tool.

---

## Why not “just use the database on GoDaddy”

| Idea | Why it is not a path |
|------|----------------------|
| PostgreSQL on shared hosting | Not available. Shared FTP/cPanel does not run our Docker/Postgres 16 stack. |
| cPanel MySQL / MariaDB | **Rejected.** This schema needs PostgreSQL (trigram, tsvector, JSONB, `verse_order` ranges, Hebrew/Greek tokens). Do not port the Bible DB to MySQL to fit the host. |
| Live query API (`serve_query_api.py`) on the host | Needs a long-running process + HTTPS + CSP `connect-src`. Shared hosting does not provide that. Production CSP already blocks `127.0.0.1`. |
| Paid VPS / managed Postgres (~$5–12/mo) | Still serves the exported cache. A live Bible database on the public site stays closed. Do not wait on a new host to ship reader improvements. |
| Option B (`loadDailyBread` from DB) | Would read a database from the public page. Closed. The page reads the exported day pack. |

---

## What production *is* (today)

Public site: `https://mt-sin.ai/365DBR/`

| Surface | Runtime |
|---------|---------|
| Daily reader (`index.html`) | Static JSON from `/365DBR/data/MMDD/` |
| Bible browser (`bible.html`) | Same static JSON / same-origin files |
| Word study (Aa) | Static same-origin packs `/365DBR/ws/` (`manifest.json`, `verse/{BOOK}.json`, `strong/{H####}.json`) |
| Crawler snapshots | Static `data/MMDD/index.html` |

No cloud database. No localhost probe on production (CSP-safe).

**Publish path**: generate on the PC (Docker Postgres + Python) → static files in `apps/365DBR/` → GoDaddy `/public_html/365DBR/`.

After a full upload is already on the server, later publishes use `scripts/publish_365dbr.ps1`. Run `-Init` once so the script records what is already online. Later runs zip only changed public files (`index.html`, `bible.html`, `bible_meta.js`, `strongs_optional.js`, `sitemap.xml`, `What_We_Know.html`, `data/`, `ws/`). Upload that one zip into `/public_html/365DBR/` and extract it there. The script does not upload `RAW/`, `LSB/`, Python, or tests.

---

## What local Docker Postgres *is* (today)

On the owner’s PC only (`docker compose up -d`):

- Schema + full 365 ETL + verification (Phases 1–3 **done**)
- Query CLI / local API on `127.0.0.1:8765` (Phase 4 Option A **done**)
- Curated annotations for S.I. prototypes (Phase 5 **minimal done**)
- **Export** of Word study JSON (`export_word_study_static.py`) for the public site

Local Postgres is how we keep the text honest and then **freeze results into files** the shared host can serve.

---

## What this freeze does *not* cancel

- Local DB work that improves **accuracy**, then re-export static files
- Static UI polish (titles, Word study, accessibility) that ships as HTML/JS/JSON
- Expanding curated annotations **locally**, then exporting anything the static packs can carry
- Free/open English↔token alignment **research** (no paid reverse-interlinear budget)
- The long-term S.I. vision stays on this machine. What the public site receives is still a cache of files.

---

## When hosting can change (later)

Revisit Option B / public API / dual-write **only after** all of:

1. Owner can pay for a host that runs PostgreSQL (or equivalent managed Postgres) with HTTPS
2. CSP `connect-src` on `mt-sin.ai` allowlists that API if the client calls it
3. AGENTS.md verification: `loadDailyBread` / `verseMap` / `playVerse` / audio still correct

Until then, agents must **not** treat “move 365DBR onto a database” as the next increment.

---

**Bible is primary. Static files on GoDaddy are the public product. Local Postgres is the workshop.**
