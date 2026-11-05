-- STEPBible TAHOT and TAGNT word rows.
-- One source row. Not a WLC or TR alignment, and not a Strong's certification.
-- original_token_id is filled later, and only when the letters match one original token in that verse.

CREATE TABLE IF NOT EXISTS stepbible_token_rows (
    id                 BIGSERIAL PRIMARY KEY,
    source             TEXT NOT NULL CHECK (source IN ('TAHOT', 'TAGNT')),
    source_file        TEXT NOT NULL,
    line_no            INT  NOT NULL CHECK (line_no > 0),
    ref_raw            TEXT NOT NULL,
    book_code          TEXT,
    chapter            INT,
    verse_num          INT,
    verse_id           TEXT REFERENCES verses(id),
    heb_ref            TEXT,
    word_index         INT  NOT NULL CHECK (word_index > 0),
    text_type          TEXT NOT NULL,
    surface            TEXT NOT NULL,
    transliteration    TEXT,
    english            TEXT,
    dstrong            TEXT,
    grammar            TEXT,
    meaning_variants   TEXT,
    spelling_variants  TEXT,
    dictionary_gloss   TEXT,
    editions           TEXT,
    spanish            TEXT,
    sub_meaning        TEXT,
    root_strong        TEXT,
    alt_strongs        TEXT,
    conjoin_word       TEXT,
    expanded_strong    TEXT,
    letters            TEXT,
    attach_candidate   BOOLEAN NOT NULL,
    original_token_id  BIGINT REFERENCES original_tokens(id) ON DELETE SET NULL,
    UNIQUE (source_file, line_no)
);

COMMENT ON TABLE stepbible_token_rows IS
    'One row per TAHOT or TAGNT word line. Contextual English is the english column. dstrong is the STEPBible tag on that line, not a certification of original_tokens.strong_number.';

COMMENT ON COLUMN stepbible_token_rows.heb_ref IS
    'Parenthetical alternate verse on the STEPBible ref when that file says the numbering differs (Hebrew Job.41.1(40.25), Greek Act.13.39(13.38)). A full verse whose letters match in order is linked even when this is set. A single word with this set is not linked by a letter guess.';

COMMENT ON COLUMN stepbible_token_rows.attach_candidate IS
    'Hebrew: text type starts with L or Q. Greek: text type contains uppercase K (Traditional / TR). X, R, Ketiv, and Greek rows without K stay in the table and are not candidates.';

COMMENT ON COLUMN stepbible_token_rows.original_token_id IS
    'Set when the row letters match the token. A whole verse of letters in order may match a token verse with a different number. No word_order join.';

COMMENT ON COLUMN stepbible_token_rows.english IS
    'STEPBible contextual English for this source row. Slashes follow Hebrew prefixes. Angle brackets are words STEPBible says are in the Hebrew and best left untranslated. Square brackets are English that is not in the Hebrew.';

CREATE INDEX IF NOT EXISTS idx_stepbible_token_rows_verse
    ON stepbible_token_rows (verse_id);

CREATE INDEX IF NOT EXISTS idx_stepbible_token_rows_token
    ON stepbible_token_rows (original_token_id);

CREATE INDEX IF NOT EXISTS idx_stepbible_token_rows_candidate
    ON stepbible_token_rows (source, attach_candidate);

CREATE OR REPLACE VIEW v_stepbible_linked AS
SELECT
    s.id,
    s.source,
    s.verse_id,
    s.word_index,
    s.text_type,
    s.surface,
    s.english,
    s.dstrong,
    s.letters,
    t.word_order AS token_word_order,
    t.surface_text AS token_surface,
    t.language AS token_language
FROM stepbible_token_rows s
JOIN original_tokens t ON t.id = s.original_token_id;

COMMENT ON VIEW v_stepbible_linked IS
    'STEPBible rows that matched one original token by letters. Greek strong_number on original_tokens is not certified and is not in this view.';

INSERT INTO schema_migrations (version) VALUES ('009_stepbible_token_rows')
ON CONFLICT DO NOTHING;
