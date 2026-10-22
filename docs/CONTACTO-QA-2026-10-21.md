# Formulario corporativo INNOVEN — verificación 2026-10-21

## Publicado

- Sitio: https://innovenca.com/#contacto
- Frontend: a0204fd78d95f436d7b372ae666ff668cd01a899, push a main; GitHub Pages run 39704998798 completado con éxito. El SHA-256 del JS servido coincide con el archivo local.
- API: commit 76274672ed413e18e061177a2aaba40c813cf865 en main de liberti-finance; deployment dpl_5Pf4XNyb8iDUYh4r7CM5g75H9vXS READY, alias https://app.innovenca.com.
- Envío directo mediante Resend dedicado de INNOVEN. Procura y sellado se dirigen a Compras; los demás servicios a Operaciones. Reply-to corresponde al visitante.
- Validación HTML y servidor, CAPTCHA en servidor con hostname limitado, CORS restringido, límite de campos/tamaño/frecuencia, honeypot y clave de idempotencia. No se abre mailto.
- Los errores conservan la información del visitante. El formulario exige respuesta CAPTCHA antes de contactar a la API.

## Comprobado

- Frontend: 8/8 pruebas Node aprobadas, incluyendo inicialización automática, callbacks, estado transitorio del widget, doble envío y recuperación del error.
- Backend: 8/8 pruebas Node aprobadas, incluyendo destinatarios fijos, escape HTML, CAPTCHA inválido, CORS y comprobante del proveedor.
- TypeScript y build del sitio aprobados durante la implementación.
- Producción: preflight autorizado 204, origen ajeno 403, POST vacío 400. Revalidado POST vacío al cerrar esta revisión.
- Clave pública, tipo v2 checkbox y dominios coinciden con la configuración visible de reCAPTCHA de INNOVEN. Ninguna clave privada se documenta aquí.

## Pendiente, no aprobado

La prueba real de dos mensajes técnicos a Compras y Operaciones está autorizada, pero no se completó. Chrome dejó vacío el iframe de Google. El ejemplo mínimo oficial local primero dibujó la casilla y luego también falló al recargarlo. Quitar el backdrop-filter del formulario no resolvió por sí solo la falla. El cambio a inicialización automática tampoco acredita una solución completa en el navegador observado.

No se enviaron los dos mensajes técnicos y no hay comprobantes de entrega de esos mensajes en Resend. No presentar este flujo como verificado de extremo a extremo hasta completar un CAPTCHA válido en producción y comprobar ambas entregas. Se dejó la pestaña de producción con el mensaje técnico de Compras preparado, sin datos comerciales reales.
