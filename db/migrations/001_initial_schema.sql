-- 001_initial_schema.sql
-- 365DBR Relational Database v0.1 (initial highly-relational schema)
--
-- EXACT implementation of the design in:
--   docs/365DBR/Database-Schema.md
--
-- Principles (non-negotiable):
--   * The 66 books of Scripture are Tier 1 absolute truth.
--   * Chapters/verses are man-made (supported for compatibility) but schema enables ranges, tokens, annotations.
--   * Strict integrity. Fail fast on mismatch.
--   * Hebrew vs Greek differences handled explicitly (see original_tokens.language and notes in schema doc).
--   * Production data (https://mt-sin.ai/365DBR/data/) is the ONLY authoritative source for population.
--
-- Migrations are plain SQL for auditability and reviewability.
-- Apply order: lexical by filename.
--
-- Run via: python db/scripts/apply_migrations.py

-- Schema version tracking (for this and future migrations)
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     TEXT PRIMARY KEY,
    applied_at  TIMESTAMPTZ DEFAULT now()
);

-- Record that we have started applying v0.1
-- (the apply script will INSERT this after successful execution of the file)

-- ============================================================
-- CORE TABLES (exact from Database-Schema.md v0.1)
-- ============================================================

-- Core reference: 66 books of the Bible
CREATE TABLE IF NOT EXISTS books (
    code            TEXT PRIMARY KEY,           -- 'GEN', 'PSA', 'MAT'
    name            TEXT NOT NULL,              -- 'Genesis'
    testament       TEXT NOT NULL CHECK (testament IN ('OT','NT')),
    order_canonical INT NOT NULL UNIQUE,
    num_chapters    INT NOT NULL,
    is_poetic       BOOLEAN DEFAULT FALSE,      -- e.g. PSA, PRO, JOB for special handling
    metadata        JSONB DEFAULT '{}'          -- future: genre, traditional author, etc.
);

-- Verse identifiers (stable BCV strings for human + joins)
CREATE TABLE IF NOT EXISTS verses (
    id              TEXT PRIMARY KEY,           -- 'GEN.1.1' (stable human + join key)
    book_code       TEXT NOT NULL REFERENCES books(code),
    chapter         INT NOT NULL,
    verse           INT NOT NULL,
    verse_order     INT NOT NULL,               -- global sequential order (enables "next/prev" beyond ch)
    UNIQUE (book_code, chapter, verse)
);

-- Translations (LSV primary; KJV seeded; LSB/WEB/etc later)
CREATE TABLE IF NOT EXISTS translations (
    id              SERIAL PRIMARY KEY,
    code            TEXT UNIQUE NOT NULL,       -- 'LSV', 'KJV'
    name            TEXT NOT NULL,              -- 'Literal Standard Version'
    language        TEXT NOT NULL DEFAULT 'en',
    source_bible_id TEXT,                       -- api.bible id for provenance
    is_primary      BOOLEAN DEFAULT FALSE,
    license         TEXT,
    added_date      DATE DEFAULT CURRENT_DATE
);

-- Per-verse translated text (fast path for display + search)
CREATE TABLE IF NOT EXISTS verse_translations (
    verse_id        TEXT NOT NULL REFERENCES verses(id),
    translation_id  INT NOT NULL REFERENCES translations(id),
    text            TEXT NOT NULL,
    text_tsv        tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
    source_note     TEXT,                       -- e.g. 'api.bible 0701 snapshot'
    PRIMARY KEY (verse_id, translation_id)
);

