# Retired api.bible fetchers

Do not run these.

`fetch_readings.py` and `fetch_omissions_cache.py` call api.bible and can overwrite `apps/365DBR/data/MMDD` day packs. That monthly process is finished. KJV and LSV load from the local eBible files (`load_ebible_kjv_lsv.py`). Do not add LSB here.

Moved out of `apps/365DBR/` on 2026-11-04 so they would not be run again by mistake.
