# 365DBR Hosting and Runtime (canonical freeze)

**Frozen**: 2026-08-26  
**Priority**: Truth/Accuracy > Safety > Performance. Bible is Tier-1 truth.

This file is the single source of truth for **where 365DBR actually runs**. Other docs should reference it rather than re-arguing hosting.

---

## Locked decision

**Production 365DBR cannot transition to a live relational database while it is on GoDaddy shared hosting.**

The owner can currently afford **GoDaddy shared hosting only** (FTP + static files + CSP on `mt-sin.ai`). That plan cannot run PostgreSQL, a persistent Python process, or a public query API. There is no supported way to host this Bible database on that shared host.

Until the owner finds work and can afford hosting that actually runs PostgreSQL (or a cheap VPS that does), **the public app stays static files**. Local Docker Postgres remains the **authoring, verification, and export** tool — not the public runtime.

---

## Why not “just use the database on GoDaddy”

| Idea | Why it is not a path |
|------|----------------------|
| PostgreSQL on shared hosting | Not available. Shared FTP/cPanel does not run our Docker/Postgres 16 stack. |
| cPanel MySQL / MariaDB | **Rejected.** This schema needs PostgreSQL (trigram, tsvector, JSONB, `verse_order` ranges, Hebrew/Greek tokens). Do not port the Bible DB to MySQL to fit the host. |
| Live query API (`serve_query_api.py`) on the host | Needs a long-running process + HTTPS + CSP `connect-src`. Shared hosting does not provide that. Production CSP already blocks `127.0.0.1`. |
| Paid VPS / managed Postgres (~$5–12/mo) | Correct *future* runtime. **Blocked by budget** until paid work. Do not wait on it to ship reader improvements. |
| Option B (`loadDailyBread` from DB) | Requires a live DB or API on the public host. **Blocked by this freeze.** Also still requires AGENTS audio verification if/when hosting exists. |

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

**Publish path**: generate on the PC (Docker Postgres + Python) → FTP static files to GoDaddy.

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
- The long-term S.I. vision (relational DB + Deep Thought) — that waits on **affordable hosting that can run Postgres**, not on more shared-host tricks

---

## When hosting can change (later)

Revisit Option B / public API / dual-write **only after** all of:

1. Owner can pay for a host that runs PostgreSQL (or equivalent managed Postgres) with HTTPS
2. CSP `connect-src` on `mt-sin.ai` allowlists that API if the client calls it
3. AGENTS.md verification: `loadDailyBread` / `verseMap` / `playVerse` / audio still correct

Until then, agents must **not** treat “move 365DBR onto a database” as the next increment.

---

**Bible is primary. Static files on GoDaddy are the public product. Local Postgres is the workshop.**
