# Scriptural Intelligence (S.I.) — Architecture & Tier 1 Specification
**Codename:** "Deep Thought"
**Last Updated:** 2026-10-26
**Priority:** Truth/Accuracy > Safety/Security > Performance ($0 Budget Constraint)

## 1. The 4-Tier Hierarchy of Reality
Every query and claim processed by S.I. is evaluated through a strict descending filter:

1. **TIER 1: The Absolute (The 66 Books of Scripture)**
   * **Engine Core:** Original Hebrew (WLC) and Greek (Textus Receptus / GRCTR), supported by royalty-free literal English translations (KJV, LSV, YLT).
   * **Rule:** God cannot lie; His Word is the definition of reality. Any human claim contradicting Tier 1 is rejected.
   * **Licensing Separation:** Non-commercial translations (e.g., LSB) and modern display translations (e.g., WEB) are flagged as `display_only` in the database so the core S.I. reasoning engine remains 100% commercially unencumbered and free of translator drift.
2. **TIER 2: Observable Reality (Physical Laws & Verified History)**
   * **Operational Science:** Repeatable, testable physical laws in the present (Thermodynamics/Entropy from the Fall, Biogenesis, Information Theory) strictly separated from uniformitarian historical speculation.
   * **Verified Archaeology/History:** Hard physical discoveries confirming Biblical history (e.g., Tel Dan Stele, Hezekiah/Isaiah bullae, Dead Sea Scrolls, Pilate Stone) locked in the local DB.
3. **TIER 3: Verified Wisdom (Vetted Apologetics & Models)**
   * **Sources:** Decades-tested Protestant creationist and apologetic works (e.g., Answers in Genesis, ICR, C.S. Lewis) providing models that align Tier 1 and Tier 2 (e.g., Catastrophic Plate Tectonics during the global Flood, ~6,000-year timeline).
4. **TIER 4: Trusted Live Domains (Whitelisted External Discovery)**
   * **Sources:** Strictly whitelisted domains (e.g., `answersingenesis.org`) queried for new archaeological or scientific findings not yet locked into Tiers 2–3.
   * *Fallback:* Anything outside Tiers 1–4 is flagged explicitly as **"Man's Opinion / Speculative."**

## 2. The 4-Pillar Ecosystem & Immutable Compilation
Because God's Word never changes, S.I. turns the GoDaddy shared hosting freeze into a security advantage:
* **Pillar 1 — The Vault (Local Docker Postgres 16 + Local API `:8765`):** Air-gapped local workshop storing the relational database, SHA-256 row/table integrity hashes, and static export compilers.
* **Pillar 2 — `365DBR`:** Independent daily reader (`index.html`, `bible.html`, `ws/`) consuming pre-compiled static JSON and Word Study shards from The Vault.
* **Pillar 3 — `What_We_Know.html`:** 40-point doctrinal framework used as an **output benchmark** (S.I. must independently prove/validate these 40 points from Tier 1; it is never used as a Tier 1 input).
* **Pillar 4 — `S.I.` Engine & Agent:** Deterministic 4-Tier + 7-Checks logic gate sitting over The Vault, using LLM compute strictly as a natural-language parser.

## 3. Tier 1 Data Sources & 4-Gate Zero-Corruption Verification
* **Local Raw USX Baseline (`apps/365DBR/RAW/`):**
  * `HEB_WLC` (UBS Westminster Leningrad Codex)
  * `GRCTR` (eBible Greek Textus Receptus — Elzevir/Scrivener/Stephanus)
  * `WEB` (eBible World English Bible — filtered strictly to the 66 canonical books in `bible_common.BIBLE_DATA`, rejecting all Apocrypha/Deuterocanon files)
* **Open-Source Linguistic Augmentation ($0, CC-BY 4.0 / Public Domain):**
  * `STEPBible-Data` (`TAHOT` Hebrew OT & `TAGNT` Greek TR NT) + `OpenScriptures/morphhb` for 100% `Hxxxx`/`Gxxxx` Strong's numbers, root lemmas, Robinson morphology, and KJV English word-level hover alignment.