-- Original language tokens (word-level for Strong's, morphology, alignment)
-- NOTE: current production data has strongs reliably only for Hebrew (OT/PSA/PRO).
-- Greek (NT) tokens will store surface_text; strong_number will often be NULL until
-- enhanced sources are added. See Database-Schema.md "OT vs NT / Hebrew vs Greek Specifics".
CREATE TABLE IF NOT EXISTS original_tokens (
    id              BIGSERIAL PRIMARY KEY,
    verse_id        TEXT NOT NULL REFERENCES verses(id),
    word_order      INT NOT NULL,               -- within verse (or global pos later)
    language        TEXT NOT NULL,              -- 'hebrew' | 'greek' (distinguishes tokenization + direction)
    surface_text    TEXT,
    strong_number   TEXT,                       -- 'H7069' (Hebrew, current data); 'Gxxxx' rare/absent today for Greek
    lemma           TEXT,
    morph           TEXT,                       -- future: from enhanced api or other source
    extra           JSONB DEFAULT '{}',
    UNIQUE (verse_id, word_order)
);

-- Rich contextual / literary / S.I. metadata (ranges, not just single verses)
CREATE TABLE IF NOT EXISTS annotations (
    id                  BIGSERIAL PRIMARY KEY,
    annotation_type     TEXT NOT NULL,          -- 'speaker', 'audience', 'chronology', 'setting',
                                                -- 'genre', 'literary_unit', 'theme', 'cross_reference',
                                                -- 'theological_link', 'semantic_tag'
    start_verse_id      TEXT NOT NULL REFERENCES verses(id),
    end_verse_id        TEXT NOT NULL REFERENCES verses(id),
    value               TEXT NOT NULL,          -- e.g. 'Jesus', 'Creation Week', 'Covenant', 'David'
    metadata            JSONB DEFAULT '{}',     -- e.g. {"quote_type": "direct", "certainty": 0.95, "refs": [...] }
    source              TEXT,                   -- 'curated-manual', 'public-domain', 'inferred-from-text'
    created_at          TIMESTAMPTZ DEFAULT now(),
    CHECK (start_verse_id <= end_verse_id)      -- simple range (lex compare works for 'GEN.1.1' style)
);

-- Cross-references (thematic + explicit)
CREATE TABLE IF NOT EXISTS cross_references (
    id              BIGSERIAL PRIMARY KEY,
    source_start    TEXT REFERENCES verses(id),
    source_end      TEXT REFERENCES verses(id),
    target_start    TEXT REFERENCES verses(id),
    target_end      TEXT REFERENCES verses(id),
    ref_type        TEXT,                       -- 'quote', 'allusion', 'parallel', 'fulfillment'
    note            TEXT,
    source          TEXT
);

-- Daily reading plan (powers 365DBR experience directly from DB)
CREATE TABLE IF NOT EXISTS daily_readings (
    day             TEXT PRIMARY KEY,           -- '0101'
    label           TEXT NOT NULL,
    reading_time_min INT,                       -- computed or stored
    total_verses    INT
);

CREATE TABLE IF NOT EXISTS daily_passages (
    id              SERIAL PRIMARY KEY,
    day             TEXT NOT NULL REFERENCES daily_readings(day),
    section         TEXT NOT NULL,              -- 'OT', 'NT', 'PSA', 'PRO'
    start_verse_id  TEXT NOT NULL REFERENCES verses(id),
    end_verse_id    TEXT NOT NULL REFERENCES verses(id),
    file_ref        TEXT,                       -- original filename for provenance
    verse_count     INT,
    UNIQUE (day, section)
);

-- Provenance / migration audit
CREATE TABLE IF NOT EXISTS data_sources (
    id              SERIAL PRIMARY KEY,
    source_url      TEXT,                       -- https://mt-sin.ai/365DBR/data/0701/...
    fetch_date      DATE,
    bible_id_used   TEXT,
    notes           TEXT
);

-- ============================================================
-- INDEXES (critical for S.I. queries, as specified)
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_books_order ON books(order_canonical);

CREATE INDEX IF NOT EXISTS idx_verses_book_ch_verse ON verses(book_code, chapter, verse);
CREATE INDEX IF NOT EXISTS idx_verses_order ON verses(verse_order);

CREATE INDEX IF NOT EXISTS idx_verse_translations_tsv ON verse_translations USING GIN (text_tsv);

CREATE INDEX IF NOT EXISTS idx_original_tokens_strong ON original_tokens(strong_number);
CREATE INDEX IF NOT EXISTS idx_original_tokens_verse_order ON original_tokens(verse_id, word_order);

CREATE INDEX IF NOT EXISTS idx_annotations_type_value ON annotations(annotation_type, value);
CREATE INDEX IF NOT EXISTS idx_annotations_range ON annotations(start_verse_id, end_verse_id);
CREATE INDEX IF NOT EXISTS idx_annotations_metadata ON annotations USING GIN (metadata);

-- Trigram indexes for fuzzy search (enable extension; used for speaker/theme etc.)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_annotations_value_trgm ON annotations USING GIN (value gin_trgm_ops);

-- ============================================================
-- TRANSLATIONS SEED (idempotent)
-- ============================================================
-- LSV is primary (current production source).
-- KJV included for historical anchor.
-- LSB and others added when data access + alignment confirmed.
-- Source bibleIds taken from production analysis.

INSERT INTO translations (code, name, language, source_bible_id, is_primary, license)
VALUES 
    ('LSV', 'Literal Standard Version', 'en', '01b29f4b342acc35-01', TRUE, 'Public domain / appropriate license'),
    ('KJV', 'King James Version', 'en', 'de4e12af7f28f599-01', FALSE, NULL)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    source_bible_id = EXCLUDED.source_bible_id,
    is_primary = EXCLUDED.is_primary;

-- Note: Books are seeded via Python script (db/scripts/seed_books.py)
--       to stay perfectly in sync with apps/365DBR/bible_common.py BIBLE_DATA + BOOK_NAMES.
--       This is the single source of truth for canonical order and verse counts.

-- Record successful application of this migration file
INSERT INTO schema_migrations (version) VALUES ('001_initial_schema')
ON CONFLICT (version) DO NOTHING;
