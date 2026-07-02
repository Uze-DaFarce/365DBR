# Organizing Knowledge from Past Agent Work (.jules)

## Background
The `.jules/` directory contains detailed journals from previous AI agent sessions (Bolt, Palette, Sentinel, etc.). These capture hard-won lessons on performance, accessibility (a11y), security, UI/UX patterns, data handling, Phaser game development, static site optimization, and more.

Agent prompts themselves are preserved in `docs/Agents/` (e.g. [Bolt-Agent-Prompt.md](Agents/Bolt-Agent-Prompt.md), [Palette-Agent-Prompt.md](Agents/Palette-Agent-Prompt.md), [Sentinel-Agent-Prompt.md](Agents/Sentinel-Agent-Prompt.md)) because many operational rules remain relevant.

These notes and prompts are valuable to avoid repeating mistakes but were previously scattered.

## Goal
Extract, organize, and reference the most relevant learnings in the centralized `docs/` so the team (human + AI) can efficiently reference them for 365DBR, S.I. development, and future projects.

## Plan (Iterative)
1. **Review Phase** (in progress):
   - `.jules/bolt.md`: Performance, optimization, React/Phaser hot paths, asset loading, memoization, DOM thrashing avoidance.
   - `.jules/palette.md`: UX, accessibility patterns (focus management, keyboard shortcuts, modals, ARIA, reduced motion, skip links, tooltips).
   - `.jules/sentinel.md`: Security (CSP, headers, input validation, game state resilience, localStorage corruption handling, robots.txt, .htaccess).
   - `.jules/leaderboard.md`: Historical game-related notes (less relevant now).

2. **Extraction & Categorization**:
   - **Shared / Cross-App**: CSP management, sub-site overrides, a11y patterns, performance principles, security hardening.
   - **365DBR Specific**: Data validation, API fetching security, React performance for Bible reader UI (verse groups, scrolling, focal state), audio playback verification.
   - **S.I. / Long-term**: Data modeling lessons, contextual handling, avoiding uniformitarian assumptions in logic.
   - **HeIsRisen / Games**: Retained in app-specific docs if needed.
   - Create tagged or sectioned references.

3. **Documentation Output**:
   - Move high-value extracts into `docs/` (e.g., `docs/Performance-Patterns.md`, `docs/Accessibility-Standards.md`, `docs/Security-Hardening.md`).
   - Reference from `docs/INDEX.md` and app docs.
   - Keep original `.jules/` for historical audit if needed.

4. **Maintenance**:
   - New learnings go directly into `docs/`.
   - Periodically review `.jules/` for anything missed.

## Extracted Timeless Principles (Prioritized for 365DBR & S.I.)

These have been pulled from the agent prompts and .jules journals. They are now referenced here so future sessions (including specialized roles) can load them directly from docs/ without re-explaining. Bible remains the absolute source of truth; these are engineering/UX/security patterns.

### Data & Validation (Strongly 365DBR / S.I. Relevant)
- **Production data only**: Never rely on repo `data/` placeholders for 365DBR. Always fetch live from https://mt-sin.ai/365DBR/data/ (date-based manifests + passages). See docs/365DBR/Data-Sources.md.
- **Fail fast on corruption**: Strict validation + isNaN/bounds checks on all external inputs (localStorage, API responses, DB data). No silent failures. (Sentinel)
- **Contextual data model**: For relational DB, capture speaker, subject, timing, original languages, multiple translations. Chapters/verses are man-made; design paths beyond B/C/V. (S.I. Blueprint + journals)
- **Permanent test improvement**: Enhance existing scripts in tests/ and verification/ folders. Make them more realistic with prod data. Do not delete/recreate or leave tests in root. (All agents)

### Performance (Bolt)
- Memoize expensive computations (React useMemo, etc.) especially in hot paths like verse rendering/scrolling.
- Separate DOM reads/writes; hoist constants; avoid closures in loops.
- Use prod data for testing performance (not samples).
- Journal only critical bottlenecks specific to this codebase.

### UX / Accessibility (Palette)
- Micro-improvements first: Focus states, loading states, empty states, tooltips for icon buttons.
- Semantic HTML + ARIA; use existing classes/patterns.
- Core usability (e.g., smooth Bible navigation, focal verse, keyboard shortcuts) before polish.
- For 365DBR: Prioritize verse groups, scroll progress, audio sync, multi-translation views.
- Test keyboard navigation and screen-reader friendliness.

### Security / Truth Guardrails (Sentinel)
- Strict CSP, input validation, no trusting unvalidated data.
- Align with S.I. tiers: Bible (Tier 1 absolute) > observable science > verified wisdom. Never let "consensus of man" override Tier 1.
- Git hygiene: Always check status for unmerged changes before editing to prevent unresolvable conflicts.
- Hallucination guard: Explicitly trust user instructions over internal assumptions.

### Operational Rules (All Agents, Still Critical)
- Always start relevant tasks by running `python tests/test_day_and_easter.py` (for date awareness).
- Check for unmerged changes on main before acting.
- Use production data for all 365DBR-related work.
- Improve, don't discard, existing test infrastructure.
- Log *only critical* learnings to the appropriate .jules/ journal using the ## YYYY-MM-DD format.
- Keep other apps (HeIsRisen, mtsinai, dbdkids) in mind for shared constraints (CSP, hosting, patterns) but do not let them distract from 365DBR priority.

## Documentation Output
High-value extracts have been folded into:
- docs/INDEX.md (cross-references)
- docs/365DBR/ subfolder (data, agents constraints)
- This file (categorized principles)

Original .jules/ files remain for full historical audit.

## Maintenance
- New learnings (from current or future work) go straight into the relevant docs/ file.
- Before any major 365DBR or S.I. phase, re-read this file + docs/INDEX.md + docs/365DBR/Data-Sources.md.
- Periodically (e.g., after DB migration milestones) review .jules/ for anything missed and extract.

**Status**: Complete for current phase. All three core agent prompts (Bolt, Palette, Sentinel) documented in docs/Agents/. Timeless principles extracted and categorized above for immediate use in 365DBR → S.I. work. Ready to hand off to specialized sessions. 

Other .md files (README.md, HeIsRisen docs, etc.) are retained as-is for awareness but deprioritized per 100% 365DBR focus.