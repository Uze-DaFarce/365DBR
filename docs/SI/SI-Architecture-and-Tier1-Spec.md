# Scriptural Intelligence (S.I.) — Architecture & Tier 1 Specification
**Codename:** "Deep Thought"
**Last Updated:** 2026-11-25
**Priority:** Truth/Accuracy > Safety/Security > Performance ($0 Budget Constraint)

## Locked contract (2026-11-16)

This section was added because the second logic layer lived only in memory, and a long 365DBR session was mistaken for S.I. itself. It does not replace the blueprint or sections 1–4 below. If a later edit conflicts with this section, stop and reconcile it here in writing. Do not rename a term in conversation only.

### What S.I. is

S.I. is the library. The Word of God is its language. The four tiers in section 1 are the only sources it may read, in that order. The blueprint's three tiers, plus the leftover label "Man's Opinion," are the earlier form of that list. Do not collapse this spec back to three tiers. Do not add a tier for a neural model.

365DBR is the first application that reads the literal text this library required. It is Pillar 2. Work on the reader, the word-study panel, or a Strong's label is 365DBR work. It is not a session of building the engine.

The vault is Pillar 1 and stays on this machine. Production receives a read-only static copy and has no write path back into the vault. That stops the live site from changing the text. It does not make a bad local load safe. A correction is a new local snapshot, checked, then exported.

God's Word does not change. It is a finite, verifiable, consistent, definitive authority. Consensus is irrelevant. A locked snapshot can be checked and then published with the knowledge that the text will not go out of date between the check and the publication. That is the advantage over a traditional model, which can be stale before it is shipped. Do not trade this for a live query of the workshop.

### The API

The S.I. API is not built. `db/scripts/serve_query_api.py` on `127.0.0.1:8765` is the local API. It is how this machine queries and controls the vault while the product is still being built. It stays until the snapshot can be locked. It is not the S.I. API. Do not extend it into the engine, and do not tell a later session that the API is already done.

The API, when it is built, reads a locked snapshot only. It has no path into the vault and no write path. A caller sends a question. The two logic layers run against that frozen text. The answer is the passages plus one result: Scripture speaks, Scripture contradicts this claim, or this search is silent. The answer is not a generated opinion. 365DBR keeps reading the static files directly. The API is not a new loader for the daily reader.

### The word LLM

In `docs/INDEX.md`, the primary LLM is the Word of God. That name means this library. A conventional language model is not S.I., not a tier, and not a source. Pillar 4's phrase "using LLM compute strictly as a natural-language parser" means an outside tool, if one is ever used. That tool may not supply the answer. Do not turn S.I. into a chatbot. Do not turn that outside tool into the product.

### Two logic layers

Both layers run before the tiers are allowed to answer, and both run again before an answer is allowed to leave.

1. Patricia Engler's 7 checks, as written in the blueprint. Check 7, the Biblical foundation, decides whether Tier 1 has spoken, contradicted the claim, or is silent. Do not replace these checks with a new list.
2. Bleed. A near neighbor is not the thing itself. Shared words, a nearby topic, or a later redefinition do not create a grey match. This layer was not in the files before 2026-11-16. Check 6 asks whether a definition is honest. Bleed asks whether a similar thing has been allowed to stand in for the real one. Do not merge bleed into check 6. Do not merge it into the hermeneutical validators in section 4. Those validators stay as written.

Before a hit is allowed to count, the words have to be about the same claim, not merely the same vocabulary. Before an answer is allowed to leave, the result has to be the passage's own sense. A concordance may list every place a word is written. It may not assemble those places into a new sentence and call that sentence Scripture. A term that has been turned around is not a shade of the original. "Freedom of religion" and "freedom from Christianity" share words. They are not the same claim.

Silence stops the answer. A lower tier does not fill a silent Tier 1. Man's opinion is labeled, and it is not an answer.

