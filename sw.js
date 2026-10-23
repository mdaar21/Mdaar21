/* Cache public application assets only. AI requests and personal data are never cached. */
const CACHE = 'mdaar-pages-v3';
const SHELL = ['/Mdaar21/', '/Mdaar21/index.html', '/Mdaar21/privacy.html', '/Mdaar21/assets/styles.css', '/Mdaar21/assets/app.js', '/Mdaar21/assets/core.mjs', '/Mdaar21/assets/remote-service.mjs', '/Mdaar21/assets/nutrition.mjs', '/Mdaar21/assets/training.mjs', '/Mdaar21/assets/pwa.mjs', '/Mdaar21/assets/assistant.mjs', '/Mdaar21/assets/experience.mjs', '/Mdaar21/assets/brand/program-four.svg', '/Mdaar21/assets/brand/program-five.svg', '/Mdaar21/assets/NotoSansArabic-Bold.ttf', '/Mdaar21/assets/food/protein.svg', '/Mdaar21/assets/food/bowl.svg', '/Mdaar21/assets/food/salad.svg', '/Mdaar21/assets/food/toast.svg', '/Mdaar21/assets/food/fruit.svg', '/Mdaar21/assets/logo.png', '/Mdaar21/assets/NotoSansArabic-Regular.ttf', '/Mdaar21/manifest.webmanifest'];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => (key.startsWith('mdaar-public-') || key.startsWith('mdaar-pages-')) && key !== CACHE).map(key => caches.delete(key)))));
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return;
  const publicAsset = SHELL.includes(url.pathname) || url.pathname.startsWith('/Mdaar21/data/') || url.pathname.startsWith('/Mdaar21/assets/');
  if (!publicAsset) return;
  event.respondWith(fetch(event.request).then(response => {
    if (response.ok && response.type === 'basic' && !response.headers.has('set-cookie')) {
      const copy = response.clone();
      event.waitUntil(caches.open(CACHE).then(cache => cache.put(event.request, copy)));
    }
    return response;
  }).catch(async () => {
    const cached = await caches.match(event.request);
    return cached || new Response('المحتوى غير متاح دون اتصال. افتحه مرة واحدة أثناء الاتصال أولاً.', {status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}});
  }));
});
