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
