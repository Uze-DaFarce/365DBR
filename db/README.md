# 365DBR Local Database Development (Phase 1)

**Priority order (per team guidance)**: Truth/Accuracy > Safety/Security > Performance.

This setup provides a reproducible local PostgreSQL 16 environment for the v0.1 schema defined in:

- `docs/365DBR/Database-Schema.md`
- `docs/365DBR/Migration-Plan.md`
- `docs/Roles/365DBR-DEV.md`

**Never use repo `apps/365DBR/data/` for real work.** Only `https://mt-sin.ai/365DBR/data/` is authoritative.

## Recommended Environment (BEST for accuracy & reproducibility)

Use **Docker** + the provided `docker-compose.yml` (at monorepo root). 

**Why Docker is best here**:
- Exact `postgres:16` image (matches design).
- Isolated, version-pinned, easy full reset (`docker compose down -v`).
- Persistent named volume for dev data across container restarts.
- Same behavior on Windows, macOS, Linux, CI.
- Easy to add future services (API, etc.).

### 1. Install Docker (if not present)

On Windows:
1. Download and install **Docker Desktop** from https://www.docker.com/products/docker-desktop/
2. Start Docker Desktop and wait for it to say "Engine running".
3. Open PowerShell (or the terminal you use) and verify:

```powershell
docker --version
docker compose version
```

If commands are not found, restart your terminal / computer after install.

### 2. Start Postgres

From the monorepo root:

```powershell
# Start in background
docker compose up -d

# Check health
docker compose ps
docker compose logs postgres --tail 20
```

The service exposes port 5432 on localhost.

To stop (data is kept in volume):

```powershell
docker compose down
```

To **completely reset** (delete all data — useful for clean re-testing of schema):

```powershell
docker compose down -v
docker compose up -d
```

### 3. Configure connection

Copy the example and customize (use a strong password for local dev):

```powershell
cd db
copy .env.example .env
# Then edit .env with your editor (VS Code, notepad, etc.)
```

Recommended `.env` (example):

```
POSTGRES_DB=mt_sinai_365dbr
POSTGRES_USER=365dbr_dev
POSTGRES_PASSWORD=UseAStrongLocalDevPasswordHere123!
POSTGRES_PORT=5432

DATABASE_URL=postgresql://365dbr_dev:UseAStrongLocalDevPasswordHere123!@localhost:5432/mt_sinai_365dbr
```

> Note: The password in the example file is a placeholder. Change it.

You can also set the `DATABASE_URL` (or individual vars) directly in your shell session without a `.env` file.

### 4. Install Python dependencies (once)

```powershell
cd db
pip install -r requirements.txt
```

`psycopg[binary]` is used so it works cleanly on Windows without a C compiler.

### 5. Apply schema + seed

```powershell
# From the monorepo root or db/ dir
python db/scripts/apply_migrations.py

# Seed the 66 books from the canonical source of truth
python db/scripts/seed_books.py
```

### 6. Verify (required)

```powershell
python db/scripts/verify_schema.py
```

Expected: All `[PASS]` checks, 66 books, LSV+ KJV translations, sample Hebrew + Greek verse inserts succeed.

If any FAIL, stop and investigate — accuracy is non-negotiable.

### 7. Useful commands

Inspect the DB:

```powershell
# Using docker
docker compose exec postgres psql -U 365dbr_dev -d mt_sinai_365dbr -c "\dt"
docker compose exec postgres psql -U 365dbr_dev -d mt_sinai_365dbr -c "SELECT code, name, testament, num_chapters FROM books ORDER BY order_canonical LIMIT 10;"

# Using psql directly (if in PATH after native install or Docker tools)
psql "postgresql://365dbr_dev:xxx@localhost:5432/mt_sinai_365dbr" -c "SELECT count(*) FROM books;"
```

Reset everything and start over (during dev):

```powershell
docker compose down -v
docker compose up -d
python db/scripts/apply_migrations.py
python db/scripts/seed_books.py
python db/scripts/verify_schema.py
```

## Alternative: Native Postgres (no Docker)

If you prefer not to use Docker:

