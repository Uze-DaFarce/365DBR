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
    // If caller passed an explicit static base, use it.
    if (base && isStaticBase(base)) {
      return Promise.resolve(base);
    }

    var explicit = resolveExplicitLiveApi();

    // Live HTTP(S) base passed in (often resolveQueryApiBase() → 127.0.0.1:8765).
    // On failure: fall back to same-origin ws/ unless this was an explicit ?queryApi=
    // override (then fail closed so a bad override is obvious).
    if (base && /^https?:\/\//i.test(base)) {
      return probeLiveApi(base, timeoutMs).then(function (live) {
        if (live) return live;
        if (
          explicit &&
          base.replace(/\/$/, "") === String(explicit).replace(/\/$/, "")
        ) {
          return null;
        }
        return probeStaticWs(timeoutMs);
      });
    }

    var chain = Promise.resolve(null);
    if (explicit) {
      chain = probeLiveApi(explicit, timeoutMs);
    } else if (isLocalPageHost()) {
      chain = probeLiveApi(DEFAULT_QUERY_API, timeoutMs);
    }

    return chain.then(function (live) {
      if (live) return live;
      // Production (and local when API down): same-origin static ws/
      return probeStaticWs(timeoutMs);
    });
  }

  function normalizeStrongKey(strong) {
    if (!strong) return "";
    var s = String(strong).trim().toUpperCase();
    var m = s.match(/^([HG])0*(\d+)([A-Z]*)$/);
    if (!m) return s;
    return m[1] + String(parseInt(m[2], 10)) + (m[3] || "");
  }

  /**
   * Static files keep the stored key (G0746.json, H0430.json) and sometimes
   * the unpadded key (H430.json). Try the token key first, then both forms.
   */
  function strongStaticKeys(strong) {
    var raw = String(strong || "").trim().toUpperCase();
    var keys = [];
    function add(k) {
      if (k && keys.indexOf(k) === -1) keys.push(k);
    }
    add(raw);
    var m = raw.match(/^([HG])0*(\d+)([A-Z]*)$/);
    if (m) {
      var digits = String(parseInt(m[2], 10));
      var suffix = m[3] || "";
      add(m[1] + digits + suffix);
      var padded = digits;
      while (padded.length < 4) padded = "0" + padded;
      add(m[1] + padded + suffix);
    }
    return keys;
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
      var keys = strongStaticKeys(strong);
      function tryKey(i) {
        if (i >= keys.length) {
          return Promise.resolve({
            ok: true,
            query: key,
            total_verses: 0,
            returned: 0,
            hits: [],
            source: "static-ws",
          });
        }
        return fetchJson(
          root + "strong/" + encodeURIComponent(keys[i]) + ".json"
        ).then(function (r) {
          if (!r.res.ok || !r.body || r.body.ok === false) return tryKey(i + 1);
          var body = r.body;
          if (body.hits && body.hits.length > limit) {
            body = Object.assign({}, body, {
              hits: body.hits.slice(0, limit),
              returned: Math.min(limit, body.hits.length),
            });
          }
          return body;
        });
      }
      return tryKey(0);
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

  function greekLetters(text) {
    var s = String(text || "").normalize("NFD");
    var out = "";
    for (var i = 0; i < s.length; i++) {
      var ch = s.charAt(i);
      if (/\p{M}/u.test(ch)) continue;
      if (ch === "ς") ch = "σ";
      var code = ch.charCodeAt(0);
      var greek =
        (code >= 0x0370 && code <= 0x03ff) || (code >= 0x1f00 && code <= 0x1fff);
      if (greek && /\p{L}/u.test(ch)) out += ch.toLowerCase();
    }
    return out;
  }

  function hebrewLetters(text) {
    var raw = String(text || "");
    var sof = raw.indexOf("\u05c3");
    if (sof >= 0) {
      raw =
        raw.slice(0, sof) +
        raw.slice(sof + 1).replace(/\u05e1/g, "").replace(/\u05e4/g, "");
    }
    var s = raw.normalize("NFKD");
    var out = "";
    for (var i = 0; i < s.length; i++) {
      var code = s.charCodeAt(i);
      if (code >= 0x05d0 && code <= 0x05ea) out += s.charAt(i);
    }
    return out;
  }

  /** ASCII file name. Greek and Hebrew letters do not survive FTP to GoDaddy. */
  function wordFileName(key) {
    var bytes = new TextEncoder().encode(key);
    var hex = "";
    for (var i = 0; i < bytes.length; i++) {
      var h = bytes[i].toString(16);
      hex += h.length < 2 ? "0" + h : h;
    }
    return hex + ".json";
  }

  /** Letters of the written word. Lemma when it has letters, else the surface. */
  function wordKey(token) {
    if (!token) return "";
    var hebrew = token.language === "hebrew";
    var letters = hebrew ? hebrewLetters : greekLetters;
    var fromLemma = letters(token.lemma);
    if (fromLemma) return fromLemma;
    return letters(token.surface);
  }

  function fetchWordHits(tokenOrKey, base, limit) {
    var key = typeof tokenOrKey === "string" ? tokenOrKey : wordKey(tokenOrKey);
    if (!key) {
      return Promise.resolve({
        ok: true,
        query: "",
        total_verses: 0,
        returned: 0,
        hits: [],
        source: "static-ws",
      });
    }
    limit = Math.max(1, Math.min(limit == null ? 12 : limit, 50));
    var root = isStaticBase(base) ? staticRoot(base) : resolveStaticWsBase();
    if (!root) {
      return Promise.reject(new Error("word study pack is not available"));
    }
    return fetchJson(root + "word/" + wordFileName(key)).then(
      function (r) {
        if (!r.res.ok || !r.body || r.body.ok === false) {
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
    fetchWordHits: fetchWordHits,
    wordKey: wordKey,
    formatVerseRef: formatVerseRef,
    normalizeStrongKey: normalizeStrongKey,
  };
})(typeof window !== "undefined" ? window : globalThis);
