const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const root = path.join(__dirname, '..');
const pages = [
  'servicios/aislamiento-integridad-termica/index.html',
  'servicios/refrigeracion-climatizacion-industrial/index.html',
  'servicios/ingenieria-civil-industrial/index.html',
  'servicios/empacaduras-sellado-industrial/index.html',
  'servicios/electricidad-industrial/index.html',
  'servicios/procura-industrial/index.html',
  'morgan-thermal-ceramics-venezuela/index.html',
];

for (const file of pages) {
  test(`${file} incluye contenido comercial y metadatos propios`, () => {
    const html = fs.readFileSync(path.join(root, file), 'utf8');
    assert.match(html, /<link rel="canonical" href="https:\/\/innovenca\.com\//);
    assert.match(html, /Alcances y aplicaciones/);
    assert.match(html, /Proceso orientativo de consulta/);
    assert.match(html, /Datos para solicitar cotización/);
    assert.match(html, /Preguntas frecuentes/);
    assert.match(html, /BreadcrumbList/);
    assert.match(html, /FAQPage/);
  });
}

test('procura usa el valor de formulario existente y Morgan enlaza fuentes primarias', () => {
  const procura = fs.readFileSync(path.join(root, 'servicios/procura-industrial/index.html'), 'utf8');
  const morgan = fs.readFileSync(path.join(root, 'morgan-thermal-ceramics-venezuela/index.html'), 'utf8');
  assert.match(procura, /\?servicio=procura#contacto/);
  assert.match(morgan, /Fuentes del fabricante/);
  assert.match(morgan, /https:\/\/www\.morganthermalceramics\.com\/en-gb\/products-systems\//);
});
