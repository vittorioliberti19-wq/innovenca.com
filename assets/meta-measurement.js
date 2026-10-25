/* Meta measurement requires a configured Pixel ID and explicit advertising consent. */
window.metaMeasurementConfig = window.metaMeasurementConfig || { metaPixelId: '2570126483450363' };
(function () {
  'use strict';
  if (location.hostname !== 'innovenca.com' && location.hostname !== 'www.innovenca.com') return;
  var path = location.pathname;
  if (/^\/(?:app|admin|panel|portal|login|auth)(?:\/|\.|$)/i.test(path) || /^(?:app|flota|admin|portal)\./i.test(location.hostname) || window.metaMeasurement) return;
  var config = window.metaMeasurementConfig;
  var pixelId = String(config.metaPixelId || '');
  var configured = /^\d{5,25}$/.test(pixelId);
  var key = 'meta-advertising-consent-v1';
  var lifetime = 180 * 24 * 60 * 60 * 1000;
  var allowed = false, analyticsAllowed = false, initialized = false, recorded = false;
  var root, banner, dialog, checkbox, analyticsCheckbox;
  function clearCookies() {
    var host = location.hostname;
    var labels = host.split('.');
    var domains = [''];
    for (var i = 0; i < labels.length - 1; i++) domains.push('.' + labels.slice(i).join('.'));
    var paths = ['/'];
    var parts = location.pathname.split('/');
    for (var n = 1; n < parts.length; n++) paths.push(parts.slice(0, n + 1).join('/'));
    ['_fbp', '_fbc'].forEach(function (name) {
      domains.forEach(function (domain) {
        paths.forEach(function (cookiePath) {
          document.cookie = name + '=; Max-Age=0; path=' + cookiePath + (domain ? '; domain=' + domain : '') + '; SameSite=Lax';
        });
      });
    });
  }
  function safeUrl(value) {
    if (!value) return true;
    try {
      var url = new URL(value, location.href);
      var permitted = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid'];
      if (url.hash) return false;
      return Array.from(url.searchParams.keys()).every(function (key) { return permitted.indexOf(key) !== -1; });
    } catch (_) { return false; }
  }
  function start() {
    if (!configured || !allowed || initialized || !safeUrl(location.href) || !safeUrl(document.referrer)) return;
    initialized = true;
    var fbq = window.fbq;
    if (!fbq) {
      fbq = function () { if (fbq.callMethod) fbq.callMethod.apply(fbq, arguments); else fbq.queue.push(arguments); };
      fbq.push = fbq; fbq.loaded = true; fbq.version = '2.0'; fbq.queue = [];
      window.fbq = fbq; window._fbq = fbq;
    }
    fbq('consent', 'grant');
    fbq('set', 'autoConfig', false, pixelId);
    fbq('init', pixelId);
    fbq('trackSingle', pixelId, 'PageView');
    var script = document.createElement('script');
    script.id = 'site-meta-pixel'; script.async = true;
    script.src = 'https://connect.facebook.net/en_US/fbevents.js';
    document.head.appendChild(script);
  }
  function choose(next, analytics) {
    var withdrawing = (initialized && !next) || (analyticsAllowed && analytics !== true);
    analyticsAllowed = analytics === true;
    if (!analyticsAllowed) {
      document.cookie.split(';').forEach(function (entry) {
        var name = entry.split('=')[0].trim();
        if (!/^_ga(?:_|$)|^_gid$|^_gat(?:_|$)/.test(name)) return;
        ['', '.innovenca.com', '.www.innovenca.com'].forEach(function (domain) {
          document.cookie = name + '=; Max-Age=0; path=/' + (domain ? '; domain=' + domain : '') + '; SameSite=Lax';
        });
      });
    }
    if (window.innovenAnalytics) window.innovenAnalytics.setConsent(analyticsAllowed);
    allowed = next === true; recorded = true;
    try { localStorage.setItem(key, JSON.stringify({ version: 2, advertising: allowed, analytics: analyticsAllowed, expires: Date.now() + lifetime })); } catch (_) { /* Page-only choice when storage is unavailable. */ }
    if (!allowed) { if (initialized && window.fbq) window.fbq('consent', 'revoke'); clearCookies(); }
    if (banner) banner.hidden = true;
    if (dialog && dialog.open) dialog.close();
    if (withdrawing) { location.reload(); return; }
    start();
  }
  function openPreferences() {
    checkbox.checked = allowed;
    analyticsCheckbox.checked = analyticsAllowed;
    if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.setAttribute('open', '');
  }
  function mount() {
    var style = document.createElement('style');
    style.textContent = '#meta-cookie-ui{font:14px/1.5 system-ui,sans-serif;color:#fff}#meta-cookie-ui button{font:inherit;border:1px solid #666;border-radius:6px;padding:9px 13px;background:#202020;color:#fff;cursor:pointer}#meta-cookie-reopen{position:fixed;bottom:12px;left:12px;z-index:2147483000}#meta-cookie-banner{position:fixed;bottom:62px;left:12px;right:12px;max-width:560px;padding:20px;background:#111;border:1px solid #666;border-radius:10px;z-index:2147483001;box-shadow:0 4px 30px #0008}#meta-cookie-ui [hidden]{display:none!important}#meta-cookie-ui p{margin:10px 0}#meta-cookie-ui .choices{display:flex;gap:8px;flex-wrap:wrap}#meta-cookie-dialog{max-width:540px;width:calc(100% - 40px);box-sizing:border-box;padding:24px;background:#111;color:#fff;border:1px solid #666;border-radius:10px;font:14px/1.6 system-ui,sans-serif}#meta-cookie-dialog::backdrop{background:#0009}#meta-cookie-dialog a{color:#9cceff}#meta-cookie-dialog label{display:block;margin:16px 0}';
    document.head.appendChild(style);
    root = document.createElement('div'); root.id = 'meta-cookie-ui';
    var status = 'Con tu permiso, usamos Google Analytics para medir visitas y solicitudes de cotización, y Meta Pixel para medir publicidad. Puedes elegir cada finalidad por separado.';
    root.innerHTML = '<button id="meta-cookie-reopen" type="button">Cookies</button><section id="meta-cookie-banner" aria-label="Preferencias de cookies"><strong>Tú eliges las cookies</strong><p>' + status + ' Puedes rechazar y seguir usando la web.</p><div class="choices"><button type="button" data-choice="accept">Aceptar</button><button type="button" data-choice="reject">Rechazar</button><button type="button" data-choice="preferences">Preferencias</button></div></section><dialog id="meta-cookie-dialog" aria-labelledby="meta-cookie-title"><h2 id="meta-cookie-title">Cookies y medición</h2><p>' + status + '</p><label><input type="checkbox" name="analytics"> Permitir estadísticas de visitas y contactos con Google Analytics</label><p>Solo medimos páginas vistas, clics de contacto y confirmaciones de formulario. No enviamos nombres, correos, teléfonos ni mensajes. Los clics de contacto no equivalen a ventas.</p><label><input type="checkbox" name="advertising"> Permitir medición publicitaria con Meta</label><p>Cuando se active y lo permitas, Meta podrá recibir páginas vistas, dirección IP, datos técnicos del navegador e identificadores de cookies (_fbp y _fbc). No activamos coincidencias avanzadas, eventos de contacto ni seguimiento automático de botones o formularios.</p><p>Guardamos tu elección en este navegador por 180 días. Puedes retirarla aquí: revocamos el permiso, eliminamos las cookies accesibles y recargamos para detener el Pixel. Esto no elimina datos que Meta haya recibido antes.</p><p><a href="/privacidad-medicion.html">Privacidad y medición</a> · <a href="https://www.facebook.com/privacy/policy/" target="_blank" rel="noopener noreferrer">Política de Meta</a></p><div class="choices"><button type="button" data-choice="save">Guardar preferencias</button><button type="button" data-choice="close">Cerrar</button></div></dialog>';
    document.body.appendChild(root);
    banner = root.querySelector('#meta-cookie-banner'); dialog = root.querySelector('#meta-cookie-dialog'); checkbox = root.querySelector('[name=advertising]'); analyticsCheckbox = root.querySelector('[name=analytics]');
    banner.hidden = recorded;
    root.querySelector('#meta-cookie-reopen').addEventListener('click', openPreferences);
    root.addEventListener('click', function (event) {
      var button = event.target.closest('[data-choice]'); if (!button || !root.contains(button)) return;
      var choice = button.getAttribute('data-choice');
      if (choice === 'accept') choose(true, true);
      if (choice === 'reject') choose(false, false);
      if (choice === 'preferences') openPreferences();
      if (choice === 'save') choose(checkbox.checked, analyticsCheckbox.checked);
      if (choice === 'close') dialog.close();
    });
  }
  try {
    var saved = JSON.parse(localStorage.getItem(key));
    if (saved && saved.version === 2 && saved.expires > Date.now() && typeof saved.advertising === 'boolean') { allowed = saved.advertising; analyticsAllowed = saved.analytics === true; recorded = true; }
  } catch (_) { /* Default denied. */ }
  if (!allowed) clearCookies();
  window.metaMeasurement = { setAdvertisingConsent: function (next) { choose(next, analyticsAllowed); }, advertisingAllowed: function () { return allowed; }, configured: configured };
  start();
  if (window.innovenAnalytics) window.innovenAnalytics.setConsent(analyticsAllowed);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, { once: true }); else mount();
})();
