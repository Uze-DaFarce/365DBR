/* ==========================================================================
   Foundations Library (FL) — fl-core.js
   Unified 365DBR Scripture Reader, Co-Branding, LocalStorage & Lab Calculator
   ========================================================================== */
const FLApp = (() => {
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

  function closeReader() {
    const drawer = document.getElementById("bible-drawer");
    if (!drawer) return;
    drawer.classList.remove("open");
    drawer.setAttribute("aria-hidden", "true");
    document.body.classList.remove("drawer-open");
  }

  function initScriptureReader() {
    const drawer = document.getElementById("bible-drawer");
    const frame = document.getElementById("bible-frame");
    const title = document.getElementById("drawer-title");
    const extLink = document.getElementById("drawer-ext");
    const closeBtn = document.getElementById("drawer-close-btn");

    if (!drawer || !frame) return;

    document.addEventListener("click", (e) => {
      const link = e.target.closest(".refs a, a.fl-scripture-link");
      if (!link) return;

      const rawHref = link.getAttribute("href") || "";
      if (!rawHref.includes("365DBR") && !rawHref.includes("bible.html")) return;

      e.preventDefault();
      const targetUrl = normalizeScriptureUrl(rawHref);
      const refLabel = (link.textContent || "Scripture").trim();

      if (title) title.textContent = `${refLabel} — 365DBR Scripture Reader`;
      if (extLink) extLink.setAttribute("href", targetUrl);

      if (frame.hasAttribute("srcdoc")) {
        frame.removeAttribute("srcdoc");
      }
      if (frame.getAttribute("src") !== targetUrl) {
        frame.setAttribute("src", targetUrl);
      }

      drawer.classList.add("open");
      drawer.setAttribute("aria-hidden", "false");
      document.body.classList.add("drawer-open");
    });

    if (closeBtn) {
      closeBtn.addEventListener("click", closeReader);
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && drawer.classList.contains("open")) {
        closeReader();
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
    }

    // Pass ?church= co-branding through to internal Foundations Library links
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
    initScriptureReader();
    initStorageInputs();
    updateLab2Calculator();
    initCoBranding();
  });

  return { printLab, clearLab, closeReader };
})();