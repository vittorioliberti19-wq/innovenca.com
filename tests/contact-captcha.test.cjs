const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "..", "assets", "contact-captcha.js"), "utf8");

class ClassList {
  constructor(values = ["hidden"]) { this.values = new Set(values); }
  toggle(name, force) { force ? this.values.add(name) : this.values.delete(name); }
  contains(name) { return this.values.has(name); }
}

class Element {
  constructor(options = {}) {
    Object.assign(this, options);
    this.listeners = {};
    this.attributes = {};
    this.classList ||= new ClassList();
    this.dataset ||= {};
    this.textContent ||= "";
  }
  addEventListener(type, listener) { this.listeners[type] = listener; }
  fire(type, event = {}) { return this.listeners[type](event); }
  remove() { this.removed = true; }
  reset() { this.resetCalls = (this.resetCalls || 0) + 1; }
  setAttribute(name, value) { this.attributes[name] = value; }
}

function boot({ width = 400, language = "es", valid = true, fetchMock } = {}) {
  const scripts = [], timers = [];
  const status = new Element(), retry = new Element(), submitButton = new Element({ disabled: false });
  const captcha = new Element({ dataset: { sitekey: "site-key", theme: "light" } });
  captcha.parentElement = new Element({ clientWidth: width });
  const form = new Element({
    reportValidity: () => valid,
    querySelector: (selector) => selector === ".g-recaptcha" ? captcha : selector === 'button[type="submit"]' ? submitButton : null,
  });
  const nodes = { "lead-form": form, "captcha-error": status, "captcha-retry": retry };
  const document = { documentElement: { lang: language }, getElementById: (id) => nodes[id], createElement: () => new Element(), head: { appendChild: (script) => scripts.push(script) } };
  const calls = { fetch: [], reset: [], response: "", random: 0 };
  const fields = { nombre: "Ana & Co", empresa: "ACME", email: "ana@example.com", telefono: "+58 412 123", servicio: "sellado", mensaje: "Necesito cotización", website: "", "g-recaptcha-response": "secret-token" };
  const window = {};
  class FakeFormData { constructor() { return Object.entries(fields); } }
  class FakeAbortController { constructor() { this.signal = {}; } abort() { this.aborted = true; } }
  const fetch = fetchMock || (async (_url, init) => ({ ok: true, json: async () => ({ ok: true, submissionId: JSON.parse(init.body).submissionId }) }));
  vm.runInNewContext(source, {
    window, document, FormData: FakeFormData, Object, AbortController: FakeAbortController,
    crypto: { randomUUID: () => `00000000-0000-4000-8000-${String(++calls.random).padStart(12, "0")}` },
    fetch: async (url, init) => { calls.fetch.push({ url, init }); return fetch(url, init); },
    setTimeout: (callback, ms) => { timers.push({ callback, ms, cleared: false }); return timers.length - 1; },
    clearTimeout: (id) => { if (timers[id]) timers[id].cleared = true; },
  });
  function installCaptcha({ response = "captcha-token-1234567890", throws = false } = {}) {
    calls.response = response;
    window.grecaptcha = { reset: (id) => calls.reset.push(id), getResponse: () => { if (throws) throw Error("widget initializing"); return calls.response; } };
  }
  async function submit() {
    let prevented = false;
    await form.fire("submit", { preventDefault: () => { prevented = true; } });
    assert.equal(prevented, true);
  }
  return { calls, captcha, fields, form, installCaptcha, retry, scripts, status, submit, submitButton, timers, window };
}

test("no carga CAPTCHA hasta foco y usa recaptcha.net una sola vez con idioma", () => {
  const page = boot({ language: "fr-FR" });
  assert.equal(page.scripts.length, 0);
  page.form.fire("focusin");
  page.form.fire("pointerdown");
  assert.equal(page.scripts.length, 1);
  assert.equal(page.scripts[0].src, "https://www.recaptcha.net/recaptcha/api.js?onload=innovenCaptchaReady&hl=fr");
});

test("modo automático configura widget compacto y callbacks globales", () => {
  const page = boot({ width: 303 });
  page.form.fire("focusin");
  assert.equal(page.captcha.dataset.size, "compact");
  assert.equal(page.captcha.dataset.callback, "innovenCaptchaSolved");
  assert.equal(page.captcha.dataset.expiredCallback, "innovenCaptchaExpired");
  assert.equal(page.captcha.dataset.errorCallback, "innovenCaptchaError");
  page.installCaptcha();
  page.window.innovenCaptchaReady();
  page.window.innovenCaptchaExpired();
  assert.equal(page.retry.classList.contains("hidden"), false);
  page.retry.fire("click");
  assert.deepEqual(page.calls.reset, [0]);
  page.window.innovenCaptchaError();
  assert.match(page.status.textContent, /No se pudo conectar/);
});

