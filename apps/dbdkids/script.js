// Day by Day Kids — Clubhouse Hub Controller
function getMtSinaiBase() {
  const host = window.location.hostname;
  if (host === "localhost" || host === "127.0.0.1" || host === "::1" || host === "[::]") {
    return "..";
  }
  if (host === "mt-sin.ai" || host.endsWith(".mt-sin.ai")) {
    return "";
  }
  return "https://mt-sin.ai";
}

function buildBibleUrl(ref) {
  const base = getMtSinaiBase();
  const safeRef = encodeURIComponent(ref || "GEN.1.1");
  return `${base}/365DBR/bible.html?mode=kids&ref=${safeRef}`;
}

function loadClubhouseVerse(ref, scrollToBible) {
  const frame = document.getElementById("clubhouse-bible-frame");
  if (!frame) return;
  frame.src = buildBibleUrl(ref);

  document.querySelectorAll(".verse-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.ref === ref);
  });

  if (scrollToBible) {
    const bibleSection = document.getElementById("bible");
    if (bibleSection) {
      bibleSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const base = getMtSinaiBase();

  // Rewrite cross-app Mt. Sinai links for localhost vs. mt-sin.ai vs. daybydaykids.com
  document.querySelectorAll("[data-mtsinai-path]").forEach((el) => {
    const relPath = el.getAttribute("data-mtsinai-path");
    if (relPath) {
      el.setAttribute("href", `${base}${relPath}`);
    }
  });

  // Mobile menu toggle
  const toggle = document.getElementById("nav-toggle");
  const nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const isOpen = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(isOpen));
    });
    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Initial Clubhouse Bible load
  loadClubhouseVerse("GEN.1.1", false);

  // Toolbar verse buttons
  document.querySelectorAll(".verse-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      loadClubhouseVerse(btn.dataset.ref, false);
    });
  });

  // Inline Scripture chips & jump buttons
  document.querySelectorAll(".verse-chip, .verse-jump").forEach((btn) => {
    btn.addEventListener("click", () => {
      loadClubhouseVerse(btn.dataset.ref, true);
    });
  });
});
