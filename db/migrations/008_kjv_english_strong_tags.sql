-- eng-kjv2006 tags on KJV English words.
-- Not a WLC or TR token alignment, and not a certification that the number is right.
CREATE TABLE IF NOT EXISTS kjv_english_strong_tags (
    verse_id      TEXT NOT NULL REFERENCES verses(id),
    word_order    INT  NOT NULL CHECK (word_order > 0),
    surface       TEXT NOT NULL,
    strong_number TEXT,
    edition       TEXT NOT NULL DEFAULT 'eng-kjv2006' CHECK (edition = 'eng-kjv2006'),
    PRIMARY KEY (verse_id, word_order)
);

COMMENT ON TABLE kjv_english_strong_tags IS
    'KJV English-word Strong''s tags from eBible eng-kjv2006. word_order counts \w and \+w spans in the verse, not every English word. Not Hebrew or Greek token alignment, and not a certification that the number is right.';

CREATE INDEX IF NOT EXISTS idx_kjv_english_strong_tags_strong
    ON kjv_english_strong_tags (strong_number);
