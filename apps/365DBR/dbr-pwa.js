(() => {
  if (!("serviceWorker" in navigator)) return;
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/365DBR/sw.js", { scope: "/365DBR/" })
      .catch((err) => console.warn("[365DBR PWA] SW registration failed:", err));
  });
})();
