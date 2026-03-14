## 2026-03-14 - [Security Enhancement] Enforced Strict Path Validation & URL Encoding

**Learning:**
The `validate_safe_path` function previously only checked for directory traversal characters (`..`, `/`, `\`), which left the door open for other forms of injection or invalid characters when generating filenames or parsing inputs. Furthermore, external API endpoints were constructed without explicitly encoding dynamic parameters like `passage_range` and `bible_id`.

**Action:**
1. Updated `validate_safe_path` in `bible_common.py` to use a strict regex `r'^[a-zA-Z0-9.\-]+$'`, definitively blocking any unexpected characters from entering file paths or internal string references.
2. Updated `fetch_readings.py`, `check_data_integrity.py`, and `fetch_omissions_cache.py` to aggressively encode API URL parameters using `urllib.parse.quote()` to prevent HTTP parameter pollution or API endpoint manipulation.
