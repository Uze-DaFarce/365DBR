# Static Word study packs (`ws/`)

**Purpose:** Publish original-token + Strong’s Word study on GoDaddy shared hosting **without** a live database or paid API.

GoDaddy shared hosting **cannot** run PostgreSQL or `serve_query_api.py`. These files *are* the public Word study runtime. Do not replace them with a live DB on this host. See `docs/365DBR/Hosting-and-Runtime.md`.

## Generate (on your PC)

```powershell
cd "D:\Users\uzeda\Mt. Sinai LLC\monorepo"
docker compose up -d
python db/scripts/export_word_study_static.py
```

Creates (gitignored except this README):

- `manifest.json` — feature-detect
- `verse/GEN.json`, `verse/MAT.json`, … — per-book verse payloads
- `strong/H430.json`, … — capped Strong’s hit lists

## Publish

FTP the entire `ws/` folder next to `index.html` / `bible.html`:

`https://mt-sin.ai/365DBR/ws/manifest.json`

CSP `connect-src 'self'` allows same-origin fetches. No localhost probe on production.

## Local

`strongs_optional.js` prefers live `http://127.0.0.1:8765` on localhost when up; otherwise uses `./ws/`.
