const CACHE_NAME = "dbr-v-20261121_004055";
const SHELL_ASSETS = [
  "/365DBR/",
  "/365DBR/index.html",
  "/365DBR/bible.html",
  "/365DBR/tailwind.prod.css",
  "/365DBR/bible_meta.js",
  "/365DBR/strongs_optional.js",
  "/365DBR/dbr-pwa.js",
  "/365DBR/manifest.webmanifest",
  "/365DBR/icons/icon-192.png",
  "/365DBR/icons/icon-512.png",
  "/365DBR/icons/apple-touch-icon.png",
  "/365DBR/icons/favicon.svg"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k.startsWith("dbr-v-") && k !== CACHE_NAME)
          .map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin || !url.pathname.startsWith("/365DBR/")) {
    return;
  }

  // Network-First with Cache Fallback for HTML navigations
  if (req.mode === "navigate" || url.pathname.endsWith(".html") || url.pathname === "/365DBR/") {
    event.respondWith(
      fetch(req)
        .then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          }
          return res;
        })
        .catch(() => caches.match(req).then((hit) => hit || caches.match("/365DBR/index.html")))
    );
    return;
  }

  // Stale-While-Revalidate for Bible chapter JSONs and ws/ shards
  if (
    url.pathname.endsWith(".json") &&
    (url.pathname.startsWith("/365DBR/data/") || url.pathname.startsWith("/365DBR/ws/"))
  ) {
    event.respondWith(
      caches.open(CACHE_NAME).then((cache) =>
        cache.match(req).then((cached) => {
          const netFetch = fetch(req)
            .then((res) => {
              if (res && res.ok) {
                cache.put(req, res.clone());
              }
              return res;
            })
            .catch(() => cached);
          return cached || netFetch;
        })
      )
    );
    return;
  }

  // Cache-First with Network Fallback for static shell assets
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((res) => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
        }
        return res;
      });
    })
  );
});
