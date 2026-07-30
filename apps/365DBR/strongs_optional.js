/**
 * Optional Strong's / original-token helpers via local Phase 4 query API.
 *
 * Loaded as a classic <script> (not ES import) so esm.sh/run text/tsx pages work.
 * Exposes window.__DBR_STRONGs__ — same pattern as bible_meta.js / __BIBLE_META__.
 *
 * Word study UI (index.html / bible.html):
 * - ON when GET /health succeeds (feature-detect). No opt-in flag.
 * - Original-first: click original words → Strong's search (data we actually have).
 * - English-word hover → original/Strong's needs free open alignment data later;
 *   do not invent maps (Truth/Accuracy). See docs/365DBR/Word-Study-and-Alignment.md.
 *
 * Override API base: ?queryApi=… or localStorage 365dbr_query_api
 */
(function (global) {
  "use strict";

  var DEFAULT_QUERY_API = "http://127.0.0.1:8765";

  function resolveQueryApiBase() {
    try {
      var params = new URLSearchParams(global.location.search);
      var fromQs = params.get("queryApi");
      if (fromQs && /^https?:\/\//i.test(fromQs)) {
        return fromQs.replace(/\/$/, "");
      }
    } catch (_) {
      /* ignore */
    }
    try {
      var stored = global.localStorage.getItem("365dbr_query_api");
      if (stored && /^https?:\/\//i.test(stored)) {
        return stored.replace(/\/$/, "");
      }
    } catch (_) {
      /* ignore */
    }
    return DEFAULT_QUERY_API;
  }

  /**
   * Probe GET /health. Returns base URL string if ok, else null.
   * Feature-detect only — Word study shows when API is up (no opt-in).
   */
  function probeQueryApi(base, timeoutMs) {
    base = base || resolveQueryApiBase();
    timeoutMs = timeoutMs == null ? 700 : timeoutMs;
    if (!base) return Promise.resolve(null);
    var ctrl =
      typeof AbortController !== "undefined" ? new AbortController() : null;
    var timer = setTimeout(function () {
      try {
        if (ctrl) ctrl.abort();
      } catch (_) {
        /* ignore */
      }
    }, timeoutMs);
    return fetch(base + "/health", {
      method: "GET",
      mode: "cors",
      cache: "no-store",
      signal: ctrl ? ctrl.signal : undefined,
    })
      .then(function (res) {
        if (!res.ok) return null;
        return res.json().catch(function () {
          return null;
        });
      })
      .then(function (body) {
        if (body && body.ok === true) return base;
        return null;
      })
      .catch(function () {
        return null;
      })
      .finally(function () {
        clearTimeout(timer);
      });
  }

  function fetchVerseDetail(verseId, base) {
    if (!base || !verseId) {
      return Promise.reject(new Error("missing base or verseId"));
    }
    var id = encodeURIComponent(String(verseId).trim());
    return fetch(base + "/verse/" + id, {
      method: "GET",
      mode: "cors",
      cache: "no-store",
    }).then(function (res) {
      return res.json().catch(function () {
        return {};
      }).then(function (body) {
        if (!res.ok || body.ok === false) {
          throw new Error(
            body.error || "verse " + verseId + ": HTTP " + res.status
          );
        }
        return body;
      });
    });
  }

  function fetchStrongHits(strong, base, limit) {
    if (!base || !strong) {
      return Promise.reject(new Error("missing base or strong"));
    }
    limit = Math.max(1, Math.min(limit == null ? 12 : limit, 50));
    var num = encodeURIComponent(String(strong).trim());
    return fetch(base + "/strong/" + num + "?limit=" + limit, {
      method: "GET",
      mode: "cors",
      cache: "no-store",
    }).then(function (res) {
      return res.json().catch(function () {
        return {};
      }).then(function (body) {
        if (!res.ok || body.ok === false) {
          throw new Error(
            body.error || "strong " + strong + ": HTTP " + res.status
          );
        }
        return body;
      });
    });
  }

  /**
   * User-facing BCV: "2KI.10.17" → "2 Kings 10:17".
   * bookNames: optional map like { "2KI": "2 Kings", GEN: "Genesis", ... }.
   */
  function formatVerseRef(vid, bookNames) {
    if (!vid) return "";
    var parts = String(vid).trim().split(".");
    if (parts.length < 3) return String(vid);
    var book = parts[0];
    var ch = parts[1];
    var verse = parts[2];
    var name =
      (bookNames && (bookNames[book] || bookNames[book.toUpperCase()])) || book;
    return name + " " + ch + ":" + verse;
  }

  global.__DBR_STRONGs__ = {
    DEFAULT_QUERY_API: DEFAULT_QUERY_API,
    resolveQueryApiBase: resolveQueryApiBase,
    probeQueryApi: probeQueryApi,
    fetchVerseDetail: fetchVerseDetail,
    fetchStrongHits: fetchStrongHits,
    formatVerseRef: formatVerseRef,
  };
})(typeof window !== "undefined" ? window : globalThis);
