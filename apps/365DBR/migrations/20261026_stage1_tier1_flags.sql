-- ============================================================================
-- Stage 1, Part 1: Schema Inspection & Idempotent Tier-1 / Commercial Flags
-- Target DB: mt_sinai_365dbr (User: 365dbr_dev)
-- ============================================================================

BEGIN;

-- 1. Add governance columns idempotently
ALTER TABLE translations
    ADD COLUMN IF NOT EXISTS allow_tier1_logic BOOLEAN NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS is_non_commercial_only BOOLEAN NOT NULL DEFAULT false;

-- 2. Update existing translations (KJV, LSV)
UPDATE translations
SET allow_tier1_logic = true,
    is_non_commercial_only = false
WHERE UPPER(code) IN ('KJV', 'LSV');

COMMIT;

-- 3. Verify translations table state and schema
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns
WHERE table_name = 'translations'
ORDER BY ordinal_position;

SELECT 
    id, 
    code, 
    name, 
    allow_tier1_logic, 
    is_non_commercial_only
FROM translations
ORDER BY id;