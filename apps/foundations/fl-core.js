/* ==========================================================================
   Foundations Library (FL) — fl-core.js (100% CSP 'script-src self' Compliant)
   2-Line Topbar Height Sync, Universal TOC Toggle, Scroll-Lock,
   12-Way Free Share Modal, Church Co-Brand Studio & 365DBR Reader
   ========================================================================== */
const FLApp = (() => {
  const COBRAND_STORAGE_KEY = "fl_cobrand_config_v1";

  const SVGS = {
    share: '<svg class="fl-icon-svg" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>',
    copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
    blurb: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
    sms: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    email: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
    facebook: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z"/></svg>',
    gab: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm3.6 13.8c-1 .9-2.3 1.4-3.8 1.4-3.1 0-5.4-2.2-5.4-5.2S8.7 6.8 11.8 6.8c1.6 0 3 .6 4 1.6l-1.5 1.5c-.6-.6-1.5-1-2.5-1-1.9 0-3.2 1.3-3.2 3.1s1.3 3.1 3.2 3.1c1.2 0 2.1-.5 2.5-1.3h-2.5v-1.9h4.6v2.1c0 .7-.3 1.3-.8 1.8z"/></svg>',
    truth: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4 4h16v3.5h-6.25V20h-3.5V7.5H4V4zm12.5 9.5H20V17h-3.5v-3.5z"/></svg>',
    telegram: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>',
    whatsapp: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.031 2c-5.516 0-9.969 4.453-9.969 9.969 0 1.766.469 3.484 1.359 5.016L2 22l5.141-1.344c1.484.813 3.172 1.25 4.891 1.25 5.516 0 9.969-4.453 9.969-9.969S17.547 2 12.031 2zm5.813 14.125c-.25.703-1.453 1.344-2.016 1.422-.531.078-1.203.109-1.953-.125-.453-.141-1.047-.344-1.797-.672-3.156-1.359-5.219-4.547-5.375-4.766-.156-.203-1.281-1.703-1.281-3.25s.813-2.313 1.109-2.625c.281-.313.625-.391.828-.391.203 0 .406.016.594.016.188 0 .438-.078.688.531.25.609.859 2.094.938 2.25.078.156.125.344.031.547-.094.203-.141.344-.297.516-.156.172-.313.391-.453.516-.141.141-.297.297-.125.594.172.297.766 1.266 1.641 2.047 1.125 1 2.078 1.313 2.375 1.469.297.156.469.125.641-.078.172-.203.734-.859.938-1.156.203-.297.391-.25.656-.156.266.094 1.688.797 1.984.938.281.141.484.219.547.344.078.125.078.719-.172 1.422z"/></svg>',
    print: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>'
  };

  function syncTopbarHeight() {
    const topbar = document.querySelector(".fl-topbar");
    if (!topbar) return;
    const update = () => {
      const h = Math.round(topbar.getBoundingClientRect().height);
      if (h > 0) {
        document.documentElement.style.setProperty("--fl-topbar-height", `${h}px`);
      }
    };
    update();
    window.addEventListener("resize", update);
    if ("ResizeObserver" in window) {
      new ResizeObserver(update).observe(topbar);
    }
  }

  function runCaseRouterIf404() {
    if (!document.body || !document.body.hasAttribute("data-fl-case-router")) return;
    const path = window.location.pathname || "";
    const lower = path.toLowerCase().replace(/_/g, "-");
    const search = window.location.search || "";
    const hash = window.location.hash || "";

    if (lower.indexOf("god") !== -1 || lower.indexOf("what-we-know") !== -1) {
      window.location.replace("/foundations/what-does-the-bible-say-about-god.html" + search + hash);
      return;
    }
    if (lower.indexOf("education") !== -1) {
      window.location.replace("/foundations/what-does-the-bible-say-about-education.html" + search + hash);
      return;
    }
    if (path !== lower) {
      window.location.replace(lower + search + hash);
    }
  }

  function normalizeScriptureUrl(rawHref) {
    if (!rawHref) return "";
    try {
      const parsed = new URL(rawHref, window.location.origin);
      if (parsed.pathname === "/365DBR/" || parsed.pathname === "/365DBR/index.html") {
        if (parsed.searchParams.has("book")) {
          parsed.pathname = "/365DBR/bible.html";
        }
      }
      if (parsed.pathname.endsWith("/bible.html")) {
        parsed.searchParams.set("fullverse", "1");
      }
      return parsed.pathname + parsed.search + parsed.hash;
    } catch (e) {
      const hasFull = /[?&]fullverse=1\b/.test(rawHref);
      if (hasFull) return rawHref;
      return rawHref + (rawHref.includes("?") ? "&" : "?") + "fullverse=1";
    }
  }

  function findReadingAnchor(preferredEl) {
    if (preferredEl && preferredEl.getBoundingClientRect) {
      const r = preferredEl.getBoundingClientRect();
      if (r.width > 0 || r.height > 0) return preferredEl;
    }
    const topbarH = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--fl-topbar-height")) || 76;
    const candidates = document.querySelectorAll(
      ".fl-main p, .fl-main li, .fl-main h2, .fl-main h3, .container .point, .container h2, .hub-container .book-card"
    );
    for (let i = 0; i < candidates.length; i++) {
      const rect = candidates[i].getBoundingClientRect();
      if (rect.bottom > topbarH + 12 && rect.height > 0) {
        return candidates[i];
      }
    }
    return null;
  }

  function withScrollLock(preferredEl, mutateLayoutFn) {
    const anchor = findReadingAnchor(preferredEl);
    const prevTop = anchor ? anchor.getBoundingClientRect().top : null;
    const htmlEl = document.documentElement;
    const prevScrollBehavior = htmlEl.style.scrollBehavior;
    htmlEl.style.scrollBehavior = "auto";

    mutateLayoutFn();

    if (anchor && prevTop !== null) {
      const newTop = anchor.getBoundingClientRect().top;
      const delta = newTop - prevTop;
      if (Math.abs(delta) > 0.5) {
        window.scrollBy(0, delta);
      }
    }
    requestAnimationFrame(() => {
      htmlEl.style.scrollBehavior = prevScrollBehavior;
    });
  }

  function isCompactTocViewport() {
    return window.matchMedia("(max-width: 1200px), (max-height: 500px)").matches;
  }

  function syncTocAria() {
    const btn = document.querySelector('[data-fl-action="toggle-toc"]');
    if (!btn) return;
    const isOpen = isCompactTocViewport()
      ? document.body.classList.contains("toc-open")
      : !document.body.classList.contains("toc-collapsed");
    btn.setAttribute("aria-expanded", isOpen ? "true" : "false");
  }

  function toggleToc() {
    if (isCompactTocViewport()) {
      document.body.classList.toggle("toc-open");
      syncTocAria();
    } else {
      withScrollLock(null, () => {
        document.body.classList.toggle("toc-collapsed");
      });
      syncTocAria();
    }
  }

  function closeReader() {
    const drawer = document.getElementById("bible-drawer");
    if (!drawer) return;
    if (document.activeElement && drawer.contains(document.activeElement)) {
      document.activeElement.blur();
    }
    withScrollLock(null, () => {
      drawer.classList.remove("open");
      drawer.setAttribute("aria-hidden", "true");
      drawer.setAttribute("inert", "");
      drawer.inert = true;
      document.body.classList.remove("drawer-open");
    });
  }

  /* ==========================================================================
     Co-Branding Engine (URL Params + LocalStorage + Custom Colors, Font & Logo)
     ========================================================================== */
  function getStoredCoBrand() {
    try {
      const raw = localStorage.getItem(COBRAND_STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }

  function saveStoredCoBrand(cfg) {
    try {
      if (!cfg || (!cfg.church && !cfg.primary && !cfg.secondary && !cfg.highlight && !cfg.font && !cfg.logo)) {
        localStorage.removeItem(COBRAND_STORAGE_KEY);
      } else {
        localStorage.setItem(COBRAND_STORAGE_KEY, JSON.stringify(cfg));
      }
    } catch (e) {}
  }

  function sanitizeHexColor(val) {
    if (!val) return "";
    const clean = val.trim().replace(/^#/, "");
    return /^([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/.test(clean) ? "#" + clean : "";
  }

  function getActiveCoBrandConfig() {
    const params = new URLSearchParams(window.location.search);
    const stored = getStoredCoBrand();
    const urlChurch = params.get("church") || params.get("org") || params.get("ministry") || "";
    const hasUrlOverride = Boolean(urlChurch || params.get("primary") || params.get("secondary") || params.get("highlight") || params.get("font") || params.get("logo"));

    const cfg = {
      church: urlChurch || stored.church || "",
      city: params.get("city") || (hasUrlOverride ? "" : stored.city) || "",
      primary: sanitizeHexColor(params.get("primary")) || stored.primary || "",
      secondary: sanitizeHexColor(params.get("secondary")) || stored.secondary || "",
      highlight: sanitizeHexColor(params.get("highlight")) || stored.highlight || "",
      font: params.get("font") || stored.font || "",
      logo: params.get("logo") || stored.logo || ""
    };

    if (hasUrlOverride) {
      saveStoredCoBrand(cfg);
    }
    return cfg;
  }

  function applyCoBrandConfig(cfg) {
    const root = document.documentElement;
    if (cfg.primary) {
      root.style.setProperty("--fl-topbar-bg", cfg.primary);
      root.style.setProperty("--accent", cfg.primary);
      root.style.setProperty("--fl-accent", cfg.primary);
    } else {
      root.style.removeProperty("--fl-topbar-bg");
      root.style.removeProperty("--accent");
      root.style.removeProperty("--fl-accent");
    }

    if (cfg.secondary) {
      root.style.setProperty("--accent-bg", cfg.secondary);
    } else {
      root.style.removeProperty("--accent-bg");
    }

    if (cfg.highlight) {
      root.style.setProperty("--gold", cfg.highlight);
      root.style.setProperty("--fl-gold", cfg.highlight);
      root.style.setProperty("--fl-topbar-border", cfg.highlight);
    } else {
      root.style.removeProperty("--gold");
      root.style.removeProperty("--fl-gold");
      root.style.removeProperty("--fl-topbar-border");
    }

    if (cfg.font === "merriweather") {
      root.style.setProperty("--fl-topbar-font", "'Merriweather', 'Georgia', serif");
    } else if (cfg.font === "sans") {
      root.style.setProperty("--fl-topbar-font", "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif");
    } else if (cfg.font === "cinzel") {
      root.style.setProperty("--fl-topbar-font", "'Cinzel', 'Georgia', serif");
    } else {
      root.style.removeProperty("--fl-topbar-font");
    }

    const box = document.getElementById("fl-cobrand-box");
    let printBanner = document.getElementById("fl-print-cobrand-banner");
    if (!printBanner) {
      printBanner = document.createElement("div");
      printBanner.id = "fl-print-cobrand-banner";
      printBanner.className = "fl-print-cobrand-header";
      const mainContainer = document.querySelector(".fl-main, .container, .hub-container");
      if (mainContainer) {
        mainContainer.insertBefore(printBanner, mainContainer.firstChild);
      }
    }

    if (cfg.church || cfg.logo) {
      const label = cfg.church ? (cfg.city ? `${cfg.church} (${cfg.city})` : cfg.church) : "Ministry Partner";
      if (box) {
        box.innerHTML = "";
        box.style.display = "inline-flex";
        if (cfg.logo) {
          const img = document.createElement("img");
          img.src = cfg.logo;
          img.alt = label + " Logo";
          img.className = "fl-cobrand-logo";
          box.appendChild(img);
        }
        const span = document.createElement("span");
        span.textContent = cfg.church ? `Provided in partnership with: ${label}` : label;
        box.appendChild(span);
      }
      if (printBanner) {
        printBanner.innerHTML = "";
        printBanner.classList.add("has-cobrand");
        const left = document.createElement("div");
        left.innerHTML = `<strong>Provided in partnership with:</strong> ${label}`;
        printBanner.appendChild(left);
        if (cfg.logo) {
          const pImg = document.createElement("img");
          pImg.src = cfg.logo;
          pImg.alt = label;
          printBanner.appendChild(pImg);
        }
      }
    } else {
      if (box) {
        box.style.display = "none";
        box.innerHTML = "";
      }
      if (printBanner) {
        printBanner.classList.remove("has-cobrand");
        printBanner.innerHTML = "";
      }
    }

    syncTopbarHeight();

    // Propagate URL shareable co-brand query params to internal /foundations/ links
    document.querySelectorAll('a[href^="/foundations/"]').forEach((a) => {
      try {
        const url = new URL(a.getAttribute("href"), window.location.origin);
        ["church", "city", "primary", "secondary", "highlight", "font", "logo"].forEach((k) => {
          url.searchParams.delete(k);
        });
        if (cfg.church) url.searchParams.set("church", cfg.church);
        if (cfg.city) url.searchParams.set("city", cfg.city);
        if (cfg.primary) url.searchParams.set("primary", cfg.primary);
        if (cfg.secondary) url.searchParams.set("secondary", cfg.secondary);
        if (cfg.highlight) url.searchParams.set("highlight", cfg.highlight);
        if (cfg.font) url.searchParams.set("font", cfg.font);
        if (cfg.logo && !cfg.logo.startsWith("data:")) url.searchParams.set("logo", cfg.logo);
        a.setAttribute("href", url.pathname + url.search + url.hash);
      } catch (e) {}
    });
  }

  function initCoBranding() {
    const cfg = getActiveCoBrandConfig();
    applyCoBrandConfig(cfg);
  }

  /* ==========================================================================
     12-Way Zero-Tracking Share Modal & Co-Brand Link Generator
     ========================================================================== */
  function getDefaultShareTarget(triggerEl) {
    const path = window.location.pathname || "";
    let shortUrl = "https://mt-sin.ai/fl/";
    let title = "Foundations Library — 100% Free Sola Scriptura Books, Articles & Scripture Tools";
    let desc = "Read, print, duplicate, and freely share Sola Scriptura books and articles linked directly to the Original Hebrew & Greek (365DBR) — 100% free (Matthew 10:8).";

    if (path.indexOf("god") !== -1) {
      shortUrl = "https://mt-sin.ai/fl/god";
      title = "Book 1: What Does the Bible Say About God? (What We Know About God — Foundational Facts, Biblically Backed)";
      desc = "A concise Sola Scriptura reference establishing who God is, why He created us, and how Jesus Christ accomplished our redemption — 100% free to read, print & share.";
    } else if (path.indexOf("education") !== -1) {
      shortUrl = "https://mt-sin.ai/fl/edu";
      title = "Book 2: What Does the Bible Say About Education? (Foundational Truths for Parents & Students Survival Guide)";
      desc = "Exposes the Concordance Trap and secular neutrality myth with 8 printable family & student labs and the K–12 Worldview Hour Calculator — 100% free to read, print & share.";
    }

    if (triggerEl) {
      const customUrl = triggerEl.getAttribute("data-share-url");
      const customTitle = triggerEl.getAttribute("data-share-title");
      const customDesc = triggerEl.getAttribute("data-share-desc");
      if (customUrl) shortUrl = customUrl;
      if (customTitle) title = customTitle;
      if (customDesc) desc = customDesc;
    }

    // Append active co-brand parameters if present
    const cfg = getActiveCoBrandConfig();
    if (cfg.church || cfg.primary || cfg.secondary || cfg.highlight || cfg.font || (cfg.logo && !cfg.logo.startsWith("data:"))) {
      try {
        const u = new URL(shortUrl);
        if (cfg.church) u.searchParams.set("church", cfg.church);
        if (cfg.city) u.searchParams.set("city", cfg.city);
        if (cfg.primary) u.searchParams.set("primary", cfg.primary);
        if (cfg.secondary) u.searchParams.set("secondary", cfg.secondary);
        if (cfg.highlight) u.searchParams.set("highlight", cfg.highlight);
        if (cfg.font) u.searchParams.set("font", cfg.font);
        if (cfg.logo && !cfg.logo.startsWith("data:")) u.searchParams.set("logo", cfg.logo);
        shortUrl = u.toString();
      } catch (e) {}
    }

    return { url: shortUrl, title, desc };
  }

  function copyTextToClipboard(text, btnEl, successLabel) {
    const done = () => {
      if (!btnEl) return;
      const orig = btnEl.innerHTML;
      btnEl.textContent = successLabel || "✓ Copied!";
      setTimeout(() => {
        btnEl.innerHTML = orig;
      }, 2000);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(() => {
        fallbackCopy(text);
        done();
      });
    } else {
      fallbackCopy(text);
      done();
    }
  }

  function fallbackCopy(text) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(ta);
  }

  function ensureShareModal() {
    let backdrop = document.getElementById("fl-share-backdrop");
    if (backdrop) return backdrop;

    backdrop = document.createElement("div");
    backdrop.id = "fl-share-backdrop";
    backdrop.className = "fl-share-backdrop no-print";
    backdrop.setAttribute("role", "dialog");
    backdrop.setAttribute("aria-modal", "true");
    backdrop.setAttribute("aria-labelledby", "fl-share-modal-title");

    backdrop.innerHTML = `
      <div class="fl-share-modal">
        <div class="fl-share-header">
          <h3 id="fl-share-modal-title">${SVGS.share} <span>Freely Share Books &amp; Articles (Matthew 10:8)</span></h3>
          <button type="button" class="drawer-close" id="fl-share-close-btn">✕ Close</button>
        </div>
        <div class="fl-share-body">
          <p class="fl-share-lead">
            Every book, article, and Scripture tool on <strong>Foundations Library</strong> is <strong>100% free to read, print, duplicate, and share</strong>—with zero paywalls, ads, or tracking pixels. <strong>Share everything freely</strong> with your family, friends, pastor, church, youth group, homeschool co-op, or neighbors!
          </p>

          <div class="fl-share-url-row">
            <input type="text" id="fl-share-url-input" class="fl-share-url-input" readonly aria-label="Shareable URL" />
            <button type="button" id="fl-share-copy-url-btn" class="fl-btn fl-btn-primary">${SVGS.copy} <span>Copy Link</span></button>
            <button type="button" id="fl-share-copy-blurb-btn" class="fl-btn fl-btn-support">${SVGS.blurb} <span>Copy Blurb + Link</span></button>
          </div>

          <div class="fl-share-grid" id="fl-share-channels"></div>

          <div class="fl-share-qr-strip">
            <img id="fl-share-qr-img" src="https://quickchart.io/qr?format=svg&margin=1&size=140&text=https%3A%2F%2Fmt-sin.ai%2Ffl%2F" alt="Scan QR Code to Open on Phone" />
            <div>
              <strong id="fl-share-qr-title">Scan to Share in Person</strong><br/>
              <span style="font-size:12px;color:var(--muted);">Hold up your screen so a friend at church, small group, or a coffee shop can scan this QR code right from your device.</span>
            </div>
          </div>

          <details class="fl-cobrand-studio" id="fl-cobrand-details">
            <summary>
              <span>⛪ Church, Ministry &amp; Homeschool Co-op Co-Brand Studio (Click to Customize)</span>
              <span style="font-size:11.5px;color:var(--link);">Customize Colors, Font &amp; Logo ▾</span>
            </summary>
            <div class="fl-cobrand-form">
              <label class="fl-cobrand-field">
                <span>Church / Ministry / Co-op Name:</span>
                <input type="text" id="fl-cb-church" placeholder="e.g., Conrad Mission Church" />
              </label>
              <label class="fl-cobrand-field">
                <span>City &amp; State:</span>
                <input type="text" id="fl-cb-city" placeholder="e.g., Conrad, MT" />
              </label>
              <label class="fl-cobrand-field">
                <span>Header Font Style:</span>
                <select id="fl-cb-font">
                  <option value="">Classic Library Serif (Cinzel / Georgia)</option>
                  <option value="merriweather">Traditional Book Serif (Merriweather)</option>
                  <option value="sans">Clean Modern Sans-Serif (System UI)</option>
                </select>
              </label>
              <label class="fl-cobrand-field">
                <span>Logo URL (or Upload Below):</span>
                <input type="url" id="fl-cb-logo-url" placeholder="https://example.org/logo.png" />
              </label>
              <label class="fl-cobrand-field" style="grid-column: 1 / -1;">
                <span>Upload Local Logo Image (Saved in Browser for Instant Preview &amp; Printouts):</span>
                <input type="file" id="fl-cb-logo-file" accept="image/*" />
              </label>
              <div class="fl-cobrand-colors">
                <label class="fl-cobrand-color-item">
                  <input type="color" id="fl-cb-primary" value="#5c4028" />
                  <span>Primary (Header &amp; Accents)</span>
                </label>
                <label class="fl-cobrand-color-item">
                  <input type="color" id="fl-cb-secondary" value="#f5efe6" />
                  <span>Secondary (Callout Boxes)</span>
                </label>
                <label class="fl-cobrand-color-item">
                  <input type="color" id="fl-cb-highlight" value="#b8860b" />
                  <span>Highlight (Borders &amp; Trim)</span>
                </label>
              </div>
              <div class="fl-cobrand-actions">
                <button type="button" id="fl-cb-apply-btn" class="fl-btn fl-btn-primary">✓ Apply &amp; Copy Co-Branded Link</button>
                <button type="button" id="fl-cb-sample-btn" class="fl-btn fl-btn-light">Load Sample (Conrad Mission Church, Conrad, MT)</button>
                <button type="button" id="fl-cb-reset-btn" class="fl-btn fl-btn-outline">Reset to Default FL Theme</button>
              </div>
            </div>
          </details>
        </div>
      </div>
    `;

    document.body.appendChild(backdrop);

    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop || e.target.closest("#fl-share-close-btn")) {
        backdrop.classList.remove("open");
      }
    });

    const logoFileInput = backdrop.querySelector("#fl-cb-logo-file");
    if (logoFileInput) {
      logoFileInput.addEventListener("change", (ev) => {
        const file = ev.target.files && ev.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (loadEv) => {
          const img = new Image();
          img.onload = () => {
            const canvas = document.createElement("canvas");
            const maxH = 56;
            const scale = Math.min(1, maxH / img.height);
            canvas.width = Math.max(1, Math.round(img.width * scale));
            canvas.height = Math.max(1, Math.round(img.height * scale));
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            const dataUrl = canvas.toDataURL("image/png");
            backdrop.setAttribute("data-uploaded-logo", dataUrl);
          };
          img.src = loadEv.target.result;
        };
        reader.readAsDataURL(file);
      });
    }

    return backdrop;
  }

  function openShareModal(triggerEl) {
    const backdrop = ensureShareModal();
    const target = getDefaultShareTarget(triggerEl);

    const urlInput = backdrop.querySelector("#fl-share-url-input");
    const copyUrlBtn = backdrop.querySelector("#fl-share-copy-url-btn");
    const copyBlurbBtn = backdrop.querySelector("#fl-share-copy-blurb-btn");
    const channelsEl = backdrop.querySelector("#fl-share-channels");
    const qrImg = backdrop.querySelector("#fl-share-qr-img");
    const qrTitle = backdrop.querySelector("#fl-share-qr-title");

    const populateLinks = (currentTarget) => {
      const encUrl = encodeURIComponent(currentTarget.url);
      const shareText = `${currentTarget.title} — ${currentTarget.desc}`;
      const fullBlurb = `📖 ${currentTarget.title}\n${currentTarget.desc}\n🔗 Read, print & share freely: ${currentTarget.url}`;
      const encText = encodeURIComponent(shareText);
      const encFull = encodeURIComponent(`${shareText} ${currentTarget.url}`);

      urlInput.value = currentTarget.url;
      qrImg.src = `https://quickchart.io/qr?format=svg&margin=1&size=140&text=${encUrl}`;
      qrTitle.textContent = currentTarget.title;

      copyUrlBtn.onclick = () => copyTextToClipboard(currentTarget.url, copyUrlBtn, "✓ Link Copied!");
      copyBlurbBtn.onclick = () => copyTextToClipboard(fullBlurb, copyBlurbBtn, "✓ Blurb Copied!");

      const canNativeShare = Boolean(navigator.share);
      channelsEl.innerHTML = `
        ${canNativeShare ? `<button type="button" class="fl-share-tile" id="fl-share-native-btn">${SVGS.share} <span>Device Share</span></button>` : ""}
        <a class="fl-share-tile" href="sms:?&body=${encFull}">${SVGS.sms} <span>Text / SMS</span></a>
        <a class="fl-share-tile" href="mailto:?subject=${encodeURIComponent(currentTarget.title)}&body=${encodeURIComponent(fullBlurb)}">${SVGS.email} <span>Email Friend</span></a>
        <a class="fl-share-tile" href="https://x.com/intent/post?text=${encText}&url=${encUrl}" target="_blank" rel="noopener noreferrer">${SVGS.x} <span>Post on X</span></a>
        <a class="fl-share-tile" href="https://www.facebook.com/sharer/sharer.php?u=${encUrl}" target="_blank" rel="noopener noreferrer">${SVGS.facebook} <span>Facebook</span></a>
        <a class="fl-share-tile" href="https://gab.com/compose?url=${encUrl}&text=${encText}" target="_blank" rel="noopener noreferrer">${SVGS.gab} <span>Share on Gab</span></a>
        <a class="fl-share-tile" href="https://truthsocial.com/share?text=${encText}&url=${encUrl}" target="_blank" rel="noopener noreferrer">${SVGS.truth} <span>Truth Social</span></a>
        <a class="fl-share-tile" href="https://t.me/share/url?url=${encUrl}&text=${encText}" target="_blank" rel="noopener noreferrer">${SVGS.telegram} <span>Telegram</span></a>
        <a class="fl-share-tile" href="https://api.whatsapp.com/send?text=${encFull}" target="_blank" rel="noopener noreferrer">${SVGS.whatsapp} <span>WhatsApp</span></a>
        <button type="button" class="fl-share-tile" id="fl-share-print-btn">${SVGS.print} <span>Print Copies</span></button>
      `;

      const nativeBtn = channelsEl.querySelector("#fl-share-native-btn");
      if (nativeBtn) {
        nativeBtn.onclick = () => {
          navigator.share({ title: currentTarget.title, text: currentTarget.desc, url: currentTarget.url }).catch(() => {});
        };
      }
      const printBtn = channelsEl.querySelector("#fl-share-print-btn");
      if (printBtn) {
        printBtn.onclick = () => {
          backdrop.classList.remove("open");
          window.print();
        };
      }
    };

    // Populate Co-Brand Studio inputs with current state
    const cfg = getActiveCoBrandConfig();
    const chInput = backdrop.querySelector("#fl-cb-church");
    const ciInput = backdrop.querySelector("#fl-cb-city");
    const fnSelect = backdrop.querySelector("#fl-cb-font");
    const lgInput = backdrop.querySelector("#fl-cb-logo-url");
    const prInput = backdrop.querySelector("#fl-cb-primary");
    const scInput = backdrop.querySelector("#fl-cb-secondary");
    const hlInput = backdrop.querySelector("#fl-cb-highlight");

    if (chInput) chInput.value = cfg.church || "";
    if (ciInput) ciInput.value = cfg.city || "";
    if (fnSelect) fnSelect.value = cfg.font || "";
    if (lgInput) lgInput.value = (cfg.logo && !cfg.logo.startsWith("data:")) ? cfg.logo : "";
    const toColorInputHex = (h, def) => (h && h.length >= 7 ? h.slice(0, 7) : def);
    if (prInput) prInput.value = toColorInputHex(cfg.primary, "#5c4028");
    if (scInput) scInput.value = toColorInputHex(cfg.secondary, "#f5efe6");
    if (hlInput) hlInput.value = toColorInputHex(cfg.highlight, "#b8860b");

    const applyBtn = backdrop.querySelector("#fl-cb-apply-btn");
    const sampleBtn = backdrop.querySelector("#fl-cb-sample-btn");
    const resetBtn = backdrop.querySelector("#fl-cb-reset-btn");

    if (applyBtn) {
      applyBtn.onclick = () => {
        const uploadedLogo = backdrop.getAttribute("data-uploaded-logo") || "";
        const newCfg = {
          church: (chInput.value || "").trim(),
          city: (ciInput.value || "").trim(),
          font: fnSelect.value || "",
          logo: (lgInput.value || "").trim() || uploadedLogo || cfg.logo || "",
          primary: prInput.value !== "#5c4028" ? prInput.value : (chInput.value ? prInput.value : ""),
          secondary: scInput.value !== "#f5efe6" ? scInput.value : (chInput.value ? scInput.value : ""),
          highlight: hlInput.value !== "#b8860b" ? hlInput.value : (chInput.value ? hlInput.value : "")
        };
        saveStoredCoBrand(newCfg);
        applyCoBrandConfig(newCfg);
        const updatedTarget = getDefaultShareTarget(triggerEl);
        populateLinks(updatedTarget);
        copyTextToClipboard(updatedTarget.url, applyBtn, "✓ Co-Brand Applied & Link Copied!");
      };
    }

    if (sampleBtn) {
      sampleBtn.onclick = () => {
        chInput.value = "Conrad Mission Church";
        ciInput.value = "Conrad, MT";
        fnSelect.value = "sans";
        prInput.value = "#414141";
        scInput.value = "#eafaf9";
        hlInput.value = "#36d9d8";
        applyBtn.click();
      };
    }

    if (resetBtn) {
      resetBtn.onclick = () => {
        backdrop.removeAttribute("data-uploaded-logo");
        saveStoredCoBrand(null);
        chInput.value = "";
        ciInput.value = "";
        fnSelect.value = "";
        lgInput.value = "";
        prInput.value = "#5c4028";
        scInput.value = "#f5efe6";
        hlInput.value = "#b8860b";
        applyCoBrandConfig({});
        populateLinks(getDefaultShareTarget(triggerEl));
      };
    }

    populateLinks(target);
    backdrop.classList.add("open");
  }

  function initDelegatedActions() {
    const drawer = document.getElementById("bible-drawer");
    const frame = document.getElementById("bible-frame");
    const title = document.getElementById("drawer-title");
    const extLink = document.getElementById("drawer-ext");
    const closeBtn = document.getElementById("drawer-close-btn");

    const tierSelect = document.getElementById("fl-support-tier");
    const tierCta = document.getElementById("fl-support-cta");
    if (tierSelect && tierCta) {
      const syncTier = () => {
        tierCta.setAttribute("href", tierSelect.value);
      };
      tierSelect.addEventListener("change", syncTier);
      tierCta.addEventListener("click", (e) => {
        e.preventDefault();
        window.open(tierSelect.value, "_blank", "noopener,noreferrer");
      });
      syncTier();
    }

    window.addEventListener("resize", syncTocAria);
    syncTocAria();

    document.addEventListener("click", (e) => {
      const shareBtn = e.target.closest('[data-fl-action="share-page"]');
      if (shareBtn) {
        e.preventDefault();
        openShareModal(shareBtn);
        return;
      }

      const tocToggleBtn = e.target.closest('[data-fl-action="toggle-toc"]');
      if (tocToggleBtn) {
        e.preventDefault();
        toggleToc();
        return;
      }

      if (document.body.classList.contains("toc-open") && isCompactTocViewport()) {
        const clickedTocLink = e.target.closest(".fl-sidebar a");
        const clickedInsideSidebar = e.target.closest(".fl-sidebar");
        if (clickedTocLink || !clickedInsideSidebar) {
          document.body.classList.remove("toc-open");
          syncTocAria();
        }
      }

      const printPageBtn = e.target.closest('[data-fl-action="print-page"]');
      if (printPageBtn) {
        e.preventDefault();
        window.print();
        return;
      }

      const printAllLabsBtn = e.target.closest('[data-fl-action="print-all-labs"]');
      if (printAllLabsBtn) {
        e.preventDefault();
        printAllLabs();
        return;
      }

      const printLabBtn = e.target.closest("[data-fl-print-lab]");
      if (printLabBtn) {
        e.preventDefault();
        printLab(printLabBtn.getAttribute("data-fl-print-lab"));
        return;
      }

      const clearLabBtn = e.target.closest("[data-fl-clear-lab]");
      if (clearLabBtn) {
        e.preventDefault();
        clearLab(clearLabBtn.getAttribute("data-fl-clear-lab"));
        return;
      }

      const link = e.target.closest(".refs a, a.fl-scripture-link");
      if (!link || !drawer || !frame) return;

      const rawHref = link.getAttribute("href") || "";
      if (!rawHref.includes("365DBR") && !rawHref.includes("bible.html")) return;

      e.preventDefault();
      const targetUrl = normalizeScriptureUrl(rawHref);
      const refLabel = (link.textContent || "Scripture").trim();

      if (title) title.textContent = refLabel;
      if (extLink) extLink.setAttribute("href", targetUrl);

      if (frame.getAttribute("src") !== targetUrl) {
        frame.setAttribute("src", targetUrl);
      }

      withScrollLock(link, () => {
        drawer.classList.add("open");
        drawer.setAttribute("aria-hidden", "false");
        drawer.removeAttribute("inert");
        drawer.inert = false;
        document.body.classList.add("drawer-open");
      });
    });

    if (closeBtn) {
      closeBtn.addEventListener("click", closeReader);
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        const shareBackdrop = document.getElementById("fl-share-backdrop");
        if (shareBackdrop && shareBackdrop.classList.contains("open")) {
          shareBackdrop.classList.remove("open");
        } else if (document.body.classList.contains("toc-open")) {
          document.body.classList.remove("toc-open");
          syncTocAria();
        } else if (drawer && drawer.classList.contains("open")) {
          closeReader();
        }
      }
    });
  }

  function syncEmptyState(el) {
    const val = (el.value || "").trim();
    if (!val) {
      el.classList.add("fl-is-empty");
    } else {
      el.classList.remove("fl-is-empty");
    }
  }

  function initStorageInputs() {
    const inputs = document.querySelectorAll(".fl-persist-input");
    inputs.forEach((el) => {
      const key = el.getAttribute("data-storage-key") || el.id;
      const saved = localStorage.getItem(key);
      if (saved !== null) {
        el.value = saved;
      }
      syncEmptyState(el);
      el.addEventListener("input", () => {
        localStorage.setItem(key, el.value);
        syncEmptyState(el);
        if (el.classList.contains("fl-calc-input")) {
          updateLab2Calculator();
        }
      });
    });
  }

  function updateLab2Calculator() {
    const schoolEl = document.getElementById("fl_edu_calc_school");
    if (!schoolEl) return;

    const schoolWk = parseFloat(schoolEl.value || 0);
    const mediaWk = parseFloat(document.getElementById("fl_edu_calc_media")?.value || 0);
    const personalWk = parseFloat(document.getElementById("fl_edu_calc_personal")?.value || 0);
    const familyWk = parseFloat(document.getElementById("fl_edu_calc_family")?.value || 0);

    const secular12Yr = Math.round((schoolWk * 36 * 12) + (mediaWk * 52 * 12));
    const biblical12Yr = Math.round((personalWk + familyWk) * 52 * 12);
    const total = Math.max(secular12Yr + biblical12Yr, 1);

    const secPct = Math.round((secular12Yr / total) * 100);
    const bibPct = Math.round((biblical12Yr / total) * 100);

    const secValEl = document.getElementById("fl-12yr-secular-val");
    const bibValEl = document.getElementById("fl-12yr-biblical-val");
    const secBarEl = document.getElementById("fl-12yr-secular-bar");
    const bibBarEl = document.getElementById("fl-12yr-biblical-bar");
    const verdictEl = document.getElementById("fl-calc-summary-verdict");

    if (secValEl) secValEl.textContent = `${secular12Yr.toLocaleString()} hrs (${secPct}%)`;
    if (bibValEl) bibValEl.textContent = `${biblical12Yr.toLocaleString()} hrs (${bibPct}%)`;
    if (secBarEl) secBarEl.style.width = `${Math.max(secPct, 2)}%`;
    if (bibBarEl) bibBarEl.style.width = `${Math.max(bibPct, 2)}%`;

    if (verdictEl) {
      const ratio = biblical12Yr > 0 ? (secular12Yr / biblical12Yr).toFixed(1) : "∞";
      verdictEl.textContent = `12-Year Cumulative Audit: ${secular12Yr.toLocaleString()} Secular Hours vs. ${biblical12Yr.toLocaleString()} Hours in God's Word (Personal + Family/Church Partnership) — Ratio: ${ratio} to 1.`;
    }
  }

  function printLab(labId) {
    const target = document.getElementById(labId);
    if (!target) return;
    document.body.classList.add("fl-print-single-lab");
    target.classList.add("fl-lab-target-active");
    window.print();
    setTimeout(() => {
      document.body.classList.remove("fl-print-single-lab");
      target.classList.remove("fl-lab-target-active");
    }, 500);
  }

  function printAllLabs() {
    document.body.classList.add("fl-print-all-labs");
    window.print();
    setTimeout(() => {
      document.body.classList.remove("fl-print-all-labs");
    }, 500);
  }

  function clearLab(labId) {
    const target = document.getElementById(labId);
    if (!target) return;
    const inputs = target.querySelectorAll(".fl-persist-input");
    inputs.forEach((el) => {
      const key = el.getAttribute("data-storage-key") || el.id;
      localStorage.removeItem(key);
      el.value = el.classList.contains("fl-calc-input") ? "0" : "";
      syncEmptyState(el);
    });
    updateLab2Calculator();
  }

  document.addEventListener("DOMContentLoaded", () => {
    runCaseRouterIf404();
    syncTopbarHeight();
    initDelegatedActions();
    initStorageInputs();
    updateLab2Calculator();
    initCoBranding();
  });

  return { printLab, printAllLabs, clearLab, closeReader, toggleToc, openShareModal };
})();