The written-word place list (`search_word`, `ws/word/`) is a list. It is not the bleed layer. Pass 4 of the retrieval cascade, the weighted Boolean OR, must not be built as a "close enough" match. Until bleed can reject a near neighbor, leave Pass 4 unbuilt.

### Speaker rule (2026-11-25)

Old sentence (Tier 1 loop, 2026-11-16): "The result still means the word is written, not that God said it." The code docstring says the same rule in two sentences: "The result means the word is written. It does not mean God said it." Both stay. Do not delete them and do not replace them with a shorter slogan.

Reading, confirmed 2026-11-25. The biblical writer's own words are the inspired Word of God: God said it, or God revealed that truth and the writer wrote it down. That is the default. A quoted speaker other than God is stored and attributed to that speaker. The serpent is a liar: the record of his words is inspired, and his claim is not cited as God's. "The word is written" means a concordance hit. It does not mean the speaker in that verse is God. A missing speaker annotation prints unknown. Unknown means the row is missing. It does not mean the verse is outside God's Word.

Rowley, the same day. The speaker is a liar whenever any human contradicts the Word of God in context from a sola scriptura perspective. Lying is default human behavior, but a sin from a Biblical perspective. The biblical writer who records that speech is not the liar. The speaker who contradicts is. The record stays inspired. That claim is not cited as God's. This rule is core. A lie introduced here makes the library useless.

Reason. The old sentence stays on the page because it is true, and because a later session must still see the words it is not allowed to reinterpret in private. Read alone, "not that God said it" can be taken to mean that the verse is outside God's Word, or that the speaker of a concordance hit is God. A missing speaker row can be taken the same way. Those readings are false. Either one corrupts the engine: one cites a liar as God, and the other treats the inspired record as if it were not the Word. Section 4's speaker weights stay as written. Bleed does not assign the speaker. This rule does not turn shared words into a match.

### What a later session must not do

- Do not start the vault or 365DBR over.
- Do not call the word-study panel S.I.
- Do not store a guessed Strong's number. Greek `strong_number` is not certified. There is no `strong_norm` column. The 2026-10-28 status lines that say otherwise are a withdrawn snapshot.
- Do not run the retired api.bible fetcher. KJV and LSV are the local eBible files.
- Do not use `What_We_Know.html` as a Tier 1 input. It remains an output benchmark.
- Do not let the owner or an agent rename a locked term without writing the old term, the new term, and the reason in this section. A redefinition that stays only in conversation is how bleed was lost.

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
* **Pillar 1 — The Vault (Local Docker Postgres 16):** Air-gapped local workshop storing the relational database, SHA-256 row/table integrity hashes, and static export compilers. `serve_query_api.py` on `127.0.0.1:8765` is the local API for querying this vault during the build. It is not the S.I. API. See the locked contract.
* **Pillar 2 — `365DBR`:** The first application of this library. Daily reader (`index.html`, `bible.html`, `ws/`) consuming pre-compiled static JSON and Word Study shards from The Vault. Finishing the reader is not the same work as building the engine.
* **Pillar 3 — `What_We_Know.html`:** 40-point doctrinal framework used as an **output benchmark** (S.I. must independently prove/validate these 40 points from Tier 1; it is never used as a Tier 1 input).
* **Pillar 4 — `S.I.` Engine & Agent:** Deterministic 4-tier gate plus both logic layers (the 7 checks, and bleed) sitting over The Vault. An outside language model, if one is ever used, is a parser only and is not a source. See the locked contract for the word LLM.

## 3. Tier 1 Data Sources & 4-Gate Zero-Corruption Verification
* **Local Raw USX Baseline (`apps/365DBR/RAW/`):**
  * `HEB_WLC` (UBS Westminster Leningrad Codex)
  * `GRCTR` (eBible Greek Textus Receptus — Elzevir/Scrivener/Stephanus)
  * `WEB` (eBible World English Bible — filtered strictly to the 66 canonical books in `bible_common.BIBLE_DATA`, rejecting all Apocrypha/Deuterocanon files)
