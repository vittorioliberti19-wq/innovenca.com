const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(`${__dirname}/../assets/site-analytics.js`, 'utf8');
function boot({ id = 'G-TEST123', hostname = 'innovenca.com', pathname = '/' } = {}) {
  const scripts = [], listeners = {};
  const window = { innovenAnalyticsConfig: { measurementId: id } };
  const document = {
    title: 'INNOVEN', createElement: () => ({}),
    head: { appendChild: s => scripts.push(s) },
    addEventListener: (name, fn) => { listeners[name] = fn; },
  };
  vm.runInNewContext(source, { window, document, location: { hostname, pathname, origin: `https://${hostname}`, search: '?email=private@example.com', hash: '#secret' }, Date, encodeURIComponent });
  return { window, scripts, listeners, events: () => (window.dataLayer || []).filter(x => x[0] === 'event').map(x => [x[1], x[2]]) };
}
test('no request or event before explicit analytics consent', () => {
  const p = boot();
  assert.equal(p.scripts.length, 0);
  p.window.innovenAnalyticsLeadSent('civil');
  assert.equal(p.events().length, 0);
});
test('consent loads once, sanitizes URL and disables advertising', () => {
  const p = boot(); p.window.innovenAnalytics.setConsent(true); p.window.innovenAnalytics.setConsent(true);
  assert.equal(p.scripts.length, 1);
  assert.equal(p.events().length, 1);
  assert.equal(p.events()[0][1].page_location, 'https://innovenca.com/');
  assert.equal(p.events()[0][1].page_referrer, '');
  const config = p.window.dataLayer.find(x => x[0] === 'config')[2];
  assert.equal(config.allow_google_signals, false);
  assert.equal(config.allow_ad_personalization_signals, false);
});
test('contact clicks contain channel only, never recipient or message', () => {
  const p = boot(); p.window.innovenAnalytics.setConsent(true);
  p.listeners.click({ target: { closest: () => ({ getAttribute: () => 'mailto:private@example.com' }) } });
  const [name, details] = p.events()[1];
  assert.equal(name, 'contact_click'); assert.equal(details.contact_channel, 'email');
  assert.ok(!JSON.stringify(details).includes('private'));
});
test('confirmed lead uses a finite service list and stops after withdrawal', () => {
  const p = boot(); p.window.innovenAnalytics.setConsent(true);
  p.window.innovenAnalyticsLeadSent('private@example.com');
  assert.equal(p.events()[1][0], 'generate_lead'); assert.equal(p.events()[1][1].service, 'otro');
  p.window.innovenAnalytics.setConsent(false); p.window.innovenAnalyticsLeadSent('civil');
  assert.equal(p.events().length, 2);
});
test('unconfigured, private and nonproduction pages never load GA4', () => {
  for (const options of [{ id: '' }, { hostname: 'localhost' }, { pathname: '/admin/' }, { pathname: '/portal.html' }]) {
    const p = boot(options); p.window.innovenAnalytics?.setConsent(true); assert.equal(p.scripts.length, 0);
  }
});
