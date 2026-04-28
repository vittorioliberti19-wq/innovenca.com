# PLAN: Internacionalización ES/EN/FR — INNOVEN C.A.

**Status:** EN PROGRESO

## Decisiones tomadas

- **Arquitectura:** 3 archivos HTML separados
  - `/index.html` → ES (default, raíz)
  - `/en/index.html` → EN
  - `/fr/index.html` → FR
- **Selector:** texto "ES / EN / FR" en el nav (no banderas — más B2B sobrio)
- **Orden visual del selector:** ES → EN → FR
- **Traducciones:** las hace Claude (técnico industrial neutro). Mantener nombres propios y datos legales (Morgan Thermal Ceramics, INNOVEN, RIF J-41223462-5, dirección, teléfonos, emails departamentales).
- **Persistencia:** detectar `navigator.language` en primera visita y redirigir a `/en/` o `/fr/` si corresponde; guardar override del usuario en `localStorage` ('innoven-lang').
- **Paths relativos:** `/en/` y `/fr/` usan `../media/`, `../dist/tailwind.css`, `../favicon.png`, `../og-image.jpg`. La raíz mantiene `media/`, `dist/...`. NO usar paths absolutos (regla del proyecto, ver commit `43d906b`).

## Glosario técnico (ES → EN → FR)

| ES                                       | EN                              | FR                                           |
| ---------------------------------------- | ------------------------------- | -------------------------------------------- |
| Servicios Industriales Integrales        | Integrated Industrial Services  | Services Industriels Intégrés                |
| Procura                                  | Procurement                     | Approvisionnement                            |
| Aislamiento e Integridad Térmica         | Thermal Insulation & Integrity  | Isolation et Intégrité Thermiques            |
| Refrigeración y Climatización Industrial | Industrial Refrigeration & HVAC | Réfrigération et Climatisation Industrielles |
| Ingeniería Civil e Industrial            | Civil & Industrial Engineering  | Ingénierie Civile et Industrielle            |
| Empacaduras y Sellado Industrial         | Industrial Gaskets & Sealing    | Joints et Étanchéité Industriels             |
| Sectores                                 | Sectors                         | Secteurs                                     |
| Capacitación Continua                    | Continuous Training             | Formation Continue                           |
| Sobre Nosotros                           | About Us                        | À Propos                                     |
| Misión                                   | Mission                         | Mission                                      |
| Visión                                   | Vision                          | Vision                                       |
| Valores                                  | Values                          | Valeurs                                      |
| Políticas                                | Policies                        | Politiques                                   |
| Calidad                                  | Quality                         | Qualité                                      |
| SIHAO                                    | OHSE Policy                     | Politique HSE                                |
| Clientes                                 | Clients                         | Clients                                      |
| Galería                                  | Gallery                         | Galerie                                      |
| Contacto                                 | Contact                         | Contact                                      |
| Solicitar Cotización                     | Request a Quote                 | Demander un Devis                            |
| Dossier Corporativo                      | Corporate Brochure              | Brochure d'Entreprise                        |
| Postulaciones                            | Careers                         | Carrières                                    |
| Operaciones                              | Operations                      | Opérations                                   |
| Compras y Procura                        | Procurement                     | Achats et Approvisionnement                  |
| Administración                           | Administration                  | Administration                               |
| Recursos Humanos                         | Human Resources                 | Ressources Humaines                          |
| Refractarios                             | Refractories                    | Réfractaires                                 |
| Fire Proofing                            | Fire Proofing                   | Protection Anti-Feu                          |
| Soldadura SMAW/MIG/TIG                   | SMAW/MIG/TIG Welding            | Soudage SMAW/MIG/TIG                         |
| Sandblasting                             | Sandblasting                    | Sablage                                      |
| Empacaduras espirometálicas              | Spiral-Wound Gaskets            | Joints Spiralés                              |
| Hornos refractarios                      | Refractory Furnaces             | Fours Réfractaires                           |
| Empresa venezolana                       | Venezuelan company              | Entreprise vénézuélienne                     |
| En proceso de Certificación              | Under Certification             | En cours de Certification                    |

## Fases (commits)

### Fase 1 — Setup base (DONE)

- [x] Crear `en/` y `fr/` directorios
- [x] Copiar `index.html` → `en/index.html` y `fr/index.html`
- [x] Crear `.claude/PLAN.md`

### Fase 2 — Ajustes de paths + hreflang en `/en/` y `/fr/`

