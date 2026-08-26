# Word Study & English↔Original Alignment

**Status**: Word study UI **enabled** from local query API (localhost `/health`) **or** static same-origin `ws/` packs on production.  
**Priority**: Truth/Accuracy > Safety > Performance.  
**Hosting freeze (2026-08-26)**: Public Word study **must** stay static `ws/` files. GoDaddy shared hosting cannot run Postgres or the query API. Do not wait on a VPS. Canonical: `docs/365DBR/Hosting-and-Runtime.md`.  
**Owner note (2026-07-28)**: Keep current original-first Word study available; **improve toward English-word hover when possible without paid data/licenses** (no budget for commercial reverse interlinears).

---

## What ships today (correct for current data)

| Capability | Status |
|------------|--------|
| Feature-detect live API on **localhost** (`http://127.0.0.1:8765`) | Yes |
| **Static same-origin** packs `ws/` on production (GoDaddy, $0) | Yes — `manifest.json` + `verse/{BOOK}.json` + `strong/{H430}.json` |
| Production: no localhost probe (CSP-safe); falls back to `ws/` | Yes |
| Override live API: `?queryApi=` / `localStorage 365dbr_query_api` | Yes (must be in host CSP `connect-src`) |
| Word study control when probe succeeds | **On** (no separate opt-in flag) |
| Interactive **original** tokens + Strong’s search | Yes (OT Hebrew Strong’s present; Greek often surface-only) |
| Human verse refs (`2 Kings 10:17`) | Yes |
| Hover **English** word → original + Strong’s for *that* word | **Not yet** — no honest EN↔token map in DB |

### Publish static Word study (GoDaddy)

```powershell
python db/scripts/export_word_study_static.py
# FTP apps/365DBR/ws/ + strongs_optional.js to /365DBR/ on host
```

See `apps/365DBR/ws/README.md`.

**Data we have:**

- `original_tokens`: ordered original words + Strong’s (where source provides them)
- `verse_translations`: **whole-verse** LSV/KJV strings
- `verse_alignments`: English BCV ↔ org BCV (`verseOrgIds`) — verse-level, not word-level

**Data we do not invent:** English word index/span ↔ original token (would be a guess).

Static JSON remains primary for daily reading / `playVerse`. Word study is enrichment only.

---

## Desired improvement (when free/open path exists)

**Product goal (owner):** As an English reader, hover a word in English and see/search the Strong’s number and original language for **that** word; search hits should make the English sense clear (not bare Hebrew alone).

**Constraint:** Prefer **zero-cost / open-license** sources. Do not require commercial reverse interlinears (Logos RI packs, paid APIs, etc.) until budget allows.

### Free/open avenues to evaluate (design before code)

1. **Open scholarly corpora** (MACULA, STEPBible-class, Open Scriptures / OSHB-style tagging)  
   - Often: original + Strong’s/morph + English **gloss** per original word  
   - Gloss is honest if labeled as gloss; may not equal LSV/KJV wording  
2. **Strong’s lexicon / gloss tables** (public domain or clearly free)  
   - Improves search hits: H3427 → “sit, dwell…” + full English verse context  
   - Still not hover-on-LSV-word without alignment  
3. **api.bible / FCBH**  
   - Re-check if any free bibleId exposes word-level English↔original maps we can license at $0  
   - Current LSV/KJV parallels we use do **not** (verseId + verseOrgIds only on English text)  
4. **Manual curation** of a few demo verses with `source` provenance — free but not scalable  

### Explicit non-goals without free data

- Paid reverse interlinear purchases  
- Scraping sites that forbid bulk reuse  
- Statistical/ML “guess” alignment as silent production truth  

---

## When free alignment exists: implementation sketch

1. Table e.g. `word_alignments`  
   `(translation_id, verse_id, eng_span_or_order) → (token verse_id/order or token id, strong_number, source, confidence)`  
2. ETL from chosen open dataset; provenance on every row  
3. UI: hover English only where a row exists; fall back to today’s original-first Word study  
4. Verify hard cases (particles, multi-word EN, Psalm numbering edges)

---

## Related paths

| Path | Role |
|------|------|
| `apps/365DBR/strongs_optional.js` | Probe + fetch + formatVerseRef |
| `apps/365DBR/index.html` / `bible.html` | Word study sheet (Aa) |
| `db/scripts/serve_query_api.py` | Local API `:8765` |
| `docs/365DBR/Verse-Identity-and-Alignment.md` | Verse-level BCV identity |
| `docs/365DBR/Hosting-and-Runtime.md` | GoDaddy = static; no live DB |
| `docs/365DBR/DEV-Logs.md` | Session history |

---

**Bible is primary. Prefer free truth over expensive convenience.**