1. Download the official PostgreSQL 16 installer for Windows: https://www.postgresql.org/download/windows/
2. Install (note the password you set for the `postgres` superuser).
3. Use pgAdmin or `psql` (from the install's bin folder) to create the database and user:

```sql
CREATE DATABASE mt_sinai_365dbr;
CREATE USER 365dbr_dev WITH PASSWORD 'your_strong_dev_password';
GRANT ALL PRIVILEGES ON DATABASE mt_sinai_365dbr TO 365dbr_dev;
```

4. Set `DATABASE_URL` or component env vars to point at your local server (usually port 5432).
5. Run the same `apply_migrations.py`, `seed_books.py`, and `verify_schema.py`.

Docker remains the **recommended** path for consistency with the project.

## Connection string formats

Scripts accept either:

- `DATABASE_URL=postgresql://user:pass@localhost:5432/mt_sinai_365dbr`
- Individual vars (`POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.)

psycopg 3 handles the URL natively.

## Migrations philosophy (Phase 1+)

- Plain, numbered `.sql` files live in `db/migrations/`.
- Each file is fully reviewable and auditable.
- The Python applier (`apply_migrations.py`) is intentionally minimal.
- `schema_migrations` table tracks what has run.
- Later phases may introduce Alembic if the migration surface grows significantly. For now this is the cleanest, lowest-dependency approach.

## What Phase 1 delivers

- Reproducible Postgres 16.
- Exact v0.1 schema from `Database-Schema.md`.
- Accurate seeding of all 66 books (single source of truth = `bible_common.py`).
- LSV (primary) + KJV translations.
- Basic indexes + tsvector + trigram readiness.
- Verification that proves the foundation is correct.

## Phase 2: Populate sample days (ETL)

After Phase 1 (schema + seeds), load real day packs into the DB.

**Preferred source:** local `apps/365DBR/data/MMDD/` after a verified `fetch_readings.py` run (GRCTR Greek + WLC Hebrew).  
**Fallback:** `--source prod` pulls `https://mt-sin.ai/365DBR/data/MMDD/` (may lag behind local until you FTP).

```powershell
# From monorepo root (quote days so PowerShell keeps leading zeros)
python db/scripts/populate_day.py --day "0123" --source local
python db/scripts/verify_population.py --day "0123" --source local

# Multiple days
python db/scripts/populate_day.py --day "0123,0702,0823" --source local
python db/scripts/verify_population.py --day "0123,0702,0823" --source local

# All 365 days (local packs; no api.bible cost)
python db/scripts/populate_day.py --all --source local --continue-on-error
python db/scripts/verify_population.py --day "0101,0702,1225" --source local
# optional full verify (slower):
# python db/scripts/verify_population.py --all --source local
```

What is loaded per day:
- `verses` for all BCV ids in the pack
- `original_tokens` (Hebrew + Strong's; Greek surface words from GRCTR)
- `verse_translations` (LSV + KJV)
- `daily_readings` + `daily_passages` (4 sections)
- `data_sources` provenance rows

Scripts:
- `db/etl/parse_passage.py` — JSON walkers
- `db/scripts/populate_day.py` — load
- `db/scripts/verify_population.py` — compare DB to source JSON (fail on mismatch)

## Phase 3: Full DB reconciliation

```powershell
python db/scripts/verify_db.py
python db/scripts/verify_db.py --json-spot-days "0101,0702,1225"
```

Checks book-level counts vs `bible_common.BIBLE_DATA`, plan coverage, TR samples, Strong's, performance, S.I. smoke queries.

## Phase 4: Optional DB query layer (static JSON remains primary)

**Constraint**: Live `index.html` / `bible.html` still load day packs from static JSON.
This layer does **not** change `loadDailyBread` / `verseMap` / `playVerse`.

```powershell
# Day pack from DB (verseMap-compatible; use --compact for summary)
python db/scripts/query_db.py day --day "0101" --compact

# Single verse + Strong's tokens
python db/scripts/query_db.py verse --id GEN.1.1

# Strong's search (H430 = Elohim)
python db/scripts/query_db.py strong --num H430 --limit 10 --compact

# Dual-read: local JSON pack English vs DB (fail on mismatch)
python db/scripts/query_db.py dual-read --day "0101,0702,1225" --source local

# Smoke tests (requires populated DB)
python db/scripts/test_query_phase4.py
```

Library: `db/query/` (`load_day`, `load_verse`, `search_strong`, `dual_read_day`).

## Next after Phase 4

- Optional: thin HTTP API or UI Strong's tooltip (still non-primary)
- Option B only if small + AGENTS verified (`loadDailyBread` from DB)
- Phase 5: annotations / S.I. metadata
- Keep static JSON pipeline working until dual-write / cutover

## Troubleshooting

- Connection refused → Docker not running or port conflict. Check `docker compose ps`.
- Authentication failed → Password mismatch in `.env` vs what was used when container first started. Use `docker compose down -v` + recreate.
- Book count wrong → Re-run `seed_books.py`. It is idempotent.
- Import errors for bible_common → Run the script with CWD at monorepo root or ensure PYTHONPATH.

## References

- `docs/Roles/365DBR-DEV.md`
- `docs/365DBR/Database-Schema.md`
- `docs/365DBR/Migration-Plan.md`
- `docs/365DBR/Data-Sources.md`
- `apps/365DBR/bible_common.py`

Bible text is primary. All code serves faithful representation of it.
