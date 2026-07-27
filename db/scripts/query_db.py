#!/usr/bin/env python3
"""
365DBR Phase 4 (Option A): optional DB-backed query CLI.

Static JSON remains primary for live 365DBR (index.html / bible.html).
This tool does NOT modify verseMap consumers; it exposes DB capability for
diagnostics and future optional features.

Usage (monorepo root; quote MMDD on PowerShell):
  python db/scripts/query_db.py day --day "0101"
  python db/scripts/query_db.py verse --id GEN.1.1
  python db/scripts/query_db.py strong --num H430 --limit 5
  python db/scripts/query_db.py dual-read --day "0101" --source local
  python db/scripts/query_db.py dual-read --day "0101,0702,1225" --source local
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))

from query import (  # noqa: E402
    dual_read_day,
    get_connection,
    load_day,
    load_verse,
    search_strong,
)


def _print_json(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_day(args) -> int:
    conn = get_connection()
    try:
        payload = load_day(conn, args.day)
        if args.compact:
            # Summary without full verseMap dump
            summary = {
                "day": payload["day"],
                "label": payload["label"],
                "verseCount": payload["verseCount"],
                "availableTranslations": payload["availableTranslations"],
                "passages": payload["passages"],
                "sample_vids": list(payload["verseMap"].keys())[:5],
                "source": payload["source"],
            }
            if args.sample_verse:
                vid = args.sample_verse
                summary["sample"] = payload["verseMap"].get(vid)
            else:
                # first verse as sample
                first = next(iter(payload["verseMap"]))
                summary["sample"] = {first: payload["verseMap"][first]}
            _print_json(summary)
        else:
            _print_json(payload)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()


def cmd_verse(args) -> int:
    conn = get_connection()
    try:
        payload = load_verse(conn, args.id)
        _print_json(payload)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()


def cmd_strong(args) -> int:
    conn = get_connection()
    try:
        payload = search_strong(conn, args.num, limit=args.limit)
        if args.compact:
            print(
                f"Strong's {payload['query']}: "
                f"{payload['total_verses']} verses "
                f"(showing {payload['returned']})"
            )
            for h in payload["hits"]:
                lsv = (h.get("lsv") or "")[:80]
                print(f"  {h['verse_id']:12} {h.get('surface') or '':12}  {lsv}")
        else:
            _print_json(payload)
        return 0 if payload["total_verses"] > 0 else 2
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()


def cmd_dual_read(args) -> int:
    days = [d.strip() for d in args.day.split(",") if d.strip()]
    if not days:
        print("ERROR: no days given", file=sys.stderr)
        return 1

    conn = get_connection()
    overall_ok = True
    try:
        for day in days:
            print(f"\n=== dual-read day {day} (source={args.source}) ===")
            try:
                report = dual_read_day(conn, day, source=args.source)
            except FileNotFoundError as e:
                print(f"  [FAIL] {e}")
                overall_ok = False
                continue
            except Exception as e:
                print(f"  [FAIL] {e}")
                overall_ok = False
                continue

            status = "PASS" if report["ok"] else "FAIL"
            print(
                f"  [{status}] checked={report['checked']} "
                f"plan={report.get('plan_checked', '?')} "
                f"spillover={report.get('spillover_checked', 0)} "
                f"mismatches={report['mismatch_count']} "
                f"db_verses={report['db_verse_count']} "
                f"json_lsv={report['json_lsv_count']} "
                f"json_kjv={report['json_kjv_count']}"
            )
            print(f"  label: {report['label']}")
            for note in report.get("notes") or []:
                print(f"  [NOTE] {note}")
            missing_en = report.get("plan_missing_english_count") or 0
            if missing_en:
                sample = report.get("plan_missing_english_sample") or []
                print(
                    f"  [INFO] plan verses without English in DB: {missing_en} "
                    f"(sample: {sample[:5]})"
                )
            if report["mismatches"]:
                for m in report["mismatches"][:10]:
                    print(
                        f"  mismatch {m['translation']} {m['verse_id']} "
                        f"({m['reason']})"
                    )
                    if m.get("json") is not None:
                        print(f"    json: {m['json']}")
                    if m.get("db") is not None:
                        print(f"    db:   {m['db']}")
            if args.json:
                _print_json(report)
            if not report["ok"]:
                overall_ok = False

        print("\n" + "=" * 50)
        if overall_ok:
            print("=== DUAL-READ OVERALL: PASS ===")
            return 0
        print("=== DUAL-READ OVERALL: FAIL ===")
        return 1
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4 optional DB query CLI (static JSON remains primary)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_day = sub.add_parser("day", help="Load day from DB as verseMap-compatible JSON")
    p_day.add_argument("--day", required=True, help='MMDD (quote on PowerShell: "0101")')
    p_day.add_argument(
        "--compact",
        action="store_true",
        help="Summary + one sample verse (default full verseMap can be large)",
    )
    p_day.add_argument("--sample-verse", default=None, help="Include this BCV in compact mode")
    p_day.set_defaults(func=cmd_day)

    p_verse = sub.add_parser("verse", help="Load one verse (translations + Strong's tokens)")
    p_verse.add_argument("--id", required=True, help="BCV id e.g. GEN.1.1 or JHN.1.1")
    p_verse.set_defaults(func=cmd_verse)

    p_strong = sub.add_parser("strong", help="Search verses by Strong's number")
    p_strong.add_argument("--num", required=True, help="H430 or G26 etc.")
    p_strong.add_argument("--limit", type=int, default=20)
    p_strong.add_argument("--compact", action="store_true", help="Table-style output")
    p_strong.set_defaults(func=cmd_strong)

    p_dual = sub.add_parser(
        "dual-read",
        help="Compare local/prod JSON day pack English text vs DB (fail on mismatch)",
    )
    p_dual.add_argument(
        "--day",
        required=True,
        help='MMDD or comma list (quote: "0101,0702")',
    )
    p_dual.add_argument(
        "--source",
        choices=("local", "prod"),
        default="local",
        help="JSON pack source (default local verified packs)",
    )
    p_dual.add_argument(
        "--json",
        action="store_true",
        help="Also emit full report JSON per day",
    )
    p_dual.set_defaults(func=cmd_dual_read)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
