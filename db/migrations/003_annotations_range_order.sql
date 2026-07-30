-- Phase 5: fix annotations range CHECK.
--
-- v0.1 used CHECK (start_verse_id <= end_verse_id) with *lexical* BCV compare.
-- That fails for multi-digit edges (e.g. MAT.5.3 > MAT.5.12 as text).
-- Ranges must be validated by verses.verse_order (canonical order).
--
-- This migration:
-- 1. Drops the broken lexical CHECK
-- 2. Adds a BEFORE INSERT/UPDATE trigger using verse_order

ALTER TABLE annotations DROP CONSTRAINT IF EXISTS annotations_check;

CREATE OR REPLACE FUNCTION annotations_range_order_ok()
RETURNS TRIGGER AS $$
DECLARE
    so INT;
    eo INT;
BEGIN
    SELECT verse_order INTO so FROM verses WHERE id = NEW.start_verse_id;
    SELECT verse_order INTO eo FROM verses WHERE id = NEW.end_verse_id;
    IF so IS NULL THEN
        RAISE EXCEPTION 'annotations.start_verse_id not in verses: %', NEW.start_verse_id;
    END IF;
    IF eo IS NULL THEN
        RAISE EXCEPTION 'annotations.end_verse_id not in verses: %', NEW.end_verse_id;
    END IF;
    IF so > eo THEN
        RAISE EXCEPTION
            'annotations range inverted by verse_order: % (%) > % (%)',
            NEW.start_verse_id, so, NEW.end_verse_id, eo;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_annotations_range_order ON annotations;
CREATE TRIGGER trg_annotations_range_order
    BEFORE INSERT OR UPDATE OF start_verse_id, end_verse_id
    ON annotations
    FOR EACH ROW
    EXECUTE FUNCTION annotations_range_order_ok();

COMMENT ON FUNCTION annotations_range_order_ok() IS
    'Phase 5: enforce annotation ranges by verses.verse_order, not lexical BCV';