* **Open-Source Linguistic Augmentation ($0, CC-BY 4.0 / Public Domain):**
  * `STEPBible-Data` (`TAHOT` Hebrew OT & `TAGNT` Greek TR NT) + `OpenScriptures/morphhb` supply Strong's tags, root lemmas, Robinson morphology, and KJV English word-level alignment. A stored number remains a source tag. It is not certified until one linked row's letters match the word and the tag is the same written tag. See `db/query/verify.py` and the locked contract.
* **4-Gate Verification Before DB Commit:**
  1. **Canonical Inventory Match:** Must match the 66 books and verse inventory of `BIBLE_DATA` (zero Critical Text omissions).
  2. **Surface Character Diff:** Strip cantillation/punctuation in memory and verify 100% word-for-word match between external tagged tokens and official `RAW/` USX + existing Postgres text.
  3. **Tag Completeness:** 100% valid `Hxxxx`/`Gxxxx` and morphology codes on substantive words. This is the standard for a future commit. The loaded Greek `strong_number` column has not passed it.
  4. **Cryptographic Lock:** Compute and store `SHA-256` hashes per verse and translation.

## 4. Tier 1 Deterministic Retrieval, Scoring & Context Validation
Every prompt is evaluated through a deterministic PostgreSQL cascade before any AI summary:
1. **5-Stage Retrieval Cascade:**
   * *Pass 1:* Exact phrase + Original Lemma sequence match (`phraseto_tsquery` + `original_tokens`).
   * *Pass 2:* Pericope-bounded `AND` (co-occurrence within the same literary unit, not just single BCV).
   * *Pass 3:* Cross-Testament Bridge (`Hxxxx` ↔ `Gxxxx` via Level 1A explicit OT/NT quotes and Level 1B LXX/root equivalents; TSK-1834 kept strictly at Level 3).
   * *Pass 4:* Weighted Boolean `OR` fallback. Leave this pass unbuilt until bleed can reject a near neighbor. It must not be implemented as a grey match. See the locked contract.
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
  - `original_tokens`: `439,531` rows (`299,420` Hebrew WLC + `140,111` Greek TR) with 100% normalized Strong's (`strong_norm`). **Withdrawn 2026-11-16:** there is no `strong_norm` column. Greek `strong_number` is not certified. Later loads changed the row counts. See `docs/365DBR/Handoff-Next-Session.md`.
  - `strongs_lexicon`: `22,716` entries (`11,681` Hebrew `TBESH` + `11,035` Greek `TBESG`), 100% token join coverage. **Withdrawn 2026-11-16:** "100% token join" is not a certification of Greek numbers.
  - `verse_alignments`: `31,102` rows; `data_sources`: `7` registered corpora; `schema_migrations`: `001` through `007` applied.
  - Views: `v_interlinear_tokens` and `v_daily_reading_verses`.
- **GoDaddy Static Hosting & S.I. Architecture Alignment:**
  - GoDaddy static hosting is **not** a blocker for S.I. development. The local PostgreSQL database serves as the Tier-1 S.I. Master Spine and compiles deterministic static JSON packs (`apps/365DBR/data/<MMDD>/canonical_map.json` and `apps/365DBR/ws/{verse,strong}/*.json`) for $0 static hosting while Tier-1/2/3 S.I. engineering proceeds locally.
- **Monthly `api.bible` Refresh Workflow:** **Withdrawn.** Do not run `apps/365DBR/reference/retired-api-bible/`. KJV and LSV are the local eBible files. The older sentence is kept so it is not revived by mistake: rather than overwriting `canonical_map.json` from scratch with the legacy `fetch_readings.py -> inject_lsb.py -> compile_site.py` chain, monthly `api.bible` refreshes were once described as updating cached translations in Postgres. That workflow is not the plan.
