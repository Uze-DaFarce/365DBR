# AGENTS.md — Mt. Sinai LLC monorepo

Owner is on a free weekly Grok token budget. Wasting tokens is failure.

## Where to work

Preferred tree: `D:\Users\uzeda\Mt. Sinai LLC\monorepo` on **main**.
Owner does not use git; agents commit and push when asked (`docs/Git-For-You.md`).
If this session is a Grok worktree, prefer the D: tree for real edits unless the user is already working here.

## 365DBR (non-negotiable)

- Bible (66 books, read contextually) is Tier-1 truth. Truth/Accuracy > Safety > Performance.
- Public site is **static files on GoDaddy** (`https://mt-sin.ai/365DBR/`). No live Postgres, no public API, no cPanel MySQL, no Option B. Canonical: `docs/365DBR/Hosting-and-Runtime.md`.
- LSB is default focal English when present in the day pack; LSV fallback. Do not add LSB to `fetch_readings.py`.
- Show real verses; never hide them. Titles live in `titles[]`, not verse bodies.
- Word study `Aa` only where Strong's exists (OT today; no NT). Do not invent EN↔Strong's maps. Do not global-wipe tokens.
- Before changing `verseMap` / `loadDailyBread` / `playVerse`, read `docs/365DBR_AGENTS.md` (audio).

## Token rules

- New **small** session per task. Do not resume 500+ message sessions to “remember.”
- Do not re-research Phases 1–3. Do not read the Blueprint, schema, or migration plan unless a design choice requires it.
- One increment, then stop. Do not explore the repo. Do not spawn extra subagents unless asked.
- Extra docs only if needed: `docs/365DBR/Handoff-Next-Session.md`, `docs/INDEX.md`.
- End of a productive small session: `/flush`. After several: `/dream`.
- PowerShell: no `&&`; quote `--day "0131"`.
