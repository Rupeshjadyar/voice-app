// VoicePro TTS — Service Worker v1.0
// Caches static assets for offline/fast loading

const CACHE_NAME = 'voicepro-v1';
const STATIC_ASSETS = [
  '/',
  '/static/manifest.json',
  '/favicon.png'
];

// Install: cache static files
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(() => {
        // Silently fail if some assets can't be cached (e.g. favicon missing)
      });
    })
  );
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: network first, cache fallback for navigation
// Audio/generate routes ALWAYS go to network (never cached)
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Never cache: API calls, audio generation, temp files
  if (
    url.pathname.startsWith('/generate') ||
    url.pathname.startsWith('/preview-voice') ||
    url.pathname.startsWith('/stats') ||
    url.pathname.startsWith('/temp') ||
    url.pathname.startsWith('/api') ||
    event.request.method !== 'GET'
  ) {
    return; // Let browser handle normally
  }

  // Network first for HTML pages
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() =>
        caches.match('/').then(r => r || fetch(event.request))
      )
    );
    return;
  }

  // Cache first for static assets (fonts, icons, CSS via CDN)
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        // Only cache successful static responses
        if (response && response.status === 200 && response.type === 'basic') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => cached);
    })
  );
});
