# Mt. Sinai LLC - Monorepo

**Faith-Centered Business Services & Ethical AI**

This monorepo contains the collected source code for all of Mt. Sinai LLC's web-based ministry projects. We are dedicated to providing professional business services that honor God, specializing in ethical AI implementation, bookkeeping, web design, and application solutions.

## Mission

"Each task, even the most ordinary, is sacred when done for God. We are called to work with excellence, integrity, and devotion, knowing that Christ Himself is whom we serve as we serve our clients."

## Applications

This repository is organized into the following applications (see `docs/` for centralized, up-to-date documentation):

*   **365DBR** (`/apps/365DBR`): A structured daily Bible reading plan (<15 min/day) with advanced browser features. Foundation for Scriptural Intelligence (S.I.). See [docs/INDEX.md](docs/INDEX.md) and [docs/365DBR_AGENTS.md](docs/365DBR_AGENTS.md).
*   **HeIsRisen** (`/apps/HeIsRisen` and `/m/`): Interactive Christian Easter Egg Hunt game (desktop + mobile versions).
*   **mtsinai** (`/apps/mtsinai`): The main corporate website for Mt. Sinai LLC.
*   **dbdkids** (`/apps/dbdkids`): In development (no documentation yet).

## 365DBR

See the centralized documentation for full details:

* [docs/INDEX.md](docs/INDEX.md)
* [docs/365DBR_AGENTS.md](docs/365DBR_AGENTS.md)
* [Project Blueprint for Scriptural Intelligence (S.I.)](docs/Project%20Blueprint_%20Scriptural%20Intelligence%20(SI).md)

**Current Status (2026-06-30)**:
- Primary data via api.bible (LSV focal).
- LSB access obtained but integration pending clarification from 316 Publishing on LLC setup.
- Planned expansions: WEB (no data yet), NKJV, ESV (when accessible/affordable).
- Transitioning from static JSON to highly relational database (far beyond Book/Chapter/Verse; includes original languages, speaker/subject/timing/context, multi-translation support).
- Deployed at: https://mt-sin.ai/365DBR/ (interactive) and static data endpoints for crawlers.

**Note**: Full technical details, setup, and usage are maintained in `docs/`. The high-level overview below is intentionally brief.

### High-Level Components
- Python pipeline for plan generation and data fetching.
- React-based frontend (single-file via CDN) with advanced browser features.
- Strong focus on accessibility, performance, and Biblical fidelity.

See `docs/` for current scripts, data model, deployment details, and S.I. integration plans.

## Documentation

All shared documentation lives in the `docs/` directory at the monorepo root (centralized to reduce repetition and capture cross-app context).

* Start here: [docs/INDEX.md](docs/INDEX.md)
* 365DBR-specific constraints: [docs/365DBR_AGENTS.md](docs/365DBR_AGENTS.md)
* Scriptural Intelligence (S.I.) vision: [docs/Project Blueprint_ Scriptural Intelligence (SI).md](docs/Project%20Blueprint_%20Scriptural%20Intelligence%20(SI).md)

App-specific documentation (when it exists) will be in `docs/<app>/`.

## Contact

*   **Email**: [truth@mt-sin.ai](mailto:truth@mt-sin.ai)
*   **Phone**: (206) 718-9780
*   **Location**: Conrad, MT
