#!/usr/bin/env python3
"""
365DBR Phase 4 Option A — thin local read-only HTTP API over db/query.

Static JSON remains primary for live 365DBR (index.html / bible.html).
This server is for local/dev tooling and optional future UI hooks.
It does NOT replace loadDailyBread / verseMap / playVerse.

Default bind: 127.0.0.1:8765 (localhost only).

Endpoints (JSON):
  GET /health
  GET /verse/{verse_id}          e.g. /verse/GEN.1.1
  GET /strong/{num}?limit=20     e.g. /strong/H430?limit=5
  GET /day/{mmdd}?compact=1      e.g. /day/0101?compact=1
  GET /dual-read/{mmdd}?source=local

Usage (monorepo root):
  python db/scripts/serve_query_api.py
  python db/scripts/serve_query_api.py --port 8765 --host 127.0.0.1

Smoke (another shell):
  curl http://127.0.0.1:8765/health
  curl http://127.0.0.1:8765/verse/GEN.1.1
  curl "http://127.0.0.1:8765/strong/H430?limit=3"
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))

from query import (  # noqa: E402
    dual_read_day,
    get_connection,
    load_day,
    load_verse,
    search_strong,
)


def _json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")


class QueryAPIHandler(BaseHTTPRequestHandler):
    """Read-only JSON API. Failures → 4xx/5xx with error JSON."""

    server_version = "365DBR-QueryAPI/0.1"

    def log_message(self, fmt: str, *args) -> None:
        # Compact access log
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _cors(self) -> None:
        # Local optional UI experiments only; not a public prod surface.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send(self, code: int, body: dict | list, *, cache: bool = False) -> None:
        data = _json_bytes(body)
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if not cache:
            self.send_header("Cache-Control", "no-store")
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def _err(self, code: int, message: str, **extra) -> None:
        payload = {"ok": False, "error": message, **extra}
        self._send(code, payload)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        try:
            self._route_get()
        except Exception as e:
            traceback.print_exc()
            self._err(500, f"internal error: {e}")

    def _route_get(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path or "/")
        qs = parse_qs(parsed.query or "")

        # Normalize trailing slash (except root)
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")

        if path in ("/", "/health"):
            self._send(
                200,
                {
                    "ok": True,
                    "service": "365DBR-query-api",
                    "phase": "4-option-A",
                    "note": "Static JSON remains primary for live daily reader",
                    "endpoints": [
                        "GET /health",
                        "GET /verse/{verse_id}",
                        "GET /strong/{num}?limit=20",
                        "GET /day/{mmdd}?compact=1",
                        "GET /dual-read/{mmdd}?source=local",
                    ],
                },
            )
            return

        parts = [p for p in path.split("/") if p]
        if not parts:
            self._err(404, "not found")
            return

        head = parts[0].lower()

        if head == "verse" and len(parts) == 2:
            self._handle_verse(parts[1])
            return
        if head == "strong" and len(parts) == 2:
            limit = int((qs.get("limit") or ["20"])[0])
            self._handle_strong(parts[1], limit=limit)
            return
        if head == "day" and len(parts) == 2:
            compact = (qs.get("compact") or ["0"])[0] in ("1", "true", "yes")
            self._handle_day(parts[1], compact=compact)
            return
        if head in ("dual-read", "dual_read") and len(parts) == 2:
            source = (qs.get("source") or ["local"])[0]
            compact = (qs.get("compact") or ["0"])[0] in ("1", "true", "yes")
            self._handle_dual_read(parts[1], source=source, compact=compact)
            return

        self._err(404, f"unknown path: {path}")

    def _handle_verse(self, verse_id: str) -> None:
        conn = get_connection()
        try:
            payload = load_verse(conn, verse_id)
            self._send(200, {"ok": True, **payload})
        except KeyError as e:
            self._err(404, str(e))
        except ValueError as e:
            self._err(400, str(e))
        finally:
            conn.close()

    def _handle_strong(self, num: str, *, limit: int) -> None:
        conn = get_connection()
        try:
            payload = search_strong(conn, num, limit=limit)
            self._send(200, {"ok": True, **payload})
        except ValueError as e:
            self._err(400, str(e))
        finally:
            conn.close()

    def _handle_day(self, day: str, *, compact: bool) -> None:
        conn = get_connection()
        try:
            payload = load_day(conn, day)
            if compact:
                first = next(iter(payload["verseMap"]))
                out = {
                    "ok": True,
                    "day": payload["day"],
                    "label": payload["label"],
                    "verseCount": payload["verseCount"],
                    "availableTranslations": payload["availableTranslations"],
                    "passages": payload["passages"],
                    "sample": {first: payload["verseMap"][first]},
                    "source": payload["source"],
                }
                self._send(200, out)
            else:
                self._send(200, {"ok": True, **payload})
        except KeyError as e:
            self._err(404, str(e))
        except (ValueError, RuntimeError) as e:
            self._err(400, str(e))
        finally:
            conn.close()

    def _handle_dual_read(self, day: str, *, source: str, compact: bool = False) -> None:
        if source not in ("local", "prod"):
            self._err(400, "source must be local or prod")
            return
        conn = get_connection()
        try:
            report = dual_read_day(conn, day, source=source)
            # Always HTTP 200 with ok true/false so browsers show full JSON body
            # (409 "Conflict" is easy to misread as a broken response).
            if compact:
                out = {
                    "ok": report.get("ok"),
                    "day": report.get("day"),
                    "label": report.get("label"),
                    "source": report.get("source"),
                    "checked": report.get("checked"),
                    "plan_checked": report.get("plan_checked"),
                    "spillover_checked": report.get("spillover_checked"),
                    "mismatch_count": report.get("mismatch_count"),
                    "mismatches": report.get("mismatches", [])[:5],
                    "plan_missing_english_count": report.get("plan_missing_english_count"),
                    "plan_missing_english_sample": report.get(
                        "plan_missing_english_sample", []
                    )[:5],
                    "notes": report.get("notes"),
                    "db_verse_count": report.get("db_verse_count"),
                    "json_lsv_count": report.get("json_lsv_count"),
                    "json_kjv_count": report.get("json_kjv_count"),
                }
                self._send(200, out)
            else:
                self._send(200, {"ok": report.get("ok"), **report})
        except FileNotFoundError as e:
            self._err(404, str(e))
        except (KeyError, ValueError, RuntimeError) as e:
            self._err(400, str(e))
        finally:
            conn.close()


def make_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), QueryAPIHandler)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4 local read-only DB query API (static JSON remains primary)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default localhost)")
    parser.add_argument("--port", type=int, default=8765, help="Port (default 8765)")
    args = parser.parse_args()

    # Fail fast if DB unreachable
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) AS c FROM books")
            n = cur.fetchone()["c"]
        conn.close()
    except Exception as e:
        print(f"ERROR: cannot connect to DB: {e}", file=sys.stderr)
        print("Ensure docker compose up -d and db/.env DATABASE_URL are set.", file=sys.stderr)
        return 1

    httpd = make_server(args.host, args.port)
    print(f"365DBR query API listening on http://{args.host}:{args.port}/")
    print(f"  DB books row count smoke: {n}")
    print("  Static JSON remains primary for live daily reader.")
    print("  Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
