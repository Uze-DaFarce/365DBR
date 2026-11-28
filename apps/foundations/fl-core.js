/* ==========================================================================
   Foundations Library (FL) — fl-core.js (100% CSP 'script-src self' Compliant)
   2-Line Topbar Height Sync, Universal TOC Toggle, Scroll-Lock,
   12-Way Free Share Modal, Church Co-Brand Studio & 365DBR Reader
   ========================================================================== */
const FLApp = (() => {
  const COBRAND_STORAGE_KEY = "fl_cobrand_config_v1";
  const STUDY_STORAGE_KEY = "fl_study_v1";
  const VALID_HL_COLORS = ["gold", "sage", "rose", "slate"];

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
    if (lower.indexOf("government") !== -1 || lower.indexOf("gov") !== -1) {
      window.location.replace("/foundations/what-does-the-bible-say-about-government.html" + search + hash);
      return;
    }
    if (lower.indexOf("love") !== -1) {
      window.location.replace("/foundations/what-does-the-bible-say-about-love.html" + search + hash);
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
    } else if (path.indexOf("government") !== -1) {
      shortUrl = "https://mt-sin.ai/fl/gov";
      title = "Book 3: What Does the Bible Say About Government? (Foundational Laws, Biblically Backed)";
      desc = "4 Parts, 14 Chapters & 14 printable family study labs on Civil Authority, the Three Jurisdictions, True Law vs. Sharia & Marxism, and America's Constitutional Republic — 100% free to read, print & share.";
    } else if (path.indexOf("love") !== -1) {
      shortUrl = "https://mt-sin.ai/fl/love";
      title = "Book 4: What Does the Bible Say About Love? (Foundational Truths, Biblically Backed)";
      desc = "4 Parts, 12 Chapters, 12 Personal & Family Heart Checks & the 1 Corinthians 13 Love Audit — testing cultural counterfeits against the infallible Word of God. 100% free to read, print & share.";
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
        const studyPop = document.getElementById("fl-study-popover");
        if (studyPop && !studyPop.hidden) {
          studyPop.hidden = true;
          studyPop.removeAttribute("data-active-pid");
          return;
        }
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

    const checkboxes = document.querySelectorAll(".fl-persist-checkbox");
    const syncCheckboxPrint = (cb) => {
      const key = cb.getAttribute("data-storage-key") || cb.id;
      const item = cb.closest(".fl-audit-item");
      if (item) item.classList.toggle("is-checked", cb.checked);
      const printBox = document.querySelector(`[data-print-check="${CSS.escape(key)}"]`);
      if (printBox) printBox.textContent = cb.checked ? "☑" : "☐";
    };
    checkboxes.forEach((cb) => {
      const key = cb.getAttribute("data-storage-key") || cb.id;
      cb.checked = localStorage.getItem(key) === "1";
      syncCheckboxPrint(cb);
      cb.addEventListener("change", () => {
        if (cb.checked) localStorage.setItem(key, "1");
        else localStorage.removeItem(key);
        syncCheckboxPrint(cb);
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
    const checkboxes = target.querySelectorAll(".fl-persist-checkbox");
    checkboxes.forEach((cb) => {
      const key = cb.getAttribute("data-storage-key") || cb.id;
      localStorage.removeItem(key);
      cb.checked = false;
      const item = cb.closest(".fl-audit-item");
      if (item) item.classList.remove("is-checked");
      const printBox = target.querySelector(`[data-print-check="${CSS.escape(key)}"]`);
      if (printBox) printBox.textContent = "☐";
    });
    updateLab2Calculator();
  }

  /* ==========================================================================
     Reader Study Framework (fl_study_v1): Progress, Highlights, Study Notes,
     Print Toggle & Local JSON Backup / Restore (Book 1..N Auto-Inheritance)
     ========================================================================== */
  function sanitizeStudyId(raw) {
    if (typeof raw !== "string") return "";
    const trimmed = raw.trim();
    return /^[a-zA-Z0-9_-]{1,80}$/.test(trimmed) ? trimmed : "";
  }

  function normalizeStudyObject(parsed) {
    const base = {
      schema: "fl_study_v1",
      version: 1,
      updatedAt: (parsed && typeof parsed.updatedAt === "string") ? parsed.updatedAt : "",
      prefs: {
        printStudyNotes: Boolean(parsed && parsed.prefs && parsed.prefs.printStudyNotes)
      },
      books: {}
    };
    if (!parsed || typeof parsed !== "object" || !parsed.books || typeof parsed.books !== "object") {
      return base;
    }
    Object.keys(parsed.books).forEach((rawBookKey) => {
      const bk = sanitizeStudyId(rawBookKey);
      if (!bk) return;
      const src = parsed.books[rawBookKey];
      if (!src || typeof src !== "object") return;
      const completed = Array.isArray(src.completedUnits)
        ? Array.from(new Set(src.completedUnits.map(sanitizeStudyId).filter(Boolean)))
        : [];
      const blocks = {};
      if (src.blocks && typeof src.blocks === "object") {
        Object.keys(src.blocks).forEach((rawPid) => {
          const pid = sanitizeStudyId(rawPid);
          if (!pid) return;
          const b = src.blocks[rawPid];
          if (!b || typeof b !== "object") return;
          const hl = VALID_HL_COLORS.includes(b.hl) ? b.hl : "";
          const note = typeof b.note === "string" ? b.note.slice(0, 20000).trim() : "";
          if (!hl && !note) return;
          blocks[pid] = {
            hl,
            note,
            updatedAt: typeof b.updatedAt === "string" ? b.updatedAt : ""
          };
        });
      }
      base.books[bk] = {
        lastUnit: sanitizeStudyId(src.lastUnit || ""),
        lastPid: sanitizeStudyId(src.lastPid || ""),
        lastTitle: typeof src.lastTitle === "string" ? src.lastTitle.slice(0, 200) : "",
        updatedAt: typeof src.updatedAt === "string" ? src.updatedAt : "",
        completedUnits: completed,
        blocks
      };
    });
    return base;
  }

  function loadStudyState() {
    try {
      const raw = localStorage.getItem(STUDY_STORAGE_KEY);
      if (!raw) return normalizeStudyObject(null);
      return normalizeStudyObject(JSON.parse(raw));
    } catch (e) {
      return normalizeStudyObject(null);
    }
  }

  function saveStudyState(state) {
    try {
      state.schema = "fl_study_v1";
      state.version = 1;
      state.updatedAt = new Date().toISOString();
      localStorage.setItem(STUDY_STORAGE_KEY, JSON.stringify(state));
    } catch (e) {}
  }

  function ensureBookStudyEntry(state, bookId) {
    if (!state.books[bookId]) {
      state.books[bookId] = {
        lastUnit: "",
        lastPid: "",
        lastTitle: "",
        updatedAt: "",
        completedUnits: [],
        blocks: {}
      };
    }
    return state.books[bookId];
  }

  function syncPrintNotesMode(state) {
    const enabled = Boolean(state && state.prefs && state.prefs.printStudyNotes);
    document.body.classList.toggle("fl-print-with-notes", enabled);
    const toggle = document.getElementById("fl-print-notes-toggle");
    if (toggle) toggle.checked = enabled;
  }

  function renderOrUpdateNoteCard(blockEl, bookId, pid, openEditor) {
    const state = loadStudyState();
    const bEntry = ensureBookStudyEntry(state, bookId);
    const blkData = bEntry.blocks[pid] || { hl: "", note: "" };
    const savedNote = (blkData.note || "").trim();

    let card = blockEl.nextElementSibling;
    if (!card || !card.classList.contains("fl-study-note-card") || card.getAttribute("data-note-for") !== pid) {
      card = null;
    }

    if (!savedNote && !openEditor) {
      if (card) card.remove();
      blockEl.classList.remove("has-study-note");
      return;
    }

    if (!card) {
      card = document.createElement("div");
      card.className = "fl-study-note-card";
      card.setAttribute("data-note-for", pid);
      blockEl.insertAdjacentElement("afterend", card);
    }

    card.innerHTML = "";
    card.classList.toggle("has-saved-note", Boolean(savedNote));
    blockEl.classList.toggle("has-study-note", Boolean(savedNote));

    const header = document.createElement("div");
    header.className = "fl-study-note-header";
    const titleSpan = document.createElement("span");
    titleSpan.textContent = "📝 Study Note";
    header.appendChild(titleSpan);

    if (!openEditor && savedNote) {
      const actions = document.createElement("div");
      actions.className = "fl-study-note-actions no-print";

      const editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.className = "fl-study-note-linkbtn";
      editBtn.textContent = "Edit";
      editBtn.addEventListener("click", () => renderOrUpdateNoteCard(blockEl, bookId, pid, true));

      const delBtn = document.createElement("button");
      delBtn.type = "button";
      delBtn.className = "fl-study-note-linkbtn";
      delBtn.textContent = "Delete";
      delBtn.addEventListener("click", () => {
        const nextState = loadStudyState();
        const nextBook = ensureBookStudyEntry(nextState, bookId);
        if (nextBook.blocks[pid]) {
          nextBook.blocks[pid].note = "";
          nextBook.blocks[pid].updatedAt = new Date().toISOString();
          if (!nextBook.blocks[pid].hl) delete nextBook.blocks[pid];
          saveStudyState(nextState);
        }
        renderOrUpdateNoteCard(blockEl, bookId, pid, false);
      });

      actions.appendChild(editBtn);
      actions.appendChild(delBtn);
      header.appendChild(actions);
      card.appendChild(header);

      const textP = document.createElement("p");
      textP.className = "fl-study-note-text";
      textP.textContent = savedNote;
      card.appendChild(textP);
      return;
    }

    card.appendChild(header);
    const editorWrap = document.createElement("div");
    editorWrap.className = "fl-study-note-editor no-print";

    const ta = document.createElement("textarea");
    ta.className = "fl-study-note-textarea";
    ta.rows = 3;
    ta.placeholder = "Write your personal or family study note on this passage (saved privately on this device)...";
    ta.value = savedNote;
    editorWrap.appendChild(ta);

    const btnRow = document.createElement("div");
    btnRow.className = "fl-study-note-editor-btns";

    const saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.className = "fl-btn fl-btn-primary";
    saveBtn.textContent = "Save Study Note";
    saveBtn.addEventListener("click", () => {
      const val = (ta.value || "").trim();
      const nextState = loadStudyState();
      const nextBook = ensureBookStudyEntry(nextState, bookId);
      const existingHl = (nextBook.blocks[pid] && nextBook.blocks[pid].hl) || "";
      const nowIso = new Date().toISOString();
      if (!val && !existingHl) {
        delete nextBook.blocks[pid];
      } else {
        nextBook.blocks[pid] = { hl: existingHl, note: val, updatedAt: nowIso };
      }
      nextBook.updatedAt = nowIso;
      saveStudyState(nextState);
      renderOrUpdateNoteCard(blockEl, bookId, pid, false);
    });

    const cancelBtn = document.createElement("button");
    cancelBtn.type = "button";
    cancelBtn.className = "fl-btn fl-btn-outline";
    cancelBtn.textContent = "Cancel";
    cancelBtn.addEventListener("click", () => {
      renderOrUpdateNoteCard(blockEl, bookId, pid, false);
    });

    btnRow.appendChild(saveBtn);
    btnRow.appendChild(cancelBtn);
    editorWrap.appendChild(btnRow);
    card.appendChild(editorWrap);

    if (savedNote) {
      const printText = document.createElement("p");
      printText.className = "fl-study-note-text print-only";
      printText.textContent = savedNote;
      card.appendChild(printText);
    }

    requestAnimationFrame(() => ta.focus());
  }

  function ensureStudyPopover(bookId) {
    let pop = document.getElementById("fl-study-popover");
    if (pop) return pop;

    pop = document.createElement("div");
    pop.id = "fl-study-popover";
    pop.className = "fl-study-popover no-print";
    pop.hidden = true;
    pop.setAttribute("role", "toolbar");
    pop.setAttribute("aria-label", "Passage Highlight and Study Note Options");

    const colorLabels = {
      gold: "Warm Gold Highlight",
      sage: "Olive Sage Highlight",
      rose: "Crimson Rose Highlight",
      slate: "Slate Blue Highlight"
    };

    VALID_HL_COLORS.forEach((c) => {
      const sw = document.createElement("button");
      sw.type = "button";
      sw.className = "fl-hl-swatch";
      sw.setAttribute("data-hl-color", c);
      sw.title = colorLabels[c];
      sw.setAttribute("aria-label", colorLabels[c]);
      pop.appendChild(sw);
    });

    const clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.className = "fl-study-pop-btn";
    clearBtn.setAttribute("data-study-pop-action", "clear-hl");
    clearBtn.textContent = "Clear";
    pop.appendChild(clearBtn);

    const sep = document.createElement("span");
    sep.className = "fl-study-pop-sep";
    pop.appendChild(sep);

    const noteBtn = document.createElement("button");
    noteBtn.type = "button";
    noteBtn.className = "fl-study-pop-btn";
    noteBtn.setAttribute("data-study-pop-action", "open-note");
    noteBtn.textContent = "📝 Study Note";
    pop.appendChild(noteBtn);

    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "fl-study-pop-close";
    closeBtn.setAttribute("data-study-pop-action", "close");
    closeBtn.setAttribute("aria-label", "Close Study Options");
    closeBtn.textContent = "✕";
    pop.appendChild(closeBtn);

    document.body.appendChild(pop);

    pop.addEventListener("click", (e) => {
      const pid = pop.getAttribute("data-active-pid") || "";
      if (!pid) return;
      const blockEl = document.querySelector(`[data-pid="${CSS.escape(pid)}"]`);
      if (!blockEl) return;

      const swatch = e.target.closest("[data-hl-color]");
      if (swatch) {
        const chosen = swatch.getAttribute("data-hl-color") || "";
        const state = loadStudyState();
        const bEntry = ensureBookStudyEntry(state, bookId);
        const prev = bEntry.blocks[pid] || { hl: "", note: "" };
        const nextHl = prev.hl === chosen ? "" : chosen;
        const nowIso = new Date().toISOString();

        if (!nextHl && !prev.note) {
          delete bEntry.blocks[pid];
          blockEl.removeAttribute("data-fl-hl");
        } else {
          bEntry.blocks[pid] = { hl: nextHl, note: prev.note || "", updatedAt: nowIso };
          if (nextHl) blockEl.setAttribute("data-fl-hl", nextHl);
          else blockEl.removeAttribute("data-fl-hl");
        }
        bEntry.updatedAt = nowIso;
        saveStudyState(state);
        pop.querySelectorAll("[data-hl-color]").forEach((btn) => {
          btn.classList.toggle("is-active", btn.getAttribute("data-hl-color") === nextHl);
        });
        return;
      }

      const actBtn = e.target.closest("[data-study-pop-action]");
      if (!actBtn) return;
      const act = actBtn.getAttribute("data-study-pop-action");

      if (act === "clear-hl") {
        const state = loadStudyState();
        const bEntry = ensureBookStudyEntry(state, bookId);
        const prev = bEntry.blocks[pid];
        if (prev) {
          prev.hl = "";
          prev.updatedAt = new Date().toISOString();
          if (!prev.note) delete bEntry.blocks[pid];
          saveStudyState(state);
        }
        blockEl.removeAttribute("data-fl-hl");
        pop.hidden = true;
        pop.removeAttribute("data-active-pid");
      } else if (act === "open-note") {
        pop.hidden = true;
        pop.removeAttribute("data-active-pid");
        renderOrUpdateNoteCard(blockEl, bookId, pid, true);
      } else if (act === "close") {
        pop.hidden = true;
        pop.removeAttribute("data-active-pid");
      }
    });

    document.addEventListener("click", (e) => {
      if (pop.hidden) return;
      if (e.target.closest("#fl-study-popover") || e.target.closest(".fl-study-trigger")) return;
      pop.hidden = true;
      pop.removeAttribute("data-active-pid");
    });

    return pop;
  }

  function openStudyPopoverForTrigger(triggerBtn, bookId) {
    const blockEl = triggerBtn.closest("[data-pid]");
    if (!blockEl) return;
    const pid = blockEl.getAttribute("data-pid") || "";
    if (!pid) return;

    const pop = ensureStudyPopover(bookId);
    if (!pop.hidden && pop.getAttribute("data-active-pid") === pid) {
      pop.hidden = true;
      pop.removeAttribute("data-active-pid");
      return;
    }

    const curHl = blockEl.getAttribute("data-fl-hl") || "";
    pop.setAttribute("data-active-pid", pid);
    pop.querySelectorAll("[data-hl-color]").forEach((btn) => {
      btn.classList.toggle("is-active", btn.getAttribute("data-hl-color") === curHl);
    });

    pop.hidden = false;
    const btnRect = triggerBtn.getBoundingClientRect();
    const popRect = pop.getBoundingClientRect();
    let top = btnRect.bottom + 6;
    if (top + popRect.height > window.innerHeight - 16) {
      top = Math.max(8, btnRect.top - popRect.height - 6);
    }
    let left = btnRect.right - popRect.width;
    left = Math.max(8, Math.min(left, window.innerWidth - popRect.width - 8));

    pop.style.top = `${Math.round(top)}px`;
    pop.style.left = `${Math.round(left)}px`;
  }

  function initBookStudyFramework() {
    const bookId = sanitizeStudyId(document.body?.getAttribute("data-fl-book") || "");
    if (!bookId) return;

    const unitLabel = document.body.getAttribute("data-fl-unit-label") || "Chapter";
    const unitLabelPlural = unitLabel + "s";
    const units = Array.from(document.querySelectorAll("[data-fl-unit]"));
    const totalUnits = parseInt(document.body.getAttribute("data-fl-units") || "0", 10) || units.length;

    const initialState = loadStudyState();
    syncPrintNotesMode(initialState);

    window.addEventListener("beforeprint", () => {
      syncPrintNotesMode(loadStudyState());
    });

    // 1. Inject Study Bar at top of .fl-main
    const mainEl = document.querySelector(".fl-main");
    let barProgressText = null;
    let barFill = null;
    if (mainEl && !document.getElementById("fl-study-bar")) {
      const bar = document.createElement("div");
      bar.id = "fl-study-bar";
      bar.className = "fl-study-bar no-print";

      const left = document.createElement("div");
      left.className = "fl-study-bar-left";
      const track = document.createElement("div");
      track.className = "fl-study-mini-track";
      barFill = document.createElement("div");
      barFill.className = "fl-study-mini-fill";
      track.appendChild(barFill);

      barProgressText = document.createElement("strong");
      left.appendChild(track);
      left.appendChild(barProgressText);

      const right = document.createElement("div");
      right.className = "fl-study-bar-right";
      const printLabel = document.createElement("label");
      printLabel.className = "fl-print-notes-label";
      const printCb = document.createElement("input");
      printCb.type = "checkbox";
      printCb.id = "fl-print-notes-toggle";
      printCb.checked = Boolean(initialState.prefs.printStudyNotes);
      printCb.addEventListener("change", () => {
        const st = loadStudyState();
        st.prefs.printStudyNotes = printCb.checked;
        saveStudyState(st);
        syncPrintNotesMode(st);
      });
      const printSpan = document.createElement("span");
      printSpan.textContent = "Include My Study Notes & Highlights in Print";
      printLabel.appendChild(printCb);
      printLabel.appendChild(printSpan);

      const backupLink = document.createElement("a");
      backupLink.href = "/foundations/#fl-study-backup";
      backupLink.className = "fl-study-backup-link";
      backupLink.textContent = "Backup Study Notes ↗";

      right.appendChild(printLabel);
      right.appendChild(backupLink);
      bar.appendChild(left);
      bar.appendChild(right);

      const heroTarget = mainEl.querySelector(".fl-hero-header, .container");
      if (heroTarget) mainEl.insertBefore(bar, heroTarget);
      else mainEl.insertBefore(bar, mainEl.firstChild);
    }

    // 2. Inject TOC Progress Summary inside Table of Contents
    const tocAside = document.querySelector(".fl-sidebar");
    let tocPctLabel = null;
    let tocCountLabel = null;
    let tocFill = null;
    if (tocAside) {
      tocAside.setAttribute("aria-label", "Table of Contents");
      const tocHeading = tocAside.querySelector("h3");
      if (tocHeading && !tocAside.querySelector(".fl-toc-progress")) {
        const tocProg = document.createElement("div");
        tocProg.className = "fl-toc-progress no-print";
        const topRow = document.createElement("div");
        topRow.className = "fl-toc-progress-label";
        tocCountLabel = document.createElement("span");
        tocPctLabel = document.createElement("span");
        topRow.appendChild(tocCountLabel);
        topRow.appendChild(tocPctLabel);

        const track = document.createElement("div");
        track.className = "fl-study-mini-track";
        tocFill = document.createElement("div");
        tocFill.className = "fl-study-mini-fill";
        track.appendChild(tocFill);

        tocProg.appendChild(topRow);
        tocProg.appendChild(track);
        tocHeading.insertAdjacentElement("afterend", tocProg);
      }
    }

    function syncUnitCompletionUI() {
      const st = loadStudyState();
      const bEntry = ensureBookStudyEntry(st, bookId);
      const doneSet = new Set(bEntry.completedUnits);
      const validUnitIds = units.map((u) => u.getAttribute("data-fl-unit")).filter(Boolean);
      const doneCount = validUnitIds.filter((id) => doneSet.has(id)).length;
      const denom = Math.max(totalUnits, 1);
      const pct = Math.min(100, Math.round((doneCount / denom) * 100));

      if (barProgressText) {
        barProgressText.textContent = `${doneCount} of ${totalUnits} ${unitLabelPlural} Complete (${pct}%)`;
      }
      if (barFill) barFill.style.width = `${pct}%`;
      if (tocCountLabel) tocCountLabel.textContent = `${doneCount} / ${totalUnits} Complete`;
      if (tocPctLabel) tocPctLabel.textContent = `${pct}%`;
      if (tocFill) tocFill.style.width = `${pct}%`;

      document.querySelectorAll("li[data-toc-unit]").forEach((li) => {
        const uid = li.getAttribute("data-toc-unit") || "";
        li.classList.toggle("is-completed", doneSet.has(uid));
        li.classList.toggle("is-current", Boolean(bEntry.lastUnit && bEntry.lastUnit === uid));
      });

      document.querySelectorAll(".fl-unit-complete-btn[data-complete-unit]").forEach((btn) => {
        const uid = btn.getAttribute("data-complete-unit") || "";
        const num = btn.getAttribute("data-unit-num") || "";
        const isDone = doneSet.has(uid);
        btn.classList.toggle("is-completed", isDone);
        btn.setAttribute("aria-pressed", isDone ? "true" : "false");
        btn.textContent = isDone
          ? `✓ ${unitLabel} ${num} Completed`
          : `☐ Mark ${unitLabel} ${num} Complete`;
      });
    }

    // 3. Inject Mark Complete buttons per Chapter / Day
    units.forEach((unitEl, idx) => {
      const uid = unitEl.getAttribute("data-fl-unit") || "";
      if (!uid) return;
      const num = unitEl.getAttribute("data-fl-unit-num") || String(idx + 1);
      const wrap = document.createElement("div");
      wrap.className = "fl-unit-complete-bar no-print";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "fl-btn fl-unit-complete-btn";
      btn.setAttribute("data-complete-unit", uid);
      btn.setAttribute("data-unit-num", num);
      btn.addEventListener("click", () => {
        const st = loadStudyState();
        const bEntry = ensureBookStudyEntry(st, bookId);
        const set = new Set(bEntry.completedUnits);
        if (set.has(uid)) set.delete(uid);
        else set.add(uid);
        bEntry.completedUnits = Array.from(set);
        bEntry.lastUnit = uid;
        bEntry.lastTitle = unitEl.getAttribute("data-fl-unit-title") || `${unitLabel} ${num}`;
        bEntry.updatedAt = new Date().toISOString();
        saveStudyState(st);
        syncUnitCompletionUI();
      });
      wrap.appendChild(btn);
      unitEl.appendChild(wrap);
    });

    // 4. Stamp Study Triggers & Restore Highlights / Notes on [data-pid] blocks
    const bInitial = ensureBookStudyEntry(initialState, bookId);
    const pidBlocks = Array.from(document.querySelectorAll("[data-pid]"));
    pidBlocks.forEach((blockEl) => {
      const pid = sanitizeStudyId(blockEl.getAttribute("data-pid") || "");
      if (!pid) return;

      const trig = document.createElement("button");
      trig.type = "button";
      trig.className = "fl-study-trigger no-print";
      trig.setAttribute("aria-label", "Highlight passage or add Study Note");
      trig.title = "Highlight or add Study Note";
      trig.textContent = "✎";
      blockEl.appendChild(trig);

      const savedBlk = bInitial.blocks[pid];
      if (savedBlk) {
        if (VALID_HL_COLORS.includes(savedBlk.hl)) {
          blockEl.setAttribute("data-fl-hl", savedBlk.hl);
        }
        if (savedBlk.note) {
          renderOrUpdateNoteCard(blockEl, bookId, pid, false);
        }
      }
    });

    document.addEventListener("click", (e) => {
      const trig = e.target.closest(".fl-study-trigger");
      if (trig) {
        e.preventDefault();
        e.stopPropagation();
        openStudyPopoverForTrigger(trig, bookId);
      }
    });

    syncUnitCompletionUI();

    // 5. Auto-Save Last-Read Chapter/Block via Debounced IntersectionObserver
    let userHasNavigatedOrScrolled = Boolean(window.location.hash) || window.scrollY > 120;
    window.addEventListener(
      "scroll",
      () => {
        if (window.scrollY > 80) userHasNavigatedOrScrolled = true;
      },
      { passive: true }
    );

    let pendingAnchorEl = null;
    let saveTimer = null;

    function flushReadingProgress() {
      if (!pendingAnchorEl || !userHasNavigatedOrScrolled) return;
      const el = pendingAnchorEl;
      pendingAnchorEl = null;

      const pid = sanitizeStudyId(el.getAttribute("data-pid") || "");
      const unitEl = el.closest("[data-fl-unit]") || (el.hasAttribute("data-fl-unit") ? el : null);
      const unitId = sanitizeStudyId(unitEl ? unitEl.getAttribute("data-fl-unit") || "" : "");
      if (!pid && !unitId) return;

      const st = loadStudyState();
      const bEntry = ensureBookStudyEntry(st, bookId);
      if (pid) bEntry.lastPid = pid;
      if (unitId) {
        bEntry.lastUnit = unitId;
        bEntry.lastTitle = unitEl.getAttribute("data-fl-unit-title") || unitId;
      }
      bEntry.updatedAt = new Date().toISOString();
      saveStudyState(st);

      document.querySelectorAll("li[data-toc-unit]").forEach((li) => {
        li.classList.toggle("is-current", Boolean(bEntry.lastUnit && li.getAttribute("data-toc-unit") === bEntry.lastUnit));
      });
    }

    if ("IntersectionObserver" in window && (pidBlocks.length > 0 || units.length > 0)) {
      const observer = new IntersectionObserver(
        (entries) => {
          if (!userHasNavigatedOrScrolled) return;
          let topCandidate = null;
          let topY = Infinity;
          for (let i = 0; i < entries.length; i++) {
            const ent = entries[i];
            if (ent.isIntersecting && ent.boundingClientRect.top < topY) {
              topY = ent.boundingClientRect.top;
              topCandidate = ent.target;
            }
          }
          if (topCandidate) {
            pendingAnchorEl = topCandidate;
            if (saveTimer) clearTimeout(saveTimer);
            saveTimer = setTimeout(flushReadingProgress, 450);
          }
        },
        { rootMargin: "-85px 0px -62% 0px", threshold: 0.05 }
      );
      pidBlocks.forEach((el) => observer.observe(el));
      units.forEach((el) => observer.observe(el));
    }

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") flushReadingProgress();
    });
  }

  /* ==========================================================================
     Hub Progress Bars, Continue Reading & JSON Export / Import Utility
     ========================================================================== */
  function mergeStudyStates(existing, incoming) {
    const out = normalizeStudyObject(existing);
    const inc = normalizeStudyObject(incoming);
    if (inc.prefs && typeof inc.prefs.printStudyNotes === "boolean") {
      out.prefs.printStudyNotes = out.prefs.printStudyNotes || inc.prefs.printStudyNotes;
    }
    Object.keys(inc.books).forEach((bk) => {
      const srcBook = inc.books[bk];
      const dstBook = ensureBookStudyEntry(out, bk);
      dstBook.completedUnits = Array.from(new Set([...dstBook.completedUnits, ...srcBook.completedUnits]));

      if (!dstBook.updatedAt || (srcBook.updatedAt && srcBook.updatedAt >= dstBook.updatedAt)) {
        if (srcBook.lastUnit) dstBook.lastUnit = srcBook.lastUnit;
        if (srcBook.lastPid) dstBook.lastPid = srcBook.lastPid;
        if (srcBook.lastTitle) dstBook.lastTitle = srcBook.lastTitle;
        if (srcBook.updatedAt) dstBook.updatedAt = srcBook.updatedAt;
      }

      Object.keys(srcBook.blocks).forEach((pid) => {
        const srcBlk = srcBook.blocks[pid];
        const dstBlk = dstBook.blocks[pid];
        if (!dstBlk || !dstBlk.updatedAt || (srcBlk.updatedAt && srcBlk.updatedAt >= dstBlk.updatedAt)) {
          dstBook.blocks[pid] = { ...srcBlk };
        }
      });
    });
    return out;
  }

  function countStudyStats(state) {
    let completed = 0;
    let highlights = 0;
    let notes = 0;
    let booksTouched = 0;
    Object.keys(state.books || {}).forEach((bk) => {
      const b = state.books[bk];
      if (!b) return;
      const cLen = (b.completedUnits || []).length;
      let bHl = 0;
      let bNotes = 0;
      Object.values(b.blocks || {}).forEach((blk) => {
        if (blk && blk.hl) bHl++;
        if (blk && blk.note) bNotes++;
      });
      completed += cLen;
      highlights += bHl;
      notes += bNotes;
      if (cLen > 0 || bHl > 0 || bNotes > 0 || b.lastUnit || b.lastPid) {
        booksTouched++;
      }
    });
    return { completed, highlights, notes, booksTouched };
  }

  function refreshHubStudyUI() {
    const cards = document.querySelectorAll(".book-card[data-fl-book-card]");
    const summaryEl = document.getElementById("fl-study-backup-summary");
    if (!cards.length && !summaryEl) return;

    const state = loadStudyState();

    cards.forEach((card) => {
      const bk = sanitizeStudyId(card.getAttribute("data-fl-book-card") || "");
      if (!bk) return;
      const totalUnits = Math.max(1, parseInt(card.getAttribute("data-fl-units") || "8", 10));
      const unitLabel = card.getAttribute("data-fl-unit-label") || "Chapter";
      const unitPlural = unitLabel + "s";
      const primaryLink = card.querySelector(".book-actions a.fl-btn-primary");
      const baseHref = primaryLink ? (primaryLink.getAttribute("href") || "").split("#")[0] : "";
      const actionsRow = card.querySelector(".book-actions");

      const bData = state.books[bk] || { completedUnits: [], blocks: {}, lastUnit: "", lastPid: "", lastTitle: "" };
      const doneCount = Math.min(totalUnits, (bData.completedUnits || []).length);
      const pct = Math.min(100, Math.round((doneCount / totalUnits) * 100));

      let hlCount = 0;
      let noteCount = 0;
      Object.values(bData.blocks || {}).forEach((blk) => {
        if (blk && blk.hl) hlCount++;
        if (blk && blk.note) noteCount++;
      });

      let progBox = card.querySelector(".fl-card-progress");
      if (!progBox && actionsRow) {
        progBox = document.createElement("div");
        progBox.className = "fl-card-progress no-print";
        actionsRow.insertAdjacentElement("beforebegin", progBox);
      }
      if (progBox) {
        progBox.innerHTML = "";
        const top = document.createElement("div");
        top.className = "fl-card-progress-top";
        const leftSpan = document.createElement("span");
        leftSpan.textContent = `${doneCount} of ${totalUnits} ${unitPlural} Complete`;
        const rightSpan = document.createElement("span");
        rightSpan.textContent = `${pct}%`;
        top.appendChild(leftSpan);
        top.appendChild(rightSpan);

        const track = document.createElement("div");
        track.className = "fl-card-progress-track";
        const fill = document.createElement("div");
        fill.className = "fl-card-progress-fill";
        fill.style.width = `${pct}%`;
        track.appendChild(fill);

        progBox.appendChild(top);
        progBox.appendChild(track);

        const metaParts = [];
        if (bData.lastTitle) metaParts.push(`Last read: ${bData.lastTitle}`);
        if (hlCount > 0) metaParts.push(`${hlCount} Highlight${hlCount === 1 ? "" : "s"}`);
        if (noteCount > 0) metaParts.push(`${noteCount} Study Note${noteCount === 1 ? "" : "s"}`);
        if (metaParts.length > 0) {
          const meta = document.createElement("div");
          meta.className = "fl-card-progress-meta";
          meta.textContent = metaParts.join(" • ");
          progBox.appendChild(meta);
        }
      }

      if (actionsRow && baseHref) {
        let contBtn = actionsRow.querySelector(".fl-btn-continue");
        const anchorId = sanitizeStudyId(bData.lastPid || bData.lastUnit || "");
        if (anchorId) {
          if (!contBtn) {
            contBtn = document.createElement("a");
            contBtn.className = "fl-btn fl-btn-support fl-btn-continue";
            actionsRow.insertBefore(contBtn, actionsRow.firstChild);
          }
          contBtn.setAttribute("href", `${baseHref}#${anchorId}`);
          const shortResume = bData.lastTitle ? bData.lastTitle.split(":")[0] : "";
          contBtn.textContent = shortResume ? `▶ Continue Reading (${shortResume})` : "▶ Continue Reading";
        } else if (contBtn) {
          contBtn.remove();
        }
      }
    });

    if (summaryEl) {
      const stats = countStudyStats(state);
      summaryEl.textContent =
        `Saved privately on this browser: ${stats.completed} completed chapters/days, ` +
        `${stats.highlights} highlight${stats.highlights === 1 ? "" : "s"}, and ` +
        `${stats.notes} study note${stats.notes === 1 ? "" : "s"} (zero cloud tracking).`;
    }
  }

  function initHubStudyFramework() {
    refreshHubStudyUI();

    const exportBtn = document.querySelector('[data-fl-action="export-study-json"]');
    const importTriggerBtn = document.querySelector('[data-fl-action="import-study-json"]');
    const fileInput = document.getElementById("fl-study-import-file");
    const modeSelect = document.getElementById("fl-study-import-mode");
    const statusEl = document.getElementById("fl-study-backup-status");

    const setStatus = (msg, isError) => {
      if (!statusEl) return;
      statusEl.textContent = msg;
      statusEl.classList.toggle("is-error", Boolean(isError));
    };

    if (exportBtn) {
      exportBtn.addEventListener("click", () => {
        const state = loadStudyState();
        state.exportedAt = new Date().toISOString();
        const jsonStr = JSON.stringify(state, null, 2);
        const now = new Date();
        const pad = (n) => String(n).padStart(2, "0");
        const stamp = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
        const filename = `foundations-study-notes-${stamp}.json`;

        const blob = new Blob([jsonStr], { type: "application/json;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 2000);

        const stats = countStudyStats(state);
        setStatus(`✓ Exported ${filename} (${stats.highlights} highlights, ${stats.notes} study notes, ${stats.completed} completed units).`, false);
      });
    }

    if (importTriggerBtn && fileInput) {
      importTriggerBtn.addEventListener("click", () => {
        fileInput.value = "";
        fileInput.click();
      });

      fileInput.addEventListener("change", () => {
        const file = fileInput.files && fileInput.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const rawText = String(reader.result || "");
            const parsed = JSON.parse(rawText);
            if (!parsed || typeof parsed !== "object" || (!parsed.books && parsed.schema !== "fl_study_v1")) {
              setStatus("✕ Invalid file: expected a Foundations Library Study Notes JSON backup.", true);
              return;
            }
            const mode = modeSelect ? modeSelect.value : "merge";
            const nextState = mode === "replace"
              ? normalizeStudyObject(parsed)
              : mergeStudyStates(loadStudyState(), parsed);

            saveStudyState(nextState);
            refreshHubStudyUI();
            initCoBranding();
            const stats = countStudyStats(nextState);
            setStatus(
              `✓ ${mode === "replace" ? "Restored" : "Merged"} backup: ${stats.highlights} highlights, ${stats.notes} study notes, and ${stats.completed} completed units active.`,
              false
            );
          } catch (err) {
            setStatus("✕ Could not read JSON backup file. Please select a valid .json export.", true);
          }
        };
        reader.onerror = () => {
          setStatus("✕ File read failed. Please try selecting the .json file again.", true);
        };
        reader.readAsText(file, "UTF-8");
      });
    }

    window.addEventListener("storage", (e) => {
      if (e.key === STUDY_STORAGE_KEY) {
        refreshHubStudyUI();
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    runCaseRouterIf404();
    syncTopbarHeight();
    initDelegatedActions();
    initStorageInputs();
    updateLab2Calculator();
    initBookStudyFramework();
    initHubStudyFramework();
    initCoBranding();
  });

  return { printLab, printAllLabs, clearLab, closeReader, toggleToc, openShareModal };
})();
