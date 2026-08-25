#!/usr/bin/env python3
"""
Smoke: static Word study export layout + sample payloads.

Does not require the HTTP server. Run after export_word_study_static.py.

  python db/scripts/test_word_study_static.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WS = ROOT / "apps" / "365DBR" / "ws"


def main() -> int:
    failures = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal failures
        status = "PASS" if cond else "FAIL"
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            failures += 1

    print("=== Static Word study (ws/) smoke ===")
    check("ws dir exists", WS.is_dir(), str(WS))
    man_path = WS / "manifest.json"
    check("manifest.json exists", man_path.is_file())
    if not man_path.is_file():
        print("Run: python db/scripts/export_word_study_static.py")
        return 1

    man = json.loads(man_path.read_text(encoding="utf-8"))
    check("manifest ok", man.get("ok") is True)
    check("mode static-ws", man.get("mode") == "static-ws")
    check("verses populated", (man.get("verses") or 0) >= 30000, str(man.get("verses")))
    check("strong numbers", (man.get("strong_numbers") or 0) >= 1000, str(man.get("strong_numbers")))

    gen_path = WS / "verse" / "GEN.json"
    check("verse/GEN.json", gen_path.is_file())
    if gen_path.is_file():
        gen = json.loads(gen_path.read_text(encoding="utf-8"))
        v = gen.get("GEN.1.1")
        check("GEN.1.1 present", isinstance(v, dict))
        toks = (v or {}).get("original", {}).get("tokens") or []
        check("GEN.1.1 has tokens", len(toks) >= 5, f"n={len(toks)}")
        check(
            "GEN.1.1 has Strong's",
            any(t.get("strong") for t in toks),
        )

    h_path = WS / "strong" / "H430.json"
    check("strong/H430.json", h_path.is_file())
    if h_path.is_file():
        h = json.loads(h_path.read_text(encoding="utf-8"))
        check("H430 ok", h.get("ok") is True)
        check("H430 has hits", len(h.get("hits") or []) >= 1)
        check("H430 total_verses", (h.get("total_verses") or 0) >= 100)

    books = list((WS / "verse").glob("*.json")) if (WS / "verse").is_dir() else []
    check("66 book shards", len(books) == 66, f"count={len(books)}")

    print("=" * 40)
    if failures:
        print(f"=== FAIL ({failures}) ===")
        return 1
    print("=== PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
