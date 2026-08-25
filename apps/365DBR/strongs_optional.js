/**
 * Optional Strong's / original-token helpers.
 *
 * Sources (feature-detect, no opt-in flag):
 * 1. Live local query API (localhost only by default) — http://127.0.0.1:8765
 * 2. Static same-origin packs under ./ws/ (GoDaddy / mt-sin.ai — $0, CSP-safe)
 * 3. Explicit ?queryApi= or localStorage 365dbr_query_api
 *
 * Exposes window.__DBR_STRONGs__.
 * See docs/365DBR/Word-Study-and-Alignment.md and apps/365DBR/ws/README.md.
 */
(function (global) {
  "use strict";

  var DEFAULT_QUERY_API = "http://127.0.0.1:8765";
  var STATIC_MARKER = "static:";

  /** True when the page itself is served from this machine (local dev). */
  function isLocalPageHost() {
    try {
      var h = (global.location && global.location.hostname) || "";
      return (
        h === "localhost" ||
        h === "127.0.0.1" ||
        h === "[::1]" ||
        h === ""
      );
    } catch (_) {
      return false;
    }
  }

  /** Absolute URL to apps/365DBR/ws/ (trailing slash). */
  function resolveStaticWsBase() {
    try {
      return new URL("ws/", global.location.href).href;
    } catch (_) {
      return null;
    }
  }

  function isStaticBase(base) {
    return !!(base && String(base).indexOf(STATIC_MARKER) === 0);
  }

  function staticRoot(base) {
    if (!isStaticBase(base)) return null;
    return String(base).slice(STATIC_MARKER.length);
  }

  /**
   * Explicit live API override only (?queryApi / localStorage).
   * Does not return the localhost default — that is handled in probe.
   */
  function resolveExplicitLiveApi() {
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
    return null;
  }

  /** @deprecated Prefer probeWordStudySource; kept for call sites. */
  function resolveQueryApiBase() {
    return resolveExplicitLiveApi() || (isLocalPageHost() ? DEFAULT_QUERY_API : null);
  }

  function fetchJson(url, timeoutMs) {
    timeoutMs = timeoutMs == null ? 8000 : timeoutMs;
    var ctrl =
      typeof AbortController !== "undefined" ? new AbortController() : null;
    var timer = setTimeout(function () {
      try {
        if (ctrl) ctrl.abort();
      } catch (_) {
        /* ignore */
      }
    }, timeoutMs);
    return fetch(url, {
      method: "GET",
      mode: "cors",
      cache: "default",
      signal: ctrl ? ctrl.signal : undefined,
    })
      .then(function (res) {
        return res.json().catch(function () {
          return null;
        }).then(function (body) {
          return { res: res, body: body };
        });
      })
      .finally(function () {
        clearTimeout(timer);
      });
  }

  function probeLiveApi(base, timeoutMs) {
    timeoutMs = timeoutMs == null ? 700 : timeoutMs;
    if (!base) return Promise.resolve(null);
    return fetchJson(base.replace(/\/$/, "") + "/health", timeoutMs)
      .then(function (r) {
        if (r.res.ok && r.body && r.body.ok === true) return base.replace(/\/$/, "");
        return null;
      })
      .catch(function () {
        return null;
      });
  }

  function probeStaticWs(timeoutMs) {
    var root = resolveStaticWsBase();
    if (!root) return Promise.resolve(null);
    return fetchJson(root + "manifest.json", timeoutMs == null ? 2500 : timeoutMs)
      .then(function (r) {
        if (r.res.ok && r.body && r.body.ok === true) {
          return STATIC_MARKER + root;
        }
        return null;
      })
      .catch(function () {
        return null;
      });
  }

  /**
   * Feature-detect Word study source.
   * Returns live API base URL, or "static:https://…/ws/", or null.
   */
  function probeQueryApi(base, timeoutMs) {
    // If caller passed an explicit base (including static:), honor probe paths
    if (base && isStaticBase(base)) {
      return Promise.resolve(base);
    }
    if (base && /^https?:\/\//i.test(base)) {
      return probeLiveApi(base, timeoutMs);
    }

    var explicit = resolveExplicitLiveApi();
    var chain = Promise.resolve(null);

    if (explicit) {
      chain = probeLiveApi(explicit, timeoutMs);
    } else if (isLocalPageHost()) {
      chain = probeLiveApi(DEFAULT_QUERY_API, timeoutMs);
    }

    return chain.then(function (live) {
      if (live) return live;
      // Production (and local fallback): same-origin static ws/
      return probeStaticWs(timeoutMs);
    });
  }

  function normalizeStrongKey(strong) {
    if (!strong) return "";
    var s = String(strong).trim().toUpperCase();
    var m = s.match(/^([HG])0*(\d+)$/);
    if (!m) return s;
    return m[1] + String(parseInt(m[2], 10));
  }

  // In-memory book shard cache for static mode
  var _bookCache = Object.create(null);

  function loadStaticBook(root, book) {
    if (_bookCache[book]) return _bookCache[book];
    var p = fetchJson(root + "verse/" + encodeURIComponent(book) + ".json").then(
      function (r) {
        if (!r.res.ok || !r.body || typeof r.body !== "object") {
          throw new Error("static verse book missing: " + book);
        }
        return r.body;
      }
    );
    _bookCache[book] = p;
    return p;
  }

  function fetchVerseDetail(verseId, base) {
    if (!base || !verseId) {
      return Promise.reject(new Error("missing base or verseId"));
    }
    var vid = String(verseId).trim();
    var parts = vid.split(".");
    if (parts.length >= 3) {
      vid = parts[0].toUpperCase() + "." + parts[1] + "." + parts[2];
    }

    if (isStaticBase(base)) {
      var root = staticRoot(base);
      var book = vid.split(".")[0];
      return loadStaticBook(root, book).then(function (map) {
        var row = map[vid];
        if (!row) {
          throw new Error("verse not in static pack: " + vid);
        }
        return row;
      });
    }

    var id = encodeURIComponent(vid);
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
    var key = normalizeStrongKey(strong);

    if (isStaticBase(base)) {
      var root = staticRoot(base);
      return fetchJson(root + "strong/" + encodeURIComponent(key) + ".json").then(
        function (r) {
          if (!r.res.ok || !r.body || r.body.ok === false) {
            // No Strong's file (e.g. Greek surface-only) — empty hits, not hard fail
            return {
              ok: true,
              query: key,
              total_verses: 0,
              returned: 0,
              hits: [],
              source: "static-ws",
            };
          }
          var body = r.body;
          if (body.hits && body.hits.length > limit) {
            body = Object.assign({}, body, {
              hits: body.hits.slice(0, limit),
              returned: Math.min(limit, body.hits.length),
            });
          }
          return body;
        }
      );
    }

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
    STATIC_MARKER: STATIC_MARKER,
    isLocalPageHost: isLocalPageHost,
    resolveStaticWsBase: resolveStaticWsBase,
    resolveQueryApiBase: resolveQueryApiBase,
    probeQueryApi: probeQueryApi,
    fetchVerseDetail: fetchVerseDetail,
    fetchStrongHits: fetchStrongHits,
    formatVerseRef: formatVerseRef,
    normalizeStrongKey: normalizeStrongKey,
  };
})(typeof window !== "undefined" ? window : globalThis);
