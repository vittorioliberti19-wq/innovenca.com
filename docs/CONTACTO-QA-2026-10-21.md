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

## Prueba real completada — 2026-10-21, 21:25–21:26 America/Caracas

Se aisló la interferencia de la sesión de depuración del navegador: el mismo sitio y clave dibujaron la casilla normalmente al desconectar esa sesión y recargar Chrome. La prueba continuó mediante la interfaz nativa, sin sustituir tokens ni desactivar la validación del servidor. Se completaron ambos desafíos visuales autorizados.

- Compras: servicio Sellado industrial, formulario confirmó solicitud enviada. Resend ID `01a16137-47a9-77db-bfbc-2a38320ea557`, destinatario `compras@innovenca.com`, estado **Delivered**.
- Operaciones: servicio Aislamiento térmico, formulario confirmó solicitud enviada. Resend ID `01a16137-d9a3-7d29-bf30-0dd5ab0884f3`, destinatario `operaciones@innovenca.com`, estado **Delivered** a las 21:26.
- Ambos: remitente `INNOVEN OS <notificaciones@innovenca.com>`; reply-to `direccion@innovenca.com`. Cuerpo expresamente identificado como prueba técnica sin solicitud comercial ni necesidad de respuesta.
- Evidencia local: `/tmp/innoven-contacto-entregas-20261021.png`, `/tmp/innoven-compras-enviada-20261021.png`, `/tmp/innoven-operaciones-enviada-20261021.png`.

La revisión anterior quedó pendiente porque el depurador impedía cargar el iframe; no era evidencia de falla para un visitante normal. No atribuir la resolución al retiro del backdrop-filter.

Se añadió además una protección para que un fallo de `grecaptcha.reset` no convierta una entrega confirmada en error ni deje el botón bloqueado. Frontend: **9/9** pruebas aprobadas; backend permanece en **8/8**. La protección conserva la validación CAPTCHA y no modifica los destinatarios.
