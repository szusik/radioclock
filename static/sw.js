var cacheName = 'radioclock';
var filesToCache = [
  '/',
  '/static/style.css',
  '/static/main.js',
  '/static/clock.png',
  '/static/clockoff.png',
  '/static/lulaby.png',
  '/static/musicoff.png',
  '/static/radio.png',
  '/static/volumedown.png',
  '/static/volumeup.png',
  '/static/jquery-3.5.1.min.js'
];

/* Start the service worker and cache all of the app's content */
self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(cacheName).then(function(cache) {
      return cache.addAll(filesToCache);
    })
  );
});

/* Serve cached content when offline */
self.addEventListener('fetch', function(e) {
  console.log(e.request.url)
  e.respondWith(    
    caches.match(e.request).then(function(response) {
      return response || fetch(e.request);
    })
  );
});