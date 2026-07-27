#!/usr/bin/env python3
"""
Phase 4 smoke: spin up local query API in-process and hit real endpoints.

Requires live Postgres with populated data (same as test_query_phase4.py).

  python db/scripts/test_query_api_phase4.py
"""

from __future__ import annotations

import json
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))
sys.path.insert(0, str(ROOT / "db" / "scripts"))

# Import server module by path-safe name
import importlib.util

spec = importlib.util.spec_from_file_location(
    "serve_query_api",
    ROOT / "db" / "scripts" / "serve_query_api.py",
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def get_json(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "365DBR-api-test/phase4"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8"))
        return e.code, body


def main() -> int:
    failures = 0

    def check(name: str, cond: bool, detail: str = ""):
        nonlocal failures
        status = "PASS" if cond else "FAIL"
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            failures += 1

    print("=== Phase 4 query API smoke ===")

    # Bind ephemeral port
    httpd = mod.make_server("127.0.0.1", 0)
    host, port = httpd.server_address[:2]
    base = f"http://{host}:{port}"

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.15)

    try:
        code, health = get_json(f"{base}/health")
        check("GET /health", code == 200 and health.get("ok") is True, f"code={code}")

        code, verse = get_json(f"{base}/verse/GEN.1.1")
        check("GET /verse/GEN.1.1", code == 200 and verse.get("ok") is True)
        check(
            "GEN.1.1 has LSV",
            "LSV" in (verse.get("translations") or {}),
            (verse.get("translations") or {}).get("LSV", "")[:50],
        )
        check(
            "GEN.1.1 has Strong's tokens",
            any(
                t.get("strong")
                for t in (verse.get("original") or {}).get("tokens") or []
            ),
        )

        code, strong = get_json(f"{base}/strong/H430?limit=3")
        check("GET /strong/H430", code == 200 and strong.get("ok") is True)
        check(
            "H430 total_verses ≥ 100",
            (strong.get("total_verses") or 0) >= 100,
            f"total={strong.get('total_verses')}",
        )
        check("H430 returns hits", (strong.get("returned") or 0) >= 1)

        code, day = get_json(f"{base}/day/0101?compact=1")
        check("GET /day/0101?compact=1", code == 200 and day.get("ok") is True)
        check(
            "day 0101 verseCount",
            (day.get("verseCount") or 0) > 50,
            f"verses={day.get('verseCount')}",
        )
        sample = day.get("sample") or {}
        first = next(iter(sample.values()), {}) if sample else {}
        check(
            "day sample lsv is str (flattened)",
            isinstance((first.get("lsv") or {}).get("text"), str),
        )

        # dual-read if local pack exists
        pack = ROOT / "apps" / "365DBR" / "data" / "0101" / "manifest.json"
        if pack.exists():
            code, dual = get_json(f"{base}/dual-read/0101?source=local")
            check(
                "GET /dual-read/0101",
                code == 200
                and dual.get("ok") is True
                and dual.get("mismatch_count") == 0,
                f"code={code} mismatches={dual.get('mismatch_count')} checked={dual.get('checked')}",
            )
            # 0228 historically surfaces Psalm numbering / spillover issues —
            # API must still return 200 + parseable JSON (ok may be false).
            code228, dual228 = get_json(f"{base}/dual-read/0228?compact=1&source=local")
            check(
                "GET /dual-read/0228?compact=1 returns JSON",
                code228 == 200 and "ok" in dual228 and "mismatch_count" in dual228,
                f"code={code228} ok={dual228.get('ok')} mm={dual228.get('mismatch_count')}",
            )
        else:
            print("  [SKIP] dual-read (no local 0101 pack)")

        # 404 path
        code, missing = get_json(f"{base}/nope")
        check("unknown path 404", code == 404 and missing.get("ok") is False)

        # bad strong
        code, bad = get_json(f"{base}/strong/NOTVALID")
        check("bad strong 400", code == 400 and bad.get("ok") is False)

    finally:
        httpd.shutdown()
        httpd.server_close()

    print("=" * 40)
    if failures:
        print(f"FAILED: {failures}")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
