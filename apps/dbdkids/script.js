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

let currentClubhouseMode = "dbr";

function buildDbrUrl() {
  return `${getMtSinaiBase()}/365DBR/index.html?mode=kids`;
}

function buildBrowseUrl(ref, openPicker = false) {
  const base = `${getMtSinaiBase()}/365DBR/bible.html?mode=kids`;
  if (!ref) return openPicker ? `${base}&browse=1` : base;
  const parts = String(ref).split(".");
  if (parts.length === 3) {
    return `${base}&book=${encodeURIComponent(parts[0])}&chapter=${encodeURIComponent(parts[1])}&verse=${encodeURIComponent(parts[2])}`;
  }
  return base;
}

function setActiveTab(mode) {
  document.querySelectorAll(".mode-tab").forEach((tab) => {
    const isMatch = tab.dataset.mode === mode;
    tab.classList.toggle("active", isMatch);
    tab.setAttribute("aria-selected", String(isMatch));
  });
}

function updateFullScreenLink(url) {
  const fullLink = document.getElementById("bible-full-link");
  if (fullLink) fullLink.setAttribute("href", url);
}

function loadClubhouseMode(mode, scrollToBible) {
  const frame = document.getElementById("clubhouse-bible-frame");
  if (!frame) return;
  if (mode === "browse" && currentClubhouseMode === "browse" && frame.contentWindow) {
    frame.contentWindow.postMessage({ type: "dbr-open-browse" }, getMtSinaiBase());
    setActiveTab("browse");
    if (scrollToBible) {
      const bibleSection = document.getElementById("bible");
      if (bibleSection) bibleSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    return;
  }
  const url = mode === "browse" ? buildBrowseUrl(null, true) : buildDbrUrl();
  currentClubhouseMode = mode;
  frame.src = url;
  setActiveTab(mode);
  updateFullScreenLink(url);
  document.querySelectorAll(".verse-btn").forEach((btn) => btn.classList.remove("active"));

  if (scrollToBible) {
    const bibleSection = document.getElementById("bible");
    if (bibleSection) bibleSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function loadClubhouseVerse(ref, scrollToBible) {
  const frame = document.getElementById("clubhouse-bible-frame");
  if (!frame) return;
  const url = buildBrowseUrl(ref);
  currentClubhouseMode = "browse";
  frame.src = url;
  setActiveTab("browse");
  updateFullScreenLink(url);

  document.querySelectorAll(".verse-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.ref === ref);
  });

  if (scrollToBible) {
    const bibleSection = document.getElementById("bible");
    if (bibleSection) bibleSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

const TOUR_STEPS = [
  {
    title: "Step 1: How Bible Addresses Work",
    body: "Every verse has an address: Book, Chapter, and Verse. For example, Ephesians 6:11 means the book of Ephesians, chapter 6, verse 11! Tap 'Try It Now!' to jump straight there.",
    actionLabel: "Jump to Ephesians 6:11",
    run: () => loadClubhouseVerse("EPH.6.11", false),
  },
  {
    title: "Step 2: Read Day by Day (DBR)",
    body: "Use the 'Daily Reading' tab to read a little bit of God's Word every day. Tip: click inside the Bible and press the Up (↑) and Down (↓) arrow keys on your keyboard to step cleanly one verse at a time!",
    actionLabel: "Open Today's Reading",
    run: () => loadClubhouseMode("dbr", false),
  },
  {
    title: "Step 3: Listen & Save Bookmarks",
    body: "Want to hear God's Word read out loud? Tap the bright yellow LISTEN button at the top right of the Bible. Found a favorite verse? Tap the little bookmark icon next to it to save up to 5 colored bookmarks!",
    actionLabel: "Open Psalm 119:105",
    run: () => loadClubhouseVerse("PSA.119.105", false),
  },
  {
    title: "Step 4: Bekah's Explorer Challenge",
    body: "Now it's your turn! Tap '📖 Look it Up!' above the Bible to pick Old or New Testament, then any book, chapter, and verse—and check God's Word for yourself!",
    actionLabel: "Tap 📖 Look it Up!",
    run: () => loadClubhouseMode("browse", false),
  },
];

document.addEventListener("DOMContentLoaded", () => {
  const base = getMtSinaiBase();

  document.querySelectorAll("[data-mtsinai-path]").forEach((el) => {
    const relPath = el.getAttribute("data-mtsinai-path");
    if (relPath) el.setAttribute("href", `${base}${relPath}`);
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

  // Default initial load: Daily Bible Reading (respects localStorage last spot or Today)
  loadClubhouseMode("dbr", false);

  // Mode tabs
  document.querySelectorAll(".mode-tab").forEach((tab) => {
    tab.addEventListener("click", () => loadClubhouseMode(tab.dataset.mode, false));
  });

  // Toolbar verse buttons
  document.querySelectorAll(".verse-btn").forEach((btn) => {
    btn.addEventListener("click", () => loadClubhouseVerse(btn.dataset.ref, false));
  });

  // Inline Scripture chips & jump buttons
  document.querySelectorAll(".verse-chip, .verse-jump").forEach((btn) => {
    btn.addEventListener("click", () => loadClubhouseVerse(btn.dataset.ref, true));
  });

  // Bekah's 4-Step Bible Tour
  let tourIdx = 0;
  const tourBox = document.getElementById("bible-tour");
  const tourToggle = document.getElementById("tour-toggle");
  const tourClose = document.getElementById("tour-close");
  const tourTitle = document.getElementById("tour-title");
  const tourBody = document.getElementById("tour-body");
  const tourCounter = document.getElementById("tour-counter");
  const tourPrev = document.getElementById("tour-prev");
  const tourNext = document.getElementById("tour-next");
  const tourTry = document.getElementById("tour-try");

  function renderTour() {
    const step = TOUR_STEPS[tourIdx];
    tourTitle.textContent = step.title;
    tourBody.textContent = step.body;
    tourCounter.textContent = `${tourIdx + 1} / ${TOUR_STEPS.length}`;
    tourPrev.disabled = tourIdx === 0;
    tourNext.textContent = tourIdx === TOUR_STEPS.length - 1 ? "Done ✓" : "Next →";
    tourTry.textContent = step.actionLabel;
  }

  if (tourBox && tourToggle) {
    renderTour();
    tourToggle.addEventListener("click", () => {
      const opening = tourBox.hidden;
      tourBox.hidden = !opening;
      tourToggle.setAttribute("aria-expanded", String(opening));
    });
    tourClose.addEventListener("click", () => {
      tourBox.hidden = true;
      tourToggle.setAttribute("aria-expanded", "false");
    });
    tourPrev.addEventListener("click", () => {
      if (tourIdx > 0) {
        tourIdx -= 1;
        renderTour();
      }
    });
    tourNext.addEventListener("click", () => {
      if (tourIdx < TOUR_STEPS.length - 1) {
        tourIdx += 1;
        renderTour();
      } else {
        tourBox.hidden = true;
        tourToggle.setAttribute("aria-expanded", "false");
      }
    });
    tourTry.addEventListener("click", () => TOUR_STEPS[tourIdx].run());
  }
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch((err) => {
      console.warn("SW registration skipped:", err);
    });
  });
}

// In-Page Full Screen Toggle + Escape Key Support (keeps Kids bar & PWA context)
document.addEventListener("DOMContentLoaded", () => {
  const fsBtn = document.getElementById("bible-full-toggle");
  const bibleSection = document.getElementById("bible");
  if (!fsBtn || !bibleSection) return;

  function setFullScreen(active) {
    bibleSection.classList.toggle("bible-fullscreen", active);
    document.body.classList.toggle("bible-fs-open", active);
    fsBtn.classList.toggle("is-exit", active);
    fsBtn.setAttribute("aria-pressed", String(active));
    fsBtn.textContent = active ? "✕ Exit Full Screen" : "⛶ Full Screen";
  }

  fsBtn.addEventListener("click", () => {
    setFullScreen(!bibleSection.classList.contains("bible-fullscreen"));
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && bibleSection.classList.contains("bible-fullscreen")) {
      setFullScreen(false);
    }
  });

  window.addEventListener("message", (e) => {
    if (e.origin !== getMtSinaiBase()) return;
    if (e.data && e.data.type === "dbr-escape" && bibleSection.classList.contains("bible-fullscreen")) {
      setFullScreen(false);
    }
  });
});