- [ ] Cambiar `<html lang="es-VE">` a `lang="en"` / `lang="fr"`
- [ ] Cambiar todos los `media/` → `../media/`
- [ ] Cambiar `dist/tailwind.css` → `../dist/tailwind.css`
- [ ] Cambiar `favicon.png` → `../favicon.png`
- [ ] Cambiar `og-image.jpg` → `../og-image.jpg`
- [ ] Cambiar `canonical` a `https://innovenca.com/en/` o `/fr/`
- [ ] Cambiar `og:url` y `og:locale` (en_US, fr_FR)
- [ ] Agregar `<link rel="alternate" hreflang="...">` en los 3 archivos (incluido raíz)
- [ ] Cambiar `inLanguage` en JSON-LD WebSite
- [ ] Agregar `availableLanguage` en JSON-LD ContactPoints
- **Commit:** `feat(i18n): scaffold /en/ and /fr/ with hreflang + path fixes`

### Fase 3 — Selector de idioma en nav

- [ ] Agregar bloque "ES / EN / FR" en el nav desktop (entre el último link y el CTA)
- [ ] Agregar el mismo bloque en el menú mobile
- [ ] Estilos: el activo en color brand red, los otros en zinc-400 hover white
- [ ] Wiring: links a `/`, `/en/`, `/fr/` (relativos según ubicación)
- [ ] JS: detectar `navigator.language` en primera visita (sin localStorage previo) y redirigir si corresponde
- [ ] JS: al click, guardar `localStorage.setItem('innoven-lang', 'es'|'en'|'fr')`
- **Commit:** `feat(i18n): language selector + auto-detect`

### Fase 4 — Traducción al inglés

- [ ] `<title>`, meta description, keywords, og titles, twitter
- [ ] JSON-LD Organization: description, knowsAbout (mantener taxID, address, contactPoint)
- [ ] JSON-LD Service descriptions (4 servicios)
- [ ] Nav links
- [ ] Hero (label, stats, headlines)
- [ ] Hero pitch band (headline + paragraph + 3 CTAs)
- [ ] Sobre Nosotros
- [ ] Misión / Visión
- [ ] Servicios (4 cards)
- [ ] Sectores (3 cards)
- [ ] Capacitación
- [ ] Banner Morgan
- [ ] Valores
- [ ] Políticas (Calidad + SIHAO)
- [ ] Clientes (sectores agrupados)
- [ ] Galería (alt texts)
- [ ] Contacto (form labels, options con `data-area` intactos, footer info)
- [ ] Footer
- **Commit:** `feat(i18n): English translation`

### Fase 5 — Traducción al francés

- [ ] Mismo scope que Fase 4 pero en FR
- **Commit:** `feat(i18n): French translation`

### Fase 6 — sitemap.xml + robots.txt

- [ ] Sitemap con 3 URLs y `xhtml:link rel="alternate"` por entry
- [ ] llms.txt — actualizar con disponibilidad multi-idioma
- **Commit:** `feat(i18n): sitemap.xml multilingual entries`

### Fase 7 — Test local

- [ ] `python3 -m http.server 4880` y verificar `/`, `/en/`, `/fr/`
- [ ] Click selector entre los 3 (idas y vueltas)
- [ ] Verificar paths de media cargan en /en/ y /fr/
- [ ] Verificar form submit con data-area en EN/FR
- [ ] Verificar reCAPTCHA renderiza (puede dar Invalid domain — aceptable en localhost)
- [ ] Verificar que `localStorage` persiste

### Fase 8 — Deploy

- [ ] `git push origin main`
- [ ] Esperar GitHub Pages rebuild (~30-60s)
- [ ] Cuando se monte CNAME: agregar `innovenca.com`/`/en/`/`/fr/` a reCAPTCHA admin

## Pendientes deferidos (NO en este sprint)

- **postulaciones.html en EN/FR** — preguntar al usuario al final si quiere
- **Brochure PDF** — mantener `brochure-innoven.pdf` en español; cuando haya versiones EN/FR, agregar como `brochure-innoven-en.pdf` y enlazar según idioma
- **Service worker / cache strategy** — no tiene actualmente, no agregar

## Lecciones del proyecto (recordar)

- Commit por fase, no acumular (commit `6de3fea` se reverteó por reset duro)
- Paths SIEMPRE relativos (sin `/` inicial) por compat GitHub Pages subpath
- Trabajar en `main` directamente — sin branches feature en este repo
