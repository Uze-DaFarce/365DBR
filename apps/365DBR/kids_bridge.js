// Lazy-loaded ONLY when ?mode=kids is active (zero overhead for adult 365DBR)
(function () {
  const ALLOWED_ORIGINS = new Set([
    "https://daybydaykids.com",
    "https://www.daybydaykids.com",
    "https://mt-sin.ai",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
  ]);

  window.addEventListener("message", (e) => {
    if (!ALLOWED_ORIGINS.has(e.origin)) return;
    if (e.data && e.data.type === "dbr-open-browse") {
      window.dispatchEvent(new CustomEvent("dbr:open-browse"));
    }
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && window !== window.parent) {
      window.parent.postMessage({ type: "dbr-escape" }, "*");
    }
  });
})();