test("error o timeout elimina script y retry permite nueva carga", () => {
  const errorPage = boot();
  errorPage.form.fire("focusin");
  errorPage.scripts[0].onerror();
  assert.equal(errorPage.scripts[0].removed, true);
  errorPage.retry.fire("click");
  assert.equal(errorPage.scripts.length, 2);
  const timeoutPage = boot();
  timeoutPage.form.fire("focusin");
  assert.equal(timeoutPage.timers[0].ms, 20000);
  timeoutPage.timers[0].callback();
  assert.equal(timeoutPage.scripts[0].removed, true);
});

test("campos inválidos o token ausente no hacen fetch", async () => {
  const invalid = boot({ valid: false });
  await invalid.submit();
  assert.equal(invalid.calls.fetch.length, 0);
  const missingToken = boot();
  missingToken.installCaptcha({ response: "" });
  missingToken.window.innovenCaptchaReady();
  await missingToken.submit();
  assert.equal(missingToken.calls.fetch.length, 0);
  assert.match(missingToken.status.textContent, /Completa la verificación/);
});

test("widget automático transitorio no envía hasta que getResponse esté listo", async () => {
  const page = boot();
  page.installCaptcha({ throws: true });
  await page.submit();
  assert.equal(page.calls.fetch.length, 0);
  page.window.innovenCaptchaReady();
  await page.submit();
  assert.equal(page.calls.fetch.length, 0);
});

test("éxito envía JSON, exige submissionId coincidente y limpia formulario", async () => {
  const page = boot();
  page.installCaptcha();
  page.window.innovenCaptchaReady();
  await page.submit();
  assert.equal(page.calls.fetch.length, 1);
  const call = page.calls.fetch[0];
  assert.equal(call.url, "https://app.innovenca.com/api/innoven/contact");
  assert.equal(call.init.method, "POST");
  const payload = JSON.parse(call.init.body);
  assert.equal(payload.captchaToken, "captcha-token-1234567890");
  assert.equal(payload.servicio, "sellado");
  assert.equal(payload.submissionId, "00000000-0000-4000-8000-000000000001");
  assert.equal(page.form.resetCalls, 1);
  assert.deepEqual(page.calls.reset, [0]);
  assert.equal(page.submitButton.disabled, false);
  assert.equal(page.form.attributes["aria-busy"], "false");
  assert.match(page.status.textContent, /Solicitud enviada/);
});

test("fallo conserva valores, reinicia CAPTCHA y desbloquea formulario", async () => {
  const page = boot({ fetchMock: async () => ({ ok: true, json: async () => ({ ok: true, submissionId: "otro-id" }) }) });
  page.installCaptcha();
  page.window.innovenCaptchaReady();
  await page.submit();
  assert.equal(page.form.resetCalls || 0, 0);
  assert.equal(page.fields.nombre, "Ana & Co");
  assert.deepEqual(page.calls.reset, [0]);
  assert.equal(page.submitButton.disabled, false);
  assert.equal(page.form.attributes["aria-busy"], "false");
  assert.equal(page.retry.classList.contains("hidden"), false);
  assert.match(page.status.textContent, /No se pudo confirmar/);
});

test("doble submit mientras envía hace un solo fetch", async () => {
  let release;
  const page = boot({ fetchMock: () => new Promise((resolve) => { release = resolve; }) });
  page.installCaptcha();
  page.window.innovenCaptchaReady();
  const first = page.submit();
  const second = page.submit();
  assert.equal(page.calls.fetch.length, 1);
  const submissionId = JSON.parse(page.calls.fetch[0].init.body).submissionId;
  release({ ok: true, json: async () => ({ ok: true, submissionId }) });
  await Promise.all([first, second]);
  assert.equal(page.calls.fetch.length, 1);
});


test("fallo de reset no cambia el comprobante de envío ni bloquea reintento", async () => {
  const page = boot();
  page.installCaptcha();
  page.window.innovenCaptchaReady();
  page.window.grecaptcha.reset = () => { throw Error("widget unavailable"); };
  await page.submit();
  assert.equal(page.calls.fetch.length, 1);
  assert.match(page.status.textContent, /Solicitud enviada/);
  assert.equal(page.submitButton.disabled, false);
  assert.doesNotThrow(() => page.retry.fire("click"));
  assert.equal(page.retry.classList.contains("hidden"), false);
  assert.match(page.status.textContent, /No se pudo conectar/);
});