* **4-Gate Verification Before DB Commit:**
  1. **Canonical Inventory Match:** Must match the 66 books and verse inventory of `BIBLE_DATA` (zero Critical Text omissions).
  2. **Surface Character Diff:** Strip cantillation/punctuation in memory and verify 100% word-for-word match between external tagged tokens and official `RAW/` USX + existing Postgres text.
  3. **Tag Completeness:** 100% valid `Hxxxx`/`Gxxxx` and morphology codes on substantive words.
  4. **Cryptographic Lock:** Compute and store `SHA-256` hashes per verse and translation.

## 4. Tier 1 Deterministic Retrieval, Scoring & Context Validation
Every prompt is evaluated through a deterministic PostgreSQL cascade before any AI summary:
1. **5-Stage Retrieval Cascade:**
   * *Pass 1:* Exact phrase + Original Lemma sequence match (`phraseto_tsquery` + `original_tokens`).
   * *Pass 2:* Pericope-bounded `AND` (co-occurrence within the same literary unit, not just single BCV).
   * *Pass 3:* Cross-Testament Bridge (`Hxxxx` ↔ `Gxxxx` via Level 1A explicit OT/NT quotes and Level 1B LXX/root equivalents; TSK-1834 kept strictly at Level 3).
   * *Pass 4:* Weighted Boolean `OR` fallback.
2. **Hermeneutical & Context Validators (`annotations` metadata):**
   * **Speaker Authority Tier:** `1.0` (God, Jesus, Holy Spirit, inspired Prophet/Apostle doctrine) vs. `0.5` (descriptive human speech) vs. `0.0 / WARNING` (Satan, demons, Job's friends, scoffers — *never cited as doctrinal truth*).
   * **Genre & Speech Mode:** Distinguishes Prescriptive Command/Doctrine from Descriptive Narrative (recording human sin without approving it), Poetry/Metaphor/Anthropomorphism, and Apocalyptic Symbolism.
   * **Covenant & Audience Scope:** Distinguishes Universal Moral Law (`EXO.20`) and New Covenant commands from temporary/fulfilled Mosaic Civil/Ceremonial laws or one-time historical commands.
   * **Grammatical Polarity & Coreference:** Preserves Hebrew/Greek negation (`lo`/`ou`/`me`) and conditional (`if`/`ean`) particles, and resolves pericope pronouns to their antecedent subjects.
   * **Mandatory Pericope Expansion:** Always retrieves the surrounding literary unit (±3 verses minimum) to prevent proof-texting out of context.


---

## Production Status Update (2026-10-28 — Stages 1–3 Complete)
- **Authoritative Database (`mt_sinai_365dbr`):**
  - `verses`: `31,102` canonical rows (`LUK.17.37`, `ACT.15.41`, `ACT.24.27` restored; bogus `REV.12.18` removed).
  - `verse_translations`: `155,510` rows (`LSB`, `LSV`, `KJV`, `WEB`, `YLT` x `31,102`) with SHA-256 verification (`text_sha256`).
  - `original_tokens`: `439,531` rows (`299,420` Hebrew WLC + `140,111` Greek TR) with 100% normalized Strong's (`strong_norm`).
  - `strongs_lexicon`: `22,716` entries (`11,681` Hebrew `TBESH` + `11,035` Greek `TBESG`), 100% token join coverage.
  - `verse_alignments`: `31,102` rows; `data_sources`: `7` registered corpora; `schema_migrations`: `001` through `007` applied.
  - Views: `v_interlinear_tokens` and `v_daily_reading_verses`.
- **GoDaddy Static Hosting & S.I. Architecture Alignment:**
  - GoDaddy static hosting is **not** a blocker for S.I. development. The local PostgreSQL database serves as the Tier-1 S.I. Master Spine and compiles deterministic static JSON packs (`apps/365DBR/data/<MMDD>/canonical_map.json` and `apps/365DBR/ws/{verse,strong}/*.json`) for $0 static hosting while Tier-1/2/3 S.I. engineering proceeds locally.
- **Monthly `api.bible` Refresh Workflow:**
  - Rather than overwriting `canonical_map.json` from scratch with the legacy `fetch_readings.py -> inject_lsb.py -> compile_site.py` chain, monthly `api.bible` refreshes update cached `api.bible` translations in Postgres (`verse_translations` with SHA-256 comparison) and re-run the DB+AST static exporter so all 5 English translations (`LSB`, `KJV`, `LSV`, `WEB`, `YLT`) and `HEB`/`GRK` data remain intact.
