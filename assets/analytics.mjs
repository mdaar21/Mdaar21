// Only public page views and explicit store-button clicks. Never read form values
// or Mdaar's food, weight, training, assistant or profile records.
const id = document.querySelector('meta[name="mdaar-ga4"]')?.content.trim() || '';
const area = document.querySelector('meta[name="mdaar-analytics-area"]')?.content;
const optedOut = navigator.globalPrivacyControl === true || navigator.doNotTrack === '1' || window.doNotTrack === '1';

if (/^G-[A-Z0-9]{6,20}$/.test(id) && ['app', 'showcase'].includes(area) && !optedOut) {
  const base = new URL('../', import.meta.url).pathname;
  const pageLocation = location.origin + base + (area === 'showcase' ? 'discover/' : '');
  let referrer = '';
  try { referrer = new URL(document.referrer).origin + '/'; } catch { /* No referrer. */ }
  const page = {
    page_location: pageLocation,
    page_referrer: referrer,
    page_title: area === 'showcase' ? 'مدار | الواجهة التعريفية' : 'مدار | التطبيق',
    site_area: area
  };
  // Accept conventional campaign labels only, never arbitrary query strings.
  const campaign = {};
  const query = new URLSearchParams(location.search);
  for (const [key, field] of [['utm_source', 'campaign_source'], ['utm_medium', 'campaign_medium'], ['utm_campaign', 'campaign_name']]) {
    const value = query.get(key) || '';
    if (/^[a-zA-Z0-9_-]{1,64}$/.test(value)) campaign[field] = value;
  }
  window.dataLayer = window.dataLayer || [];
  const tag = function () { window.dataLayer.push(arguments); };
  window.gtag = tag;
  tag('js', new Date());
  tag('set', 'ads_data_redaction', true);
  tag('config', id, {
    ...page, ...campaign,
    send_page_view: false,
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    cookie_domain: 'none',
    cookie_path: base,
    cookie_flags: 'SameSite=Lax;Secure'
  });
  tag('event', 'page_view', { ...page, ...campaign, send_to: id });

  const script = document.createElement('script');
  script.async = true;
  script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
  document.head.append(script);

  const product = new URL('https://mdaar21.zid.store/products/بروتوكول-التحول');
  function trackPurchaseClick(event) {
    if (event.type === 'auxclick' && event.button !== 1) return;
    const anchor = event.target instanceof Element ? event.target.closest('a[data-purchase]') : null;
    if (!anchor) return;
    let destination;
    try { destination = new URL(anchor.href); } catch { return; }
    if (destination.origin !== product.origin || destination.pathname !== product.pathname) return;
    let placement = 'other';
    for (const [selector, name] of [['.site-header', 'header'], ['.hero-actions', 'hero'], ['#get-mdaar', 'product'], ['#mobile-purchase', 'mobile'], ['#book-preview', 'preview']]) {
      if (anchor.closest(selector)) { placement = name; break; }
    }
    tag('event', 'purchase_click', {
      ...page, send_to: id,
      link_url: product.href,
      button_placement: placement
    });
    // Never prevent or delay the actual purchase navigation.
  }
  document.addEventListener('click', trackPurchaseClick);
  document.addEventListener('auxclick', trackPurchaseClick);
}
