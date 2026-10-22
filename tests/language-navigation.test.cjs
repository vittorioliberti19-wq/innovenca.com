const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

for (const file of ["index.html", "en/index.html", "fr/index.html", "it/index.html"]) {
  test(`la URL solicitada conserva idioma en ${file} incluso en primera visita`, () => {
    const html = fs.readFileSync(path.join(__dirname, "..", file), "utf8");
    const script = html.split("// BEGIN LANG_INIT")[1].split("// END LANG_INIT")[0];
    for (const browserLanguage of ["es-VE", "en-US", "fr-FR", "it-IT"]) {
      for (const stored of [null, "en", "es"]) {
        const events = new Map();
        const link = { dataset: { lang: "fr" }, addEventListener: (name, cb) => events.set(name, cb) };
        const writes = [];
        const location = { pathname: file === "index.html" ? "/" : `/${file.split("/")[0]}/`, replace: () => assert.fail("automatic redirect") };
        vm.runInNewContext(script, { navigator: { language: browserLanguage }, window: { location }, localStorage: { getItem: () => stored, setItem: (...args) => writes.push(args) }, document: { getElementById: () => null, querySelectorAll: () => [link] } });
        assert.equal(writes.length, 0, "no implicit language choice");
        events.get("click")();
        assert.deepEqual(writes, [["innoven-lang", "fr"]], "manual language selection remains available");
      }
    }
  });
}
