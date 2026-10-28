CREATE TABLE IF NOT EXISTS strongs_lexicon (extended_strong TEXT PRIMARY KEY, base_strong TEXT NOT NULL, language TEXT NOT NULL, dstrongs TEXT, original_word TEXT, transliteration TEXT, morph_code TEXT, gloss TEXT, definition_html TEXT);
CREATE INDEX IF NOT EXISTS idx_strongs_lexicon_base ON strongs_lexicon(base_strong);
