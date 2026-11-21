# AGENTS.md — Mt. Sinai LLC Monorepo

- **Branch & Tree:** Work on `main` in `D:\Users\uzeda\Mt. Sinai LLC\monorepo`.
- **Priority & Token Budget:** Truth/Accuracy > Safety > Performance. Strict token budget—one increment per small session, then stop; never resume 500+ message threads, explore the repo unasked, or spawn extra subagents.
- **Production Web Root Mapping:** Production `/public_html/` maps to `apps/mtsinai/` (NOT monorepo root). Write root `.htaccess` rules (`/fl/*` redirects, CSP headers) to `apps/mtsinai/.htaccess`.
- **Sub-App Mapping:** `apps/<app_name>/` deploys to `/public_html/<app_name>/` (`apps/foundations/` -> `/foundations/`, `apps/365DBR/` -> `/365DBR/`, `apps/HeIsRisen/` -> `/HeIsRisen/`).
- **Local Dev Server:** Run `python -m http.server 8080` from `apps/` so root-relative URLs match production.
- **Reusable Temp Files:** Reuse `temp/task.py` and `temp/out.txt` (UTF-8) for helper scripts/dumps; never invent new temp filenames.
- **User-Facing Labels:** Use "Scripture Reader" or "Verse View" in UI copy—never internal dev terms like "Drawer."
- **PowerShell & Docs:** No `&&`; quote string flags (e.g., `--day "0131"`). Read `docs/INDEX.md` only when needed.