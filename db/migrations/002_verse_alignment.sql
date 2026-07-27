-- 002_verse_alignment.sql
-- English-primary display + original (org) provenance via api.bible verseOrgIds.
-- See docs/365DBR/Verse-Identity-and-Alignment.md

-- Map: modern English BCV <-> source/org BCV (from parallel verseOrgIds)
CREATE TABLE IF NOT EXISTS verse_alignments (
    english_verse_id    TEXT NOT NULL REFERENCES verses(id),
    source_verse_id     TEXT NOT NULL,
    source_system       TEXT NOT NULL DEFAULT 'api.bible-org',
    established_by      TEXT,                   -- 'LSV' | 'KJV' | etc.
    note                TEXT,
    created_at          TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (english_verse_id, source_verse_id, source_system)
);

CREATE INDEX IF NOT EXISTS idx_verse_alignments_source
    ON verse_alignments(source_verse_id);

CREATE INDEX IF NOT EXISTS idx_verse_alignments_english
    ON verse_alignments(english_verse_id);

-- Provenance: org/source id for tokens stored under English-primary verse_id
ALTER TABLE original_tokens
    ADD COLUMN IF NOT EXISTS source_verse_id TEXT;

CREATE INDEX IF NOT EXISTS idx_original_tokens_source_verse
    ON original_tokens(source_verse_id)
    WHERE source_verse_id IS NOT NULL;

COMMENT ON TABLE verse_alignments IS
    'English (modern) verse id ↔ original/org verse id from api.bible verseOrgIds. Not an API error log.';
COMMENT ON COLUMN original_tokens.source_verse_id IS
    'Org/source verse id before English-primary remap; null when 1:1 with verse_id.';
