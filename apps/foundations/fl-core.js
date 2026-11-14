/* ==========================================================================
   Foundations Library (FL) — fl-core.js (100% CSP 'script-src self' Compliant)
   2-Line Topbar Height Sync, Universal TOC Toggle, Scroll-Lock & 365DBR Reader
   ========================================================================== */
const FLApp = (() => {
  const COFFEE_TIP_URL = "#support-coffee";

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

  function initDelegatedActions() {
    const drawer = document.getElementById("bible-drawer");
    const frame = document.getElementById("bible-frame");
    const title = document.getElementById("drawer-title");
    const extLink = document.getElementById("drawer-ext");
    const closeBtn = document.getElementById("drawer-close-btn");

    if (COFFEE_TIP_URL && COFFEE_TIP_URL !== "#support-coffee") {
      document.querySelectorAll(".fl-btn-coffee").forEach((btn) => {
        btn.setAttribute("href", COFFEE_TIP_URL);
        btn.setAttribute("target", "_blank");
        btn.setAttribute("rel", "noopener");
      });
    }

    window.addEventListener("resize", syncTocAria);
    syncTocAria();

    document.addEventListener("click", (e) => {
      // 0. Toggle Left Table of Contents Drawer
      const tocToggleBtn = e.target.closest('[data-fl-action="toggle-toc"]');
      if (tocToggleBtn) {
        e.preventDefault();
        toggleToc();
        return;
      }

      // Auto-close TOC Drawer on Compact Viewports When Clicking a TOC Link or Outside
      if (document.body.classList.contains("toc-open") && isCompactTocViewport()) {
        const clickedTocLink = e.target.closest(".fl-sidebar a");
        const clickedInsideSidebar = e.target.closest(".fl-sidebar");
        if (clickedTocLink || !clickedInsideSidebar) {
          document.body.classList.remove("toc-open");
          syncTocAria();
        }
      }

      // 1. Print Full Page
      const printPageBtn = e.target.closest('[data-fl-action="print-page"]');
      if (printPageBtn) {
        e.preventDefault();
        window.print();
        return;
      }

      // 2. Print All 8 Labs Only (Book 2)
      const printAllLabsBtn = e.target.closest('[data-fl-action="print-all-labs"]');
      if (printAllLabsBtn) {
        e.preventDefault();
        printAllLabs();
        return;
      }

      // 3. Print Single Lab
      const printLabBtn = e.target.closest("[data-fl-print-lab]");
      if (printLabBtn) {
        e.preventDefault();
        printLab(printLabBtn.getAttribute("data-fl-print-lab"));
        return;
      }

      // 4. Clear Single Lab
      const clearLabBtn = e.target.closest("[data-fl-clear-lab]");
      if (clearLabBtn) {
        e.preventDefault();
        clearLab(clearLabBtn.getAttribute("data-fl-clear-lab"));
        return;
      }

      // 5. Scripture Reference Links -> Open Docked 450px 365DBR Scripture Reader (Scroll-Locked)
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
        if (document.body.classList.contains("toc-open")) {
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

  function initCoBranding() {
    const params = new URLSearchParams(window.location.search);
    const church = params.get("church") || params.get("org") || params.get("ministry");
    const city = params.get("city") || "";
    if (!church) return;

    const box = document.getElementById("fl-cobrand-box");
    if (box) {
      box.style.display = "inline-block";
      const label = city ? `${church} (${city})` : church;
      box.textContent = `Provided in partnership with: ${label}`;
      syncTopbarHeight();
    }

    document.querySelectorAll('a[href^="/foundations/"]').forEach((a) => {
      try {
        const url = new URL(a.getAttribute("href"), window.location.origin);
        params.forEach((val, key) => {
          if (["church", "org", "ministry", "city"].includes(key) && !url.searchParams.has(key)) {
            url.searchParams.set(key, val);
          }
        });
        a.setAttribute("href", url.pathname + url.search + url.hash);
      } catch (e) {}
    });
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

  return { printLab, printAllLabs, clearLab, closeReader, toggleToc };
})();