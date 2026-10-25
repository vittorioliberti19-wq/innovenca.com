/* Optional GA4 measurement. No requests or cookies before analytics consent. */
window.innovenAnalyticsConfig = window.innovenAnalyticsConfig || { measurementId: 'G-Q60421FPQZ' };
(function () {
  'use strict';
  if (!['innovenca.com', 'www.innovenca.com'].includes(location.hostname)) return;
  if (/^\/(app|admin|panel|portal|login|auth)(\/|\.|$)/i.test(location.pathname)) return;
  const id = String(window.innovenAnalyticsConfig.measurementId || '');
  const configured = /^G-[A-Z0-9]+$/.test(id);
  let allowed = false, started = false;
  const services = ['aislamiento', 'climatizacion', 'civil', 'sellado', 'procura', 'electricidad', 'otro'];
  const cleanLocation = location.origin + location.pathname;
  function send(name, details) {
    if (!allowed || !started) return;
    window.gtag('event', name, { ...details, send_to: id, page_location: cleanLocation, page_referrer: '' });
  }
  function start() {
    if (!configured || !allowed || started) return;
    started = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      analytics_storage: 'granted', ad_storage: 'denied',
      ad_user_data: 'denied', ad_personalization: 'denied',
    });
    window.gtag('js', new Date());
    window.gtag('config', id, {
      send_page_view: false, allow_google_signals: false,
      allow_ad_personalization_signals: false, page_location: cleanLocation, page_referrer: '',
    });
    const script = document.createElement('script');
    script.id = 'innoven-ga4'; script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(script);
    send('page_view', { page_title: document.title });
  }
  window.innovenAnalytics = {
    configured,
    setConsent(next) {
      allowed = next === true;
      if (!allowed && started) window.gtag('consent', 'update', { analytics_storage: 'denied' });
      start();
    },
  };
  document.addEventListener('click', function (event) {
    const anchor = event.target.closest?.('a[href]');
    if (!anchor) return;
    const href = anchor.getAttribute('href') || '';
    const channel = /^(https:\/\/(wa\.me|api\.whatsapp\.com)\/)/.test(href) ? 'whatsapp'
      : href.startsWith('tel:') ? 'phone' : href.startsWith('mailto:') ? 'email' : '';
    if (channel) send('contact_click', { contact_channel: channel });
  });
  window.innovenAnalyticsLeadSent = function (service) {
    send('generate_lead', { method: 'contact_form', service: services.includes(service) ? service : 'otro' });
  };
})();
