const CACHE_NAME = 'fl-v-20261128_015524'; // seed_ns=1795856124935449400
const CORE_ASSETS = [
  '/foundations/index.html',
  '/foundations/what-does-the-bible-say-about-god.html',
  '/foundations/what-does-the-bible-say-about-education.html',
  '/foundations/what-does-the-bible-say-about-government.html',
  '/foundations/what-does-the-bible-say-about-love.html',
  '/foundations/fl-core.css?v=6',
  '/foundations/fl-god.css',
  '/foundations/fl-education.css',
  '/foundations/fl-government.css',
  '/foundations/fl-love.css',
  '/foundations/fl-core.js?v=6',
  '/foundations/fl-pwa.js',
  '/foundations/manifest.webmanifest',
  '/foundations/icons/icon-192.png',
  '/foundations/icons/icon-512.png',
  '/foundations/icons/apple-touch-icon.png',
  '/foundations/icons/favicon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET') return;

  // Explicit 365DBR pass-through
  if (url.pathname.startsWith('/365DBR/')) return;

  const isHtml = event.request.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname === '/foundations/';

  if (isHtml) {
    event.respondWith(
      fetch(event.request)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          return res;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((res) => {
        const copy = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return res;
      });
    })
  );
});
