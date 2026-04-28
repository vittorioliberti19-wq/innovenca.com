#!/usr/bin/env python3
"""
INNOVEN C.A. multilingual generator.

Reads `index.html` (Spanish source), injects:
  - hreflang block in <head>
  - language switcher button in nav (desktop) + mobile menu
  - CSS for the switcher inside the <style> block
  - JS for auto-detect + dropdown wiring inside the <script> block

Then writes:
  - index.html      (ES, with all injections)
  - en/index.html   (EN translations + path fixes)
  - fr/index.html   (FR translations + path fixes)
  - it/index.html   (IT translations + path fixes)

Idempotent: re-running replaces the injected blocks instead of duplicating.

Run:  python3 .claude/translate.py
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "index.html")

LANGS = ["en", "fr", "it"]

# -------------------------------------------------------------- markers
HREFLANG_S, HREFLANG_E = "<!-- BEGIN HREFLANG -->", "<!-- END HREFLANG -->"
SW_S, SW_E = "<!-- BEGIN LANG_SWITCHER -->", "<!-- END LANG_SWITCHER -->"
SWM_S, SWM_E = (
    "<!-- BEGIN LANG_SWITCHER_MOBILE -->",
    "<!-- END LANG_SWITCHER_MOBILE -->",
)
JS_S, JS_E = "// BEGIN LANG_INIT", "// END LANG_INIT"
CSS_S, CSS_E = "/* BEGIN LANG_SWITCHER_CSS */", "/* END LANG_SWITCHER_CSS */"


# -------------------------------------------------------------- helpers
def replace_or_insert(text, ms, me, content, anchor, position="after"):
    """If markers exist, replace block. Else insert content before/after anchor."""
    pat = re.compile(re.escape(ms) + r"[\s\S]*?" + re.escape(me))
    block = f"{ms}\n{content}\n{me}"
    if pat.search(text):
        return pat.sub(block.replace("\\", "\\\\"), text)
    if anchor not in text:
        raise SystemExit(f"Anchor not found: {anchor[:120]}")
    if position == "before":
        return text.replace(anchor, block + "\n            " + anchor, 1)
    return text.replace(anchor, anchor + "\n" + block, 1)


# -------------------------------------------------------------- path fixes (apply only to /en/, /fr/, /it/)
PATH_FIXES = [
    ('src="media/', 'src="../media/'),
    ('poster="media/', 'poster="../media/'),
    ('mobile="media/', 'mobile="../media/'),
    ('href="dist/tailwind.css"', 'href="../dist/tailwind.css"'),
    ('href="favicon.png"', 'href="../favicon.png"'),
    ('href="brochure-innoven.pdf"', 'href="../brochure-innoven.pdf"'),
    ('href="postulaciones.html"', 'href="../postulaciones.html"'),
    ('data-lb-src="media/', 'data-lb-src="../media/'),
    ('data-lb-src-mobile="media/', 'data-lb-src-mobile="../media/'),
    ('data-lb-poster="media/', 'data-lb-poster="../media/'),
]

# -------------------------------------------------------------- locale-specific head edits
LOCALE_HEAD = {
    "en": ("en_US", "en"),
    "fr": ("fr_FR", "fr"),
    "it": ("it_IT", "it"),
}


def head_fixes(lang):
    locale, html_lang = LOCALE_HEAD[lang]
    return [
        ('<html lang="es-VE">', f'<html lang="{html_lang}">'),
        (
            '<link rel="canonical" href="https://innovenca.com/" />',
            f'<link rel="canonical" href="https://innovenca.com/{lang}/" />',
        ),
        (
            '<meta property="og:url" content="https://innovenca.com/" />',
            f'<meta property="og:url" content="https://innovenca.com/{lang}/" />',
        ),
        (
            '<meta property="og:locale" content="es_VE" />',
            f'<meta property="og:locale" content="{locale}" />',
        ),
    ]


# -------------------------------------------------------------- hreflang block
HREFLANG_BLOCK = """    <link rel="alternate" hreflang="es" href="https://innovenca.com/" />
    <link rel="alternate" hreflang="en" href="https://innovenca.com/en/" />
    <link rel="alternate" hreflang="fr" href="https://innovenca.com/fr/" />
    <link rel="alternate" hreflang="it" href="https://innovenca.com/it/" />
    <link rel="alternate" hreflang="x-default" href="https://innovenca.com/" />"""

HREFLANG_ANCHOR = '<link rel="canonical" href="https://innovenca.com/" />'

# -------------------------------------------------------------- language switcher (desktop + mobile)
LANG_LIST = [
    ("es", "ES", "Español", "/"),
    ("en", "EN", "English", "/en/"),
    ("fr", "FR", "Français", "/fr/"),
    ("it", "IT", "Italiano", "/it/"),
]


def desktop_switcher(active):
    items = []
    for code, abbr, label, href in LANG_LIST:
        is_active = code == active
        cls = "lang-link" + (" lang-link-active" if is_active else "")
        aria = ' aria-current="page"' if is_active else ""
        items.append(
            f'        <a href="{href}" class="{cls}"{aria} data-lang="{code}">'
            f'<span class="lang-abbr">{abbr}</span>'
            f'<span class="lang-full">{label}</span></a>'
        )
    items_html = "\n".join(items)
    active_abbr = next(abbr for code, abbr, _, _ in LANG_LIST if code == active)
    return f"""<div class="lang-switcher" id="lang-switcher">
      <button id="lang-btn" type="button" class="lang-btn" aria-label="Change language" aria-haspopup="true" aria-expanded="false">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6" d="M12 3a9 9 0 100 18 9 9 0 000-18zM3.5 12h17M12 3a14 14 0 010 18M12 3a14 14 0 000 18"/>
        </svg>
        <span class="lang-current">{active_abbr}</span>
        <svg class="w-3 h-3 lang-chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>
      <div id="lang-menu" class="lang-menu hidden">
{items_html}
      </div>
    </div>"""


def mobile_switcher(active):
    items = []
    for code, abbr, label, href in LANG_LIST:
        is_active = code == active
        cls = "lang-mlink" + (" lang-mlink-active" if is_active else "")
        items.append(
            f'      <a href="{href}" class="{cls}" data-lang="{code}">'
            f'<span class="lang-abbr">{abbr}</span> {label}</a>'
        )
    return f"""<div class="lang-mobile-row">
{chr(10).join(items)}
    </div>"""


DESKTOP_SWITCHER_ANCHOR = '''<button
              id="menu-btn"'''

MOBILE_SWITCHER_ANCHOR = """<nav
        class="px-6 py-10 flex flex-col gap-2 text-2xl font-display font-semibold"
      >"""

# -------------------------------------------------------------- CSS for switcher
SWITCHER_CSS = """      .lang-switcher { position: relative; display: inline-flex; }
      .lang-btn { display: inline-flex; align-items: center; gap: .4rem; padding: .55rem .8rem; font-size: .7rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: rgba(255,255,255,.85); background: transparent; border: 1px solid rgba(255,255,255,.18); border-radius: 2px; cursor: pointer; transition: color .2s ease, border-color .2s ease, background .2s ease; }
      .lang-btn:hover { color: #fff; border-color: rgba(212,32,42,.7); background: rgba(212,32,42,.08); }
      .lang-btn[aria-expanded="true"] { border-color: rgba(212,32,42,.7); background: rgba(212,32,42,.08); }
      .lang-btn[aria-expanded="true"] .lang-chevron { transform: rotate(180deg); }
      .lang-current { font-family: 'Space Grotesk', sans-serif; }
      .lang-chevron { transition: transform .2s ease; }
      .lang-menu { position: absolute; top: calc(100% + 8px); right: 0; min-width: 180px; background: #050505; border: 1px solid rgba(255,255,255,.1); z-index: 70; box-shadow: 0 10px 40px rgba(0,0,0,.6); padding: .25rem 0; }
      .lang-menu.hidden { display: none; }
      .lang-link { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: .65rem 1rem; font-size: .75rem; font-weight: 600; color: rgba(255,255,255,.7); text-decoration: none; transition: background .15s, color .15s; border-bottom: 1px solid rgba(255,255,255,.04); }
      .lang-link:last-child { border-bottom: none; }
      .lang-link:hover { background: rgba(212,32,42,.12); color: #fff; }
      .lang-link-active { color: #d4202a; font-weight: 700; }
      .lang-link .lang-abbr { font-family: 'Space Grotesk', sans-serif; letter-spacing: .12em; }
      .lang-link .lang-full { font-size: .7rem; opacity: .65; font-weight: 400; }
      .lang-mobile-row { display: flex; flex-wrap: wrap; gap: .5rem; padding: 1rem 0 .5rem; border-bottom: 1px solid rgba(255,255,255,.06); margin-bottom: 1.5rem; }
      .lang-mlink { flex: 0 0 auto; padding: .5rem .85rem; font-size: .8rem; font-weight: 600; color: rgba(255,255,255,.7); border: 1px solid rgba(255,255,255,.12); text-decoration: none; transition: all .15s; letter-spacing: .05em; }
      .lang-mlink:hover { color: #fff; border-color: rgba(212,32,42,.7); }
      .lang-mlink-active { background: #d4202a; color: #fff; border-color: #d4202a; }
      .lang-mlink .lang-abbr { font-family: 'Space Grotesk', sans-serif; font-weight: 700; margin-right: .35rem; }"""

CSS_ANCHOR = "      /* Mobile menu */"

# -------------------------------------------------------------- JS auto-detect + dropdown
LANG_JS = """      (function() {
        var STORAGE_KEY = 'innoven-lang';
        var supported = ['es', 'en', 'fr', 'it'];
        var path = window.location.pathname || '/';
        var currentLang = 'es';
        for (var i = 0; i < supported.length; i++) {
          var c = supported[i];
          if (c !== 'es' && (path.indexOf('/' + c + '/') === 0 || path === '/' + c)) {
            currentLang = c; break;
          }
        }
        var stored = null;
        try { stored = localStorage.getItem(STORAGE_KEY); } catch(e) {}
        if (!stored) {
          var browserLang = (navigator.language || 'es').slice(0,2).toLowerCase();
          if (supported.indexOf(browserLang) !== -1 && browserLang !== currentLang) {
            try { localStorage.setItem(STORAGE_KEY, browserLang); } catch(e) {}
            window.location.replace(browserLang === 'es' ? '/' : '/' + browserLang + '/');
            return;
          }
          try { localStorage.setItem(STORAGE_KEY, currentLang); } catch(e) {}
        }
        var btn = document.getElementById('lang-btn');
        var menu = document.getElementById('lang-menu');
        if (btn && menu) {
          btn.addEventListener('click', function(e) {
            e.stopPropagation();
            var isOpen = !menu.classList.contains('hidden');
            menu.classList.toggle('hidden');
            btn.setAttribute('aria-expanded', String(!isOpen));
          });
          document.addEventListener('click', function(e) {
            if (!menu.contains(e.target) && !btn.contains(e.target)) {
              menu.classList.add('hidden');
              btn.setAttribute('aria-expanded', 'false');
            }
          });
        }
        document.querySelectorAll('a[data-lang]').forEach(function(a) {
          a.addEventListener('click', function() {
            try { localStorage.setItem(STORAGE_KEY, a.dataset.lang); } catch(e) {}
          });
        });
      })();"""

JS_ANCHOR = "      // Mobile menu"

# ============================================================ TRANSLATIONS DICT
# Every entry: 'spanish source' -> {'en': ..., 'fr': ..., 'it': ...}
# Order matters: longest/most specific first.

T = {
    # --- <head> meta ---
    "INNOVEN C.A. — Servicios Industriales Integrales y Procura | Maracaibo,\n      Venezuela": {
        "en": "INNOVEN C.A. — Integrated Industrial Services & Procurement | Maracaibo,\n      Venezuela",
        "fr": "INNOVEN C.A. — Services Industriels Intégrés et Approvisionnement | Maracaibo,\n      Venezuela",
        "it": "INNOVEN C.A. — Servizi Industriali Integrati e Approvvigionamento | Maracaibo,\n      Venezuela",
    },
    'content="INNOVEN C.A. — empresa venezolana especializada en servicios industriales integrales y procura para el sector industrial y energético. Aislamiento térmico, refractarios, refrigeración industrial, ingeniería civil, metalmecánica y empacaduras. Representantes oficiales de Morgan Thermal Ceramics."': {
        "en": 'content="INNOVEN C.A. — Venezuelan company specialized in integrated industrial services and procurement for the industrial and energy sectors. Thermal insulation, refractories, industrial refrigeration, civil engineering, metalworking and gaskets. Official partner of Morgan Thermal Ceramics."',
        "fr": 'content="INNOVEN C.A. — entreprise vénézuélienne spécialisée dans les services industriels intégrés et l\'approvisionnement pour les secteurs industriel et énergétique. Isolation thermique, réfractaires, réfrigération industrielle, ingénierie civile, métallurgie et joints. Partenaires officiels de Morgan Thermal Ceramics."',
        "it": 'content="INNOVEN C.A. — azienda venezuelana specializzata in servizi industriali integrati e approvvigionamento per i settori industriale ed energetico. Isolamento termico, refrattari, refrigerazione industriale, ingegneria civile, metalmeccanica e guarnizioni. Partner ufficiali di Morgan Thermal Ceramics."',
    },
    'content="servicios industriales venezuela, aislamiento térmico, refractarios, fire proofing, refrigeración industrial, climatización industrial maracaibo, ingeniería civil industrial, metalmecánica, empacaduras espirometálicas, procura industrial, morgan thermal ceramics venezuela, innoven, contratista industrial zulia"': {
        "en": 'content="industrial services venezuela, thermal insulation, refractories, fire proofing, industrial refrigeration, industrial HVAC maracaibo, civil and industrial engineering, metalworking, spiral-wound gaskets, industrial procurement, morgan thermal ceramics venezuela, innoven, industrial contractor zulia"',
        "fr": 'content="services industriels venezuela, isolation thermique, réfractaires, protection anti-feu, réfrigération industrielle, climatisation industrielle maracaibo, ingénierie civile industrielle, métallurgie, joints spiralés, approvisionnement industriel, morgan thermal ceramics venezuela, innoven, sous-traitant industriel zulia"',
        "it": 'content="servizi industriali venezuela, isolamento termico, refrattari, fire proofing, refrigerazione industriale, climatizzazione industriale maracaibo, ingegneria civile industriale, metalmeccanica, guarnizioni spiralate, approvvigionamento industriale, morgan thermal ceramics venezuela, innoven, appaltatore industriale zulia"',
    },
    'content="INNOVEN C.A. — Servicios Industriales Integrales y Procura"': {
        "en": 'content="INNOVEN C.A. — Integrated Industrial Services & Procurement"',
        "fr": 'content="INNOVEN C.A. — Services Industriels Intégrés et Approvisionnement"',
        "it": 'content="INNOVEN C.A. — Servizi Industriali Integrati e Approvvigionamento"',
    },
    'content="Aislamiento térmico, refractarios, refrigeración industrial, ingeniería civil, metalmecánica y procura para el sector industrial y energético en Venezuela."': {
        "en": 'content="Thermal insulation, refractories, industrial refrigeration, civil engineering, metalworking and procurement for the industrial and energy sectors in Venezuela."',
        "fr": 'content="Isolation thermique, réfractaires, réfrigération industrielle, ingénierie civile, métallurgie et approvisionnement pour les secteurs industriel et énergétique au Venezuela."',
        "it": 'content="Isolamento termico, refrattari, refrigerazione industriale, ingegneria civile, metalmeccanica e approvvigionamento per i settori industriale ed energetico in Venezuela."',
    },
    'content="INNOVEN C.A. — operaciones industriales en planta"': {
        "en": 'content="INNOVEN C.A. — industrial operations on site"',
        "fr": 'content="INNOVEN C.A. — opérations industrielles sur site"',
        "it": 'content="INNOVEN C.A. — operazioni industriali in impianto"',
    },
    'content="Aislamiento térmico, refractarios, refrigeración industrial, ingeniería civil, metalmecánica y procura. Representantes Morgan Thermal Ceramics en Venezuela."': {
        "en": 'content="Thermal insulation, refractories, industrial refrigeration, civil engineering, metalworking and procurement. Morgan Thermal Ceramics partners in Venezuela."',
        "fr": 'content="Isolation thermique, réfractaires, réfrigération industrielle, ingénierie civile, métallurgie et approvisionnement. Partenaires Morgan Thermal Ceramics au Venezuela."',
        "it": 'content="Isolamento termico, refrattari, refrigerazione industriale, ingegneria civile, metalmeccanica e approvvigionamento. Partner Morgan Thermal Ceramics in Venezuela."',
    },
    # --- JSON-LD Organization ---
    '"description": "Empresa venezolana de servicios industriales integrales y procura para el sector industrial y energético. Representantes oficiales de Morgan Advanced Materials – Thermal Ceramics."': {
        "en": '"description": "Venezuelan company providing integrated industrial services and procurement for the industrial and energy sectors. Official partners of Morgan Advanced Materials – Thermal Ceramics."',
        "fr": '"description": "Entreprise vénézuélienne de services industriels intégrés et d\'approvisionnement pour les secteurs industriel et énergétique. Partenaires officiels de Morgan Advanced Materials – Thermal Ceramics."',
        "it": '"description": "Azienda venezuelana di servizi industriali integrati e approvvigionamento per i settori industriale ed energetico. Partner ufficiali di Morgan Advanced Materials – Thermal Ceramics."',
    },
    '"Aislamiento térmico industrial",\n          "Refractarios",\n          "Fire Proofing",\n          "Refrigeración y climatización industrial",\n          "Ingeniería civil e industrial",\n          "Metalmecánica y soldadura",\n          "Empacaduras y sellado industrial",\n          "Procura de materiales y equipos industriales"': {
        "en": '"Industrial thermal insulation",\n          "Refractories",\n          "Fire Proofing",\n          "Industrial refrigeration and HVAC",\n          "Civil and industrial engineering",\n          "Metalworking and welding",\n          "Industrial gaskets and sealing",\n          "Procurement of industrial materials and equipment"',
        "fr": '"Isolation thermique industrielle",\n          "Réfractaires",\n          "Protection Anti-Feu",\n          "Réfrigération et climatisation industrielles",\n          "Ingénierie civile et industrielle",\n          "Métallurgie et soudage",\n          "Joints et étanchéité industriels",\n          "Approvisionnement de matériaux et équipements industriels"',
        "it": '"Isolamento termico industriale",\n          "Refrattari",\n          "Fire Proofing",\n          "Refrigerazione e climatizzazione industriale",\n          "Ingegneria civile e industriale",\n          "Metalmeccanica e saldatura",\n          "Guarnizioni e tenute industriali",\n          "Approvvigionamento di materiali e attrezzature industriali"',
    },
    '"availableLanguage": ["Spanish"]': {
        "en": '"availableLanguage": ["Spanish", "English"]',
        "fr": '"availableLanguage": ["Spanish", "French"]',
        "it": '"availableLanguage": ["Spanish", "Italian"]',
    },
    '"description": "Servicios industriales integrales y procura — Venezuela",': {
        "en": '"description": "Integrated industrial services and procurement — Venezuela",',
        "fr": '"description": "Services industriels intégrés et approvisionnement — Venezuela",',
        "it": '"description": "Servizi industriali integrati e approvvigionamento — Venezuela",',
    },
    '"inLanguage": "es-VE"': {
        "en": '"inLanguage": "en"',
        "fr": '"inLanguage": "fr"',
        "it": '"inLanguage": "it"',
    },
    # --- JSON-LD Services ---
    '"name": "Aislamiento e Integridad Térmica",\n            "serviceType": "Aislamiento térmico industrial, criogénico, acústico, refractarios y Fire Proofing",': {
        "en": '"name": "Thermal Insulation & Integrity",\n            "serviceType": "Industrial thermal, cryogenic and acoustic insulation, refractories and Fire Proofing",',
        "fr": '"name": "Isolation et Intégrité Thermiques",\n            "serviceType": "Isolation thermique industrielle, cryogénique, acoustique, réfractaires et Protection Anti-Feu",',
        "it": '"name": "Isolamento e Integrità Termica",\n            "serviceType": "Isolamento termico industriale, criogenico, acustico, refrattari e Fire Proofing",',
    },
    '"description": "Aislamiento térmico industrial (fibra de vidrio, silicato de calcio, perlita, lana mineral, fibra cerámica), criogénico (Foam Glass, poliuretano, neopreno, poliestireno), acústico, refractarios para hornos y calderas (enladrillado, vaciado, proyectado, apisonado, inyectado) y Fire Proofing — con materiales Morgan Thermal Ceramics."': {
        "en": '"description": "Industrial thermal insulation (fiberglass, calcium silicate, perlite, mineral wool, ceramic fiber), cryogenic (Foam Glass, polyurethane, neoprene, polystyrene), acoustic, refractories for furnaces and boilers (bricking, casting, gunning, ramming, injection) and Fire Proofing — with Morgan Thermal Ceramics materials."',
        "fr": '"description": "Isolation thermique industrielle (fibre de verre, silicate de calcium, perlite, laine minérale, fibre céramique), cryogénique (Foam Glass, polyuréthane, néoprène, polystyrène), acoustique, réfractaires pour fours et chaudières (briquetage, coulage, projection, pilonnage, injection) et Protection Anti-Feu — avec matériaux Morgan Thermal Ceramics."',
        "it": '"description": "Isolamento termico industriale (fibra di vetro, silicato di calcio, perlite, lana minerale, fibra ceramica), criogenico (Foam Glass, poliuretano, neoprene, polistirolo), acustico, refrattari per forni e caldaie (mattonatura, colatura, proiezione, pestonatura, iniezione) e Fire Proofing — con materiali Morgan Thermal Ceramics."',
    },
    '"name": "Refrigeración y Climatización Industrial",\n            "serviceType": "HVAC industrial, A/C de confort, precisión y agua helada",': {
        "en": '"name": "Industrial Refrigeration & HVAC",\n            "serviceType": "Industrial HVAC, comfort, precision and chilled water A/C",',
        "fr": '"name": "Réfrigération et Climatisation Industrielles",\n            "serviceType": "CVC industriel, climatisation de confort, de précision et eau glacée",',
        "it": '"name": "Refrigerazione e Climatizzazione Industriale",\n            "serviceType": "HVAC industriale, A/C comfort, precisione e acqua refrigerata",',
    },
    '"description": "Aire acondicionado de confort, precisión y agua helada para edificios corporativos, centros logísticos y operaciones críticas. Diseño y ejecución de ductería, mantenimiento preventivo y respuesta 24/7/365."': {
        "en": '"description": "Comfort, precision and chilled-water air conditioning for corporate buildings, logistics centers and critical operations. Ductwork design and execution, preventive maintenance and 24/7/365 response."',
        "fr": '"description": "Climatisation de confort, de précision et eau glacée pour bâtiments d\'entreprise, centres logistiques et opérations critiques. Conception et exécution de gainage, maintenance préventive et intervention 24/7/365."',
        "it": '"description": "Aria condizionata di comfort, precisione e acqua refrigerata per edifici aziendali, centri logistici e operazioni critiche. Progettazione ed esecuzione di canalizzazioni, manutenzione preventiva e risposta 24/7/365."',
    },
    '"name": "Ingeniería Civil e Industrial",\n            "serviceType": "Obra civil, metalmecánica, soldadura, tratamiento de superficies, electricidad e instrumentación",': {
        "en": '"name": "Civil & Industrial Engineering",\n            "serviceType": "Civil works, metalworking, welding, surface treatment, electrical and instrumentation",',
        "fr": '"name": "Ingénierie Civile et Industrielle",\n            "serviceType": "Travaux de génie civil, métallurgie, soudage, traitement de surface, électricité et instrumentation",',
        "it": '"name": "Ingegneria Civile e Industriale",\n            "serviceType": "Opere civili, metalmeccanica, saldatura, trattamento superfici, elettricità e strumentazione",',
    },
    '"description": "Construcción y obra civil, movimiento de tierra, impermeabilización y andamios; metalmecánica y estructuras con soldadura SMAW, MIG/MAG y TIG; tratamiento y protección de superficies (sandblasting, pintura industrial, epóxicos, pasivado); instalaciones eléctricas e instrumentación."': {
        "en": '"description": "Construction and civil works, earthmoving, waterproofing and scaffolding; metalworking and structures with SMAW, MIG/MAG and TIG welding; surface treatment and protection (sandblasting, industrial painting, epoxies, passivation); electrical installations and instrumentation."',
        "fr": '"description": "Construction et génie civil, terrassement, étanchéité et échafaudages ; métallurgie et structures avec soudage SMAW, MIG/MAG et TIG ; traitement et protection de surfaces (sablage, peinture industrielle, époxydes, passivation) ; installations électriques et instrumentation."',
        "it": '"description": "Costruzione e opere civili, movimento terra, impermeabilizzazione e ponteggi; metalmeccanica e strutture con saldatura SMAW, MIG/MAG e TIG; trattamento e protezione superfici (sabbiatura, verniciatura industriale, epossidiche, passivazione); impianti elettrici e strumentazione."',
    },
    '"name": "Empacaduras y Sellado Industrial",\n            "serviceType": "Procura de empacaduras, juntas espirometálicas, sellos de grafito y juntas RTJ/FF/RF",': {
        "en": '"name": "Industrial Gaskets & Sealing",\n            "serviceType": "Procurement of gaskets, spiral-wound, graphite seals and RTJ/FF/RF gaskets",',
        "fr": '"name": "Joints et Étanchéité Industriels",\n            "serviceType": "Approvisionnement de joints, joints spiralés, joints en graphite et joints RTJ/FF/RF",',
        "it": '"name": "Guarnizioni e Tenute Industriali",\n            "serviceType": "Approvvigionamento di guarnizioni, guarnizioni spiralate, tenute in grafite e guarnizioni RTJ/FF/RF",',
    },
    '"description": "Suministro de soluciones de sellado de alta integridad: kits de juntas para aislamiento de bridas, empacaduras espirometálicas, sellos de grafito flexible y juntas tipo D (RTJ), E (FF) y F (RF) para líneas críticas, recipientes a presión y bridas industriales."': {
        "en": '"description": "Supply of high-integrity sealing solutions: flange isolation kits, spiral-wound gaskets, flexible graphite seals and type D (RTJ), E (FF) and F (RF) gaskets for critical lines, pressure vessels and industrial flanges."',
        "fr": '"description": "Fourniture de solutions d\'étanchéité haute intégrité : kits de joints pour isolation de brides, joints spiralés, joints en graphite flexible et joints type D (RTJ), E (FF) et F (RF) pour lignes critiques, récipients sous pression et brides industrielles."',
        "it": '"description": "Fornitura di soluzioni di tenuta ad alta integrità: kit di guarnizioni per isolamento flange, guarnizioni spiralate, tenute in grafite flessibile e guarnizioni tipo D (RTJ), E (FF) e F (RF) per linee critiche, recipienti a pressione e flange industriali."',
    },
    # --- Nav (desktop links) ---
    'class="hover:text-white transition">Nosotros</a>': {
        "en": 'class="hover:text-white transition">About</a>',
        "fr": 'class="hover:text-white transition">À Propos</a>',
        "it": 'class="hover:text-white transition">Chi Siamo</a>',
    },
    'class="hover:text-white transition"\n              >Servicios</a': {
        "en": 'class="hover:text-white transition"\n              >Services</a',
        "fr": 'class="hover:text-white transition"\n              >Services</a',
        "it": 'class="hover:text-white transition"\n              >Servizi</a',
    },
    'class="hover:text-white transition">Sectores</a>': {
        "en": 'class="hover:text-white transition">Sectors</a>',
        "fr": 'class="hover:text-white transition">Secteurs</a>',
        "it": 'class="hover:text-white transition">Settori</a>',
    },
    'class="hover:text-white transition">Equipo</a>': {
        "en": 'class="hover:text-white transition">Team</a>',
        "fr": 'class="hover:text-white transition">Équipe</a>',
        "it": 'class="hover:text-white transition">Team</a>',
    },
    'class="hover:text-white transition"\n              >Representación</a': {
        "en": 'class="hover:text-white transition"\n              >Partnership</a',
        "fr": 'class="hover:text-white transition"\n              >Partenariat</a',
        "it": 'class="hover:text-white transition"\n              >Rappresentanza</a',
    },
    'class="hover:text-white transition">Clientes</a>': {
        "en": 'class="hover:text-white transition">Clients</a>',
        "fr": 'class="hover:text-white transition">Clients</a>',
        "it": 'class="hover:text-white transition">Clienti</a>',
    },
    'class="hover:text-white transition"\n              >Postulaciones</a': {
        "en": 'class="hover:text-white transition"\n              >Careers</a',
        "fr": 'class="hover:text-white transition"\n              >Carrières</a',
        "it": 'class="hover:text-white transition"\n              >Carriere</a',
    },
    'class="hover:text-white transition">Contacto</a>': {
        "en": 'class="hover:text-white transition">Contact</a>',
        "fr": 'class="hover:text-white transition">Contact</a>',
        "it": 'class="hover:text-white transition">Contatto</a>',
    },
    # --- Mobile menu links ---
    'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Nosotros</a': {
        "en": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >About</a',
        "fr": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >À Propos</a',
        "it": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Chi Siamo</a',
    },
    'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Servicios</a': {
        "en": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Services</a',
        "fr": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Services</a',
        "it": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Servizi</a',
    },
    'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Sectores</a': {
        "en": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Sectors</a',
        "fr": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Secteurs</a',
        "it": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Settori</a',
    },
    'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Equipo</a': {
        "en": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Team</a',
        "fr": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Équipe</a',
        "it": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Team</a',
    },
    'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Representación</a': {
        "en": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Partnership</a',
        "fr": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Partenariat</a',
        "it": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Rappresentanza</a',
    },
    'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Clientes</a': {
        "en": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Clients</a',
        "fr": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Clients</a',
        "it": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Clienti</a',
    },
    'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Postulaciones</a': {
        "en": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Careers</a',
        "fr": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Carrières</a',
        "it": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Carriere</a',
    },
    'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Contacto</a': {
        "en": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Contact</a',
        "fr": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Contact</a',
        "it": 'class="py-3 border-b border-white/5 hover:text-brand transition"\n          >Contatto</a',
    },
    # --- aria labels ---
    'aria-label="INNOVEN inicio"': {
        "en": 'aria-label="INNOVEN home"',
        "fr": 'aria-label="INNOVEN accueil"',
        "it": 'aria-label="INNOVEN home"',
    },
    'aria-label="Abrir menú"': {
        "en": 'aria-label="Open menu"',
        "fr": 'aria-label="Ouvrir le menu"',
        "it": 'aria-label="Apri menu"',
    },
    'aria-label="Cerrar menú"': {
        "en": 'aria-label="Close menu"',
        "fr": 'aria-label="Fermer le menu"',
        "it": 'aria-label="Chiudi menu"',
    },
    'aria-label="Galería ampliada"': {
        "en": 'aria-label="Expanded gallery"',
        "fr": 'aria-label="Galerie agrandie"',
        "it": 'aria-label="Galleria ingrandita"',
    },
    'aria-label="Anterior"': {
        "en": 'aria-label="Previous"',
        "fr": 'aria-label="Précédent"',
        "it": 'aria-label="Precedente"',
    },
    'aria-label="Siguiente"': {
        "en": 'aria-label="Next"',
        "fr": 'aria-label="Suivant"',
        "it": 'aria-label="Successivo"',
    },
    'aria-label="Cerrar"': {
        "en": 'aria-label="Close"',
        "fr": 'aria-label="Fermer"',
        "it": 'aria-label="Chiudi"',
    },
    # --- CTA & button labels ---
    "Solicitar cotización": {
        "en": "Request a Quote",
        "fr": "Demander un Devis",
        "it": "Richiedi Preventivo",
    },
    "Ver servicios": {
        "en": "View Services",
        "fr": "Voir les services",
        "it": "Vedi i servizi",
    },
    "Dossier corporativo": {
        "en": "Corporate Brochure",
        "fr": "Brochure d'entreprise",
        "it": "Brochure aziendale",
    },
    "Iniciar conversación": {
        "en": "Start a conversation",
        "fr": "Démarrer la conversation",
        "it": "Avvia conversazione",
    },
    "Únete al equipo →": {
        "en": "Join the team →",
        "fr": "Rejoindre l'équipe →",
        "it": "Unisciti al team →",
    },
    "Únete al equipo": {
        "en": "Join the team",
        "fr": "Rejoindre l'équipe",
        "it": "Unisciti al team",
    },
    "Ir al formulario": {
        "en": "Go to the form",
        "fr": "Aller au formulaire",
        "it": "Vai al modulo",
    },
    "Escribirnos por WhatsApp": {
        "en": "Write us on WhatsApp",
        "fr": "Nous écrire sur WhatsApp",
        "it": "Scrivici su WhatsApp",
    },
    "Cuéntanos tu caso →": {
        "en": "Tell us your case →",
        "fr": "Parlez-nous de votre cas →",
        "it": "Raccontaci il tuo caso →",
    },
    "¿Tu sector no aparece?": {
        "en": "Don't see your sector?",
        "fr": "Votre secteur n'apparaît pas ?",
        "it": "Il tuo settore non c'è?",
    },
    # --- Hero stats ---
    "Personal disponible": {
        "en": "Available staff",
        "fr": "Personnel disponible",
        "it": "Personale disponibile",
    },
    "Clientes activos": {
        "en": "Active clients",
        "fr": "Clients actifs",
        "it": "Clienti attivi",
    },
    "Áreas de servicio": {
        "en": "Service areas",
        "fr": "Domaines d'activité",
        "it": "Aree di servizio",
    },
    "Under Certification 2026-2027": {
        "en": "Under Certification 2026-2027",
        "fr": "En cours de Certification 2026-2027",
        "it": "In Corso di Certificazione 2026-2027",
    },
    "En proceso de Certificación 2026-2027": {
        "en": "Under Certification 2026-2027",
        "fr": "En cours de Certification 2026-2027",
        "it": "In Corso di Certificazione 2026-2027",
    },
    "                  Líder\n                ": {
        "en": "                  Leader\n                ",
        "fr": "                  Leader\n                ",
        "it": "                  Leader\n                ",
    },
    "<span>Precisión</span": {
        "en": "<span>Precision</span",
        "fr": "<span>Précision</span",
        "it": "<span>Precisione</span",
    },
    # --- Hero pitch ---
    'Soluciones industriales <span class="text-brand">integrales</span\n              ><br />\n              para la operación que\n              <span class="italic font-medium text-white/90"\n                >no puede parar</span\n              >.': {
        "en": '<span class="text-brand">Integrated</span\n              ><br />\n              industrial solutions for the operation that\n              <span class="italic font-medium text-white/90"\n                >can\'t stop</span\n              >.',
        "fr": 'Solutions industrielles <span class="text-brand">intégrées</span\n              ><br />\n              pour l\'opération qui\n              <span class="italic font-medium text-white/90"\n                >ne peut s\'arrêter</span\n              >.',
        "it": 'Soluzioni industriali <span class="text-brand">integrate</span\n              ><br />\n              per l\'operazione che\n              <span class="italic font-medium text-white/90"\n                >non può fermarsi</span\n              >.',
    },
    "Ingeniería, mantenimiento y procura para los sectores industriales\n              en Venezuela. Representantes oficiales de": {
        "en": "Engineering, maintenance and procurement for the industrial sectors\n              in Venezuela. Official partners of",
        "fr": "Ingénierie, maintenance et approvisionnement pour les secteurs industriels\n              au Venezuela. Partenaires officiels de",
        "it": "Ingegneria, manutenzione e approvvigionamento per i settori industriali\n              in Venezuela. Partner ufficiali di",
    },
    "Confían en nosotros": {
        "en": "Trusted by",
        "fr": "Ils nous font confiance",
        "it": "Si fidano di noi",
    },
    # --- Sobre Nosotros ---
    "01 / Sobre Nosotros": {
        "en": "01 / About Us",
        "fr": "01 / À Propos",
        "it": "01 / Chi Siamo",
    },
    'Aliados estratégicos<br /><span class="text-brand"\n                >de la industria</span\n              >\n              venezolana.': {
        "en": 'Strategic partners<br /><span class="text-brand"\n                >for Venezuelan</span\n              >\n              industry.',
        "fr": 'Partenaires stratégiques<br /><span class="text-brand"\n                >de l\'industrie</span\n              >\n              vénézuélienne.',
        "it": 'Partner strategici<br /><span class="text-brand"\n                >dell\'industria</span\n              >\n              venezuelana.',
    },
    "Equipo Innoven en visita técnica con cliente en cantera de Cementos Catatumbo": {
        "en": "Innoven team on technical site visit with client at Cementos Catatumbo quarry",
        "fr": "Équipe Innoven en visite technique avec client à la carrière de Cementos Catatumbo",
        "it": "Team Innoven in visita tecnica con cliente alla cava di Cementos Catatumbo",
    },
    "Equipo Innoven en sitio cliente junto a equipos industriales con andamios y EPP": {
        "en": "Innoven team on client site next to industrial equipment with scaffolding and PPE",
        "fr": "Équipe Innoven sur site client avec équipements industriels, échafaudages et EPI",
        "it": "Team Innoven presso il cliente con attrezzature industriali, ponteggi e DPI",
    },
    '<span class="text-white font-semibold">INNOVEN C.A.</span> es\n                una empresa venezolana especializada en la prestación de\n                servicios industriales integrales y procura de materiales y\n                equipos, con amplia trayectoria en el sector industrial y\n                energético.': {
        "en": '<span class="text-white font-semibold">INNOVEN C.A.</span> is\n                a Venezuelan company specialized in providing integrated\n                industrial services and procurement of materials and\n                equipment, with extensive experience in the industrial and\n                energy sectors.',
        "fr": '<span class="text-white font-semibold">INNOVEN C.A.</span> est\n                une entreprise vénézuélienne spécialisée dans la prestation de\n                services industriels intégrés et l\'approvisionnement de matériaux et\n                équipements, avec une vaste expérience dans les secteurs industriel et\n                énergétique.',
        "it": "<span class=\"text-white font-semibold\">INNOVEN C.A.</span> è\n                un'azienda venezuelana specializzata nella fornitura di\n                servizi industriali integrati e nell'approvvigionamento di materiali e\n                attrezzature, con vasta esperienza nei settori industriale ed\n                energetico.",
    },
    "Contamos con un equipo de ingenieros, técnicos y especialistas\n                altamente calificados, respaldados por representaciones de\n                fabricantes líderes a nivel mundial.": {
        "en": "We have a team of highly qualified engineers, technicians and\n                specialists, backed by partnerships with world-leading\n                manufacturers.",
        "fr": "Nous disposons d'une équipe d'ingénieurs, techniciens et spécialistes\n                hautement qualifiés, soutenus par des partenariats avec des\n                fabricants leaders au niveau mondial.",
        "it": "Disponiamo di un team di ingegneri, tecnici e specialisti\n                altamente qualificati, supportati da partnership con\n                produttori leader a livello mondiale.",
    },
    'Nos posicionamos como aliados estratégicos de nuestros clientes,\n                aportando soluciones técnicas confiables, eficientes y adaptadas\n                a las exigencias operacionales de cada proyecto. Nuestro enfoque\n                está orientado a contribuir directamente a la\n                <span class="text-white">integridad de los activos</span>, la\n                <span class="text-white">continuidad operativa</span> y el\n                <span class="text-white">beneficio económico sostenible</span>\n                de las operaciones de nuestros contratantes.': {
        "en": 'We position ourselves as strategic partners to our clients,\n                providing reliable, efficient technical solutions tailored\n                to the operational demands of each project. Our approach\n                is oriented to contribute directly to\n                <span class="text-white">asset integrity</span>,\n                <span class="text-white">operational continuity</span> and the\n                <span class="text-white">sustainable economic benefit</span>\n                of our clients\' operations.',
        "fr": 'Nous nous positionnons comme partenaires stratégiques de nos clients,\n                en apportant des solutions techniques fiables, efficaces et adaptées\n                aux exigences opérationnelles de chaque projet. Notre approche\n                vise à contribuer directement à\n                <span class="text-white">l\'intégrité des actifs</span>, à la\n                <span class="text-white">continuité opérationnelle</span> et au\n                <span class="text-white">bénéfice économique durable</span>\n                des opérations de nos contractants.',
        "it": 'Ci posizioniamo come partner strategici dei nostri clienti,\n                fornendo soluzioni tecniche affidabili, efficienti e adattate\n                alle esigenze operative di ogni progetto. Il nostro approccio\n                è orientato a contribuire direttamente a\n                <span class="text-white">l\'integrità degli asset</span>, alla\n                <span class="text-white">continuità operativa</span> e al\n                <span class="text-white">beneficio economico sostenibile</span>\n                delle operazioni dei nostri clienti.',
    },
    # --- Misión / Visión ---
    ">Misión<": {"en": ">Mission<", "fr": ">Mission<", "it": ">Missione<"},
    ">Visión<": {"en": ">Vision<", "fr": ">Vision<", "it": ">Visione<"},
    "Soluciones integrales con compromiso técnico.": {
        "en": "Integrated solutions with technical commitment.",
        "fr": "Solutions intégrées avec engagement technique.",
        "it": "Soluzioni integrate con impegno tecnico.",
    },
    "En INNOVEN, brindamos soluciones integrales en ingeniería civil,\n            mecánica, eléctrica e instrumentación, así como en la procura de\n            proyectos, con un firme compromiso hacia la calidad, la mejora\n            continua y la satisfacción del cliente. Actuamos con responsabilidad\n            técnica y profesional, adaptándonos a los desafíos del entorno para\n            garantizar resultados confiables y eficientes.": {
        "en": "At INNOVEN, we provide integrated solutions in civil,\n            mechanical, electrical and instrumentation engineering, as well as project\n            procurement, with a firm commitment to quality, continuous\n            improvement and customer satisfaction. We act with technical\n            and professional responsibility, adapting to the challenges of the environment to\n            guarantee reliable and efficient results.",
        "fr": "Chez INNOVEN, nous fournissons des solutions intégrées en ingénierie civile,\n            mécanique, électrique et instrumentation, ainsi qu'en approvisionnement de\n            projets, avec un engagement ferme envers la qualité, l'amélioration\n            continue et la satisfaction du client. Nous agissons avec responsabilité\n            technique et professionnelle, en nous adaptant aux défis de l'environnement pour\n            garantir des résultats fiables et efficaces.",
        "it": "In INNOVEN, forniamo soluzioni integrate nell'ingegneria civile,\n            meccanica, elettrica e di strumentazione, così come nell'approvvigionamento di\n            progetti, con un fermo impegno verso la qualità, il miglioramento\n            continuo e la soddisfazione del cliente. Agiamo con responsabilità\n            tecnica e professionale, adattandoci alle sfide dell'ambiente per\n            garantire risultati affidabili ed efficienti.",
    },
    'Ser <span class="text-brand">referencia</span> en ingeniería\n            multidisciplinaria.': {
        "en": 'To be a <span class="text-brand">reference</span> in multidisciplinary\n            engineering.',
        "fr": 'Être une <span class="text-brand">référence</span> en ingénierie\n            multidisciplinaire.',
        "it": 'Essere un <span class="text-brand">riferimento</span> nell\'ingegneria\n            multidisciplinare.',
    },
    "Ser reconocidos como una empresa líder en ingeniería\n            multidisciplinaria en Venezuela, destacándonos por nuestra\n            excelencia operativa, capacidad de adaptación y compromiso con los\n            clientes, consolidando relaciones de confianza a largo plazo en cada\n            proyecto que emprendemos.": {
        "en": "To be recognized as a leading multidisciplinary engineering\n            company in Venezuela, standing out for our\n            operational excellence, adaptability and commitment to\n            clients, consolidating long-term trust relationships in every\n            project we undertake.",
        "fr": "Être reconnus comme une entreprise leader en ingénierie\n            multidisciplinaire au Venezuela, en nous distinguant par notre\n            excellence opérationnelle, capacité d'adaptation et engagement envers les\n            clients, consolidant des relations de confiance à long terme dans chaque\n            projet que nous entreprenons.",
        "it": "Essere riconosciuti come azienda leader nell'ingegneria\n            multidisciplinare in Venezuela, distinguendoci per la nostra\n            eccellenza operativa, capacità di adattamento e impegno verso i\n            clienti, consolidando relazioni di fiducia a lungo termine in ogni\n            progetto che intraprendiamo.",
    },
    # --- Servicios section header ---
    "02 / Productos y Servicios": {
        "en": "02 / Products & Services",
        "fr": "02 / Produits et Services",
        "it": "02 / Prodotti e Servizi",
    },
    'Cuatro áreas. <span class="text-brand">Una sola</span> capacidad\n            operativa.': {
        "en": 'Four areas. <span class="text-brand">One unified</span> operational\n            capability.',
        "fr": 'Quatre domaines. <span class="text-brand">Une seule</span> capacité\n            opérationnelle.',
        "it": 'Quattro aree. <span class="text-brand">Un\'unica</span> capacità\n            operativa.',
    },
    "Capacidades agrupadas para el mantenimiento integral, intervención\n            estructural, protección de activos y procura técnica de plantas\n            industriales.": {
        "en": "Capabilities grouped for integrated maintenance, structural\n            intervention, asset protection and technical procurement for industrial\n            plants.",
        "fr": "Capacités regroupées pour la maintenance intégrée, l'intervention\n            structurelle, la protection des actifs et l'approvisionnement technique d'usines\n            industrielles.",
        "it": "Capacità raggruppate per la manutenzione integrata, l'intervento\n            strutturale, la protezione degli asset e l'approvvigionamento tecnico di impianti\n            industriali.",
    },
    # --- Service 1: Aislamiento ---
    "Thermal insulation industrial en planta industrial": {
        "en": "Industrial thermal insulation at an industrial plant",
        "fr": "Isolation thermique industrielle dans une usine",
        "it": "Isolamento termico industriale in impianto",
    },
    "Aislamiento térmico industrial en planta industrial": {
        "en": "Industrial thermal insulation at an industrial plant",
        "fr": "Isolation thermique industrielle dans une usine",
        "it": "Isolamento termico industriale in impianto",
    },
    "01 — Servicio": {
        "en": "01 — Service",
        "fr": "01 — Service",
        "it": "01 — Servizio",
    },
    "02 — Servicio": {
        "en": "02 — Service",
        "fr": "02 — Service",
        "it": "02 — Servizio",
    },
    "Ingeniería de Aislamiento e Integridad Térmica": {
        "en": "Thermal Insulation & Integrity Engineering",
        "fr": "Ingénierie d'Isolation et Intégrité Thermiques",
        "it": "Ingegneria di Isolamento e Integrità Termica",
    },
    "Ingeniería de Thermal Insulation & Integrity": {
        "en": "Thermal Insulation & Integrity Engineering",
        "fr": "Ingénierie d'Isolation et Intégrité Thermiques",
        "it": "Ingegneria di Isolamento e Integrità Termica",
    },
    "Representantes": {"en": "Partners", "fr": "Partenaires", "it": "Partner"},
    "Conservación energética, protección de activos y continuidad\n                operativa de plantas e instalaciones industriales. Soluciones\n                para servicios de calor, frío criogénico, control acústico y\n                refractarios.": {
        "en": "Energy conservation, asset protection and operational\n                continuity for industrial plants and facilities. Solutions\n                for heat, cryogenic cold, acoustic control and\n                refractories.",
        "fr": "Conservation énergétique, protection des actifs et continuité\n                opérationnelle des usines et installations industrielles. Solutions\n                pour services de chaleur, froid cryogénique, contrôle acoustique et\n                réfractaires.",
        "it": "Conservazione energetica, protezione degli asset e continuità\n                operativa di impianti e installazioni industriali. Soluzioni\n                per servizi di calore, freddo criogenico, controllo acustico e\n                refrattari.",
    },
    "Aislamiento térmico\n                  industrial": {
        "en": "Industrial thermal\n                  insulation",
        "fr": "Isolation thermique\n                  industrielle",
        "it": "Isolamento termico\n                  industriale",
    },
    "Servicios criogénicos (Foam\n                  Glass)": {
        "en": "Cryogenic services (Foam\n                  Glass)",
        "fr": "Services cryogéniques (Foam\n                  Glass)",
        "it": "Servizi criogenici (Foam\n                  Glass)",
    },
    "Aislamiento acústico": {
        "en": "Acoustic insulation",
        "fr": "Isolation acoustique",
        "it": "Isolamento acustico",
    },
    "Sistemas refractarios": {
        "en": "Refractory systems",
        "fr": "Systèmes réfractaires",
        "it": "Sistemi refrattari",
    },
    "Fire Proofing estructural": {
        "en": "Structural Fire Proofing",
        "fr": "Protection anti-feu structurelle",
        "it": "Fire Proofing strutturale",
    },
    "Fibra cerámica · Silicato de\n                  calcio": {
        "en": "Ceramic fiber · Calcium\n                  silicate",
        "fr": "Fibre céramique · Silicate de\n                  calcium",
        "it": "Fibra ceramica · Silicato di\n                  calcio",
    },
    # --- Service 2: Refrigeración ---
    "02 — Procura": {
        "en": "02 — Procurement",
        "fr": "02 — Approvisionnement",
        "it": "02 — Approvvigionamento",
    },
    "03 — Servicio": {
        "en": "03 — Service",
        "fr": "03 — Service",
        "it": "03 — Servizio",
    },
    "04 — Procura": {
        "en": "04 — Procurement",
        "fr": "04 — Approvisionnement",
        "it": "04 — Approvvigionamento",
    },
    "Refrigeración y Climatización Industrial": {
        "en": "Industrial Refrigeration & HVAC",
        "fr": "Réfrigération et Climatisation Industrielles",
        "it": "Refrigerazione e Climatizzazione Industriale",
    },
    "Diseño, instalación y mantenimiento especializado de sistemas de\n                aire acondicionado de confort, precisión y agua helada. Personal\n                disponible las 24 horas para garantizar la continuidad de salas\n                de control y procesos críticos.": {
        "en": "Specialized design, installation and maintenance of comfort,\n                precision and chilled-water air conditioning systems. Staff\n                available 24/7 to ensure the continuity of control rooms\n                and critical processes.",
        "fr": "Conception, installation et maintenance spécialisée de systèmes de\n                climatisation de confort, de précision et eau glacée. Personnel\n                disponible 24h/24 pour garantir la continuité des salles\n                de contrôle et processus critiques.",
        "it": "Progettazione, installazione e manutenzione specializzata di sistemi di\n                condizionamento di comfort, precisione e acqua refrigerata. Personale\n                disponibile 24 ore su 24 per garantire la continuità delle sale\n                di controllo e processi critici.",
    },
    "A/C confort, precisión y\n                  agua helada": {
        "en": "Comfort, precision &\n                  chilled-water A/C",
        "fr": "A/C confort, précision et\n                  eau glacée",
        "it": "A/C comfort, precisione e\n                  acqua refrigerata",
    },
    "Ductería en lámina\n                  galvanizada y poliuretano": {
        "en": "Galvanized sheet & polyurethane\n                  ductwork",
        "fr": "Gainage en tôle galvanisée\n                  et polyuréthane",
        "it": "Canalizzazioni in lamiera\n                  zincata e poliuretano",
    },
    "Mantenimiento Liebert y\n                  otros equipos": {
        "en": "Liebert and other equipment\n                  maintenance",
        "fr": "Maintenance Liebert et\n                  autres équipements",
        "it": "Manutenzione Liebert e\n                  altre attrezzature",
    },
    "Suministro de repuestos\n                  originales": {
        "en": "Supply of original\n                  spare parts",
        "fr": "Fourniture de pièces de\n                  rechange originales",
        "it": "Fornitura di ricambi\n                  originali",
    },
    "Mantenimiento de equipos de refrigeración en planta industrial": {
        "en": "Refrigeration equipment maintenance at an industrial plant",
        "fr": "Maintenance d'équipements de réfrigération en usine industrielle",
        "it": "Manutenzione di apparecchiature di refrigerazione in impianto industriale",
    },
    "Servicio 24/7 sobre unidades de aire acondicionado industrial": {
        "en": "24/7 service on industrial A/C units",
        "fr": "Service 24/7 sur unités de climatisation industrielle",
        "it": "Servizio 24/7 su unità di condizionamento industriale",
    },
    # --- Service 3: Civil ---
    "Equipo Innoven en obra civil e industrial": {
        "en": "Innoven team on civil and industrial works site",
        "fr": "Équipe Innoven sur chantier civil et industriel",
        "it": "Team Innoven in opera civile e industriale",
    },
    "Ingeniería Civil e Industrial": {
        "en": "Civil & Industrial Engineering",
        "fr": "Ingénierie Civile et Industrielle",
        "it": "Ingegneria Civile e Industriale",
    },
    "Proyectos integrales de ingeniería civil e industrial con\n                personal calificado y equipos propios. Capacidades de\n                construcción, intervención estructural, protección de\n                superficies y servicios eléctricos.": {
        "en": "Integrated civil and industrial engineering projects with\n                qualified personnel and our own equipment. Capabilities for\n                construction, structural intervention, surface\n                protection and electrical services.",
        "fr": "Projets intégrés d'ingénierie civile et industrielle avec\n                personnel qualifié et équipements propres. Capacités de\n                construction, intervention structurelle, protection de\n                surfaces et services électriques.",
        "it": "Progetti integrati di ingegneria civile e industriale con\n                personale qualificato e attrezzature proprie. Capacità di\n                costruzione, intervento strutturale, protezione di\n                superfici e servizi elettrici.",
    },
    "Obras Civiles": {
        "en": "Civil Works",
        "fr": "Travaux Civils",
        "it": "Opere Civili",
    },
    "Construcción y remodelación · Movimiento de tierra ·\n                    Impermeabilización · Andamios (suministro, montaje,\n                    alquiler)": {
        "en": "Construction and remodeling · Earthmoving ·\n                    Waterproofing · Scaffolding (supply, assembly,\n                    rental)",
        "fr": "Construction et rénovation · Terrassement ·\n                    Étanchéité · Échafaudages (fourniture, montage,\n                    location)",
        "it": "Costruzione e ristrutturazione · Movimento terra ·\n                    Impermeabilizzazione · Ponteggi (fornitura, montaggio,\n                    noleggio)",
    },
    "Metalmecánica y Estructuras": {
        "en": "Metalworking and Structures",
        "fr": "Métallurgie et Structures",
        "it": "Metalmeccanica e Strutture",
    },
    "Fabricación y montaje de estructuras metálicas · Soldadura\n                    SMAW, MIG/MAG, TIG · Alquiler de equipos pesados": {
        "en": "Fabrication and assembly of steel structures · SMAW,\n                    MIG/MAG, TIG welding · Heavy equipment rental",
        "fr": "Fabrication et montage de structures métalliques · Soudage\n                    SMAW, MIG/MAG, TIG · Location d'équipements lourds",
        "it": "Fabbricazione e montaggio di strutture metalliche · Saldatura\n                    SMAW, MIG/MAG, TIG · Noleggio attrezzature pesanti",
    },
    "Tratamiento y Protección de Superficies": {
        "en": "Surface Treatment and Protection",
        "fr": "Traitement et Protection de Surfaces",
        "it": "Trattamento e Protezione Superfici",
    },
    "Sandblasting · Pintura industrial anticorrosiva ·\n                    Recubrimientos epóxicos · Pasivado anticorrosivo": {
        "en": "Sandblasting · Anti-corrosive industrial painting ·\n                    Epoxy coatings · Anti-corrosive passivation",
        "fr": "Sablage · Peinture industrielle anticorrosion ·\n                    Revêtements époxy · Passivation anticorrosion",
        "it": "Sabbiatura · Verniciatura industriale anticorrosione ·\n                    Rivestimenti epossidici · Passivazione anticorrosione",
    },
    "Electricidad e Instrumentación": {
        "en": "Electrical and Instrumentation",
        "fr": "Électricité et Instrumentation",
        "it": "Elettricità e Strumentazione",
    },
    "Generación y transformación · Transmisión y distribución ·\n                    Instrumentación y control de procesos": {
        "en": "Generation and transformation · Transmission and distribution ·\n                    Process instrumentation and control",
        "fr": "Production et transformation · Transmission et distribution ·\n                    Instrumentation et contrôle de processus",
        "it": "Generazione e trasformazione · Trasmissione e distribuzione ·\n                    Strumentazione e controllo processi",
    },
    # --- Service 4: Empacaduras ---
    "Empacaduras y Sellado Industrial": {
        "en": "Industrial Gaskets & Sealing",
        "fr": "Joints et Étanchéité Industriels",
        "it": "Guarnizioni e Tenute Industriali",
    },
    "Suministro de soluciones de sellado de alta integridad para\n                líneas críticas, recipientes a presión y bridas industriales en\n                operaciones industriales y energéticas.": {
        "en": "Supply of high-integrity sealing solutions for\n                critical lines, pressure vessels and industrial flanges in\n                industrial and energy operations.",
        "fr": "Fourniture de solutions d'étanchéité haute intégrité pour\n                lignes critiques, récipients sous pression et brides industrielles dans\n                les opérations industrielles et énergétiques.",
        "it": "Fornitura di soluzioni di tenuta ad alta integrità per\n                linee critiche, recipienti a pressione e flange industriali in\n                operazioni industriali ed energetiche.",
    },
    "Kits de juntas para\n                  aislamiento de bridas": {
        "en": "Flange isolation\n                  gasket kits",
        "fr": "Kits de joints pour\n                  isolation de brides",
        "it": "Kit di guarnizioni per\n                  isolamento flange",
    },
    "Empacaduras espirometálicas": {
        "en": "Spiral-wound gaskets",
        "fr": "Joints spiralés",
        "it": "Guarnizioni spiralate",
    },
    "Sellos de grafito flexible": {
        "en": "Flexible graphite seals",
        "fr": "Joints en graphite flexible",
        "it": "Tenute in grafite flessibile",
    },
    "Juntas tipo D (RTJ), E (FF)\n                  y F (RF)": {
        "en": "Type D (RTJ), E (FF)\n                  and F (RF) gaskets",
        "fr": "Joints type D (RTJ), E (FF)\n                  et F (RF)",
        "it": "Guarnizioni tipo D (RTJ), E (FF)\n                  e F (RF)",
    },
    # --- Morgan banner ---
    "Representación Oficial": {
        "en": "Official Partnership",
        "fr": "Partenariat Officiel",
        "it": "Partnership Ufficiale",
    },
    'Representantes oficiales de<br />\n              <span class="text-brand">Morgan Advanced Materials</span><br />\n              <span class="text-white/90">– Thermal Ceramics</span>': {
        "en": 'Official partners of<br />\n              <span class="text-brand">Morgan Advanced Materials</span><br />\n              <span class="text-white/90">– Thermal Ceramics</span>',
        "fr": 'Partenaires officiels de<br />\n              <span class="text-brand">Morgan Advanced Materials</span><br />\n              <span class="text-white/90">– Thermal Ceramics</span>',
        "it": 'Partner ufficiali di<br />\n              <span class="text-brand">Morgan Advanced Materials</span><br />\n              <span class="text-white/90">– Thermal Ceramics</span>',
    },
    "Fabricante líder mundial en soluciones de aislamiento térmico y\n              materiales refractarios. Esta representación nos posiciona como\n              referencia técnica para el sector industrial y energético de\n              Venezuela, garantizando calidad de fabricante y respaldo\n              internacional.": {
        "en": "World-leading manufacturer of thermal insulation solutions and\n              refractory materials. This partnership positions us as a\n              technical reference for the industrial and energy sector of\n              Venezuela, ensuring manufacturer quality and international\n              backing.",
        "fr": "Fabricant leader mondial de solutions d'isolation thermique et\n              matériaux réfractaires. Ce partenariat nous positionne comme\n              référence technique pour le secteur industriel et énergétique du\n              Venezuela, garantissant qualité fabricant et support\n              international.",
        "it": "Produttore leader mondiale di soluzioni di isolamento termico e\n              materiali refrattari. Questa partnership ci posiziona come\n              riferimento tecnico per il settore industriale ed energetico del\n              Venezuela, garantendo qualità del produttore e supporto\n              internazionale.",
    },
    ">Líder<": {"en": ">Leader<", "fr": ">Leader<", "it": ">Leader<"},
    ">Calidad<": {"en": ">Quality<", "fr": ">Qualité<", "it": ">Qualità<"},
    ">Respaldo<": {"en": ">Backing<", "fr": ">Support<", "it": ">Supporto<"},
    "Mundial en aislamiento": {
        "en": "Worldwide in insulation",
        "fr": "Mondial en isolation",
        "it": "Mondiale nell'isolamento",
    },
    "Materiales certificados": {
        "en": "Certified materials",
        "fr": "Matériaux certifiés",
        "it": "Materiali certificati",
    },
    "Soporte de fabricante": {
        "en": "Manufacturer support",
        "fr": "Support fabricant",
        "it": "Supporto del produttore",
    },
    "Sello de Representación": {
        "en": "Partnership Seal",
        "fr": "Sceau de Partenariat",
        "it": "Sigillo di Partnership",
    },
    "Fibra cerámica · Silicato de calcio · Lana mineral ·\n                Refractarios · Sistemas Fire Proofing certificados": {
        "en": "Ceramic fiber · Calcium silicate · Mineral wool ·\n                Refractories · Certified Fire Proofing systems",
        "fr": "Fibre céramique · Silicate de calcium · Laine minérale ·\n                Réfractaires · Systèmes de Protection Anti-Feu certifiés",
        "it": "Fibra ceramica · Silicato di calcio · Lana minerale ·\n                Refrattari · Sistemi Fire Proofing certificati",
    },
    # --- Sectores ---
    "03 / Sectores donde operamos": {
        "en": "03 / Sectors we operate in",
        "fr": "03 / Secteurs où nous opérons",
        "it": "03 / Settori in cui operiamo",
    },
    'Experiencia comprobada en<br />\n            <span class="text-brand">industrias críticas</span>.': {
        "en": 'Proven experience in<br />\n            <span class="text-brand">critical industries</span>.',
        "fr": 'Expérience prouvée dans<br />\n            <span class="text-brand">industries critiques</span>.',
        "it": 'Esperienza comprovata in<br />\n            <span class="text-brand">industrie critiche</span>.',
    },
    "Más de una década atendiendo operaciones donde un día de parada\n            cuesta más que un año de mantenimiento preventivo. Estos son los\n            sectores donde nuestro equipo opera con frecuencia.": {
        "en": "Over a decade serving operations where one day of downtime\n            costs more than a year of preventive maintenance. These are the\n            sectors where our team operates regularly.",
        "fr": "Plus d'une décennie au service d'opérations où un jour d'arrêt\n            coûte plus qu'une année de maintenance préventive. Voici les\n            secteurs où notre équipe opère régulièrement.",
        "it": "Oltre un decennio al servizio di operazioni dove un giorno di fermo\n            costa più di un anno di manutenzione preventiva. Questi sono i\n            settori in cui il nostro team opera regolarmente.",
    },
    "Reparación de aislamiento térmico en torre industrial con andamio completo": {
        "en": "Thermal insulation repair on industrial tower with full scaffolding",
        "fr": "Réparation d'isolation thermique sur tour industrielle avec échafaudage complet",
        "it": "Riparazione di isolamento termico su torre industriale con ponteggio completo",
    },
    "Industria energética": {
        "en": "Energy industry",
        "fr": "Industrie énergétique",
        "it": "Industria energetica",
    },
    "Reparación de aislamiento térmico en torres de proceso": {
        "en": "Thermal insulation repair on process towers",
        "fr": "Réparation d'isolation thermique sur tours de procédé",
        "it": "Riparazione di isolamento termico su torri di processo",
    },
    "Diagnóstico, retiro y reinstalación de aislamiento térmico en\n                torres y equipos verticales de altura. Incluye el montaje\n                completo del sistema de andamios necesario para ejecutar la\n                reparación con seguridad y cumplir el plan de paradas del\n                cliente.": {
        "en": "Diagnosis, removal and reinstallation of thermal insulation on\n                tall towers and vertical equipment. Includes full assembly\n                of the scaffolding system required to perform the\n                repair safely and meet the client's shutdown plan.",
        "fr": "Diagnostic, retrait et réinstallation d'isolation thermique sur\n                tours et équipements verticaux en hauteur. Inclut le montage\n                complet du système d'échafaudage nécessaire pour effectuer la\n                réparation en sécurité et respecter le plan d'arrêt du\n                client.",
        "it": "Diagnosi, rimozione e reinstallazione di isolamento termico su\n                torri e attrezzature verticali in altezza. Include il montaggio\n                completo del sistema di ponteggi necessario per eseguire la\n                riparazione in sicurezza e rispettare il piano di fermo del\n                cliente.",
    },
    "<span>Aislamiento</span>": {
        "en": "<span>Insulation</span>",
        "fr": "<span>Isolation</span>",
        "it": "<span>Isolamento</span>",
    },
    "<span>Andamios</span>": {
        "en": "<span>Scaffolding</span>",
        "fr": "<span>Échafaudages</span>",
        "it": "<span>Ponteggi</span>",
    },
    "<span>Trabajos en altura</span>": {
        "en": "<span>Working at height</span>",
        "fr": "<span>Travaux en hauteur</span>",
        "it": "<span>Lavori in quota</span>",
    },
    "Inspección interna de horno industrial con refractario": {
        "en": "Internal inspection of industrial furnace with refractory",
        "fr": "Inspection interne de four industriel avec réfractaire",
        "it": "Ispezione interna di forno industriale con refrattario",
    },
    "Industria pesada · Cementeras": {
        "en": "Heavy industry · Cement plants",
        "fr": "Industrie lourde · Cimenteries",
        "it": "Industria pesante · Cementifici",
    },
    "Inspección y reparación de hornos con ladrillos refractarios": {
        "en": "Inspection and repair of furnaces with refractory bricks",
        "fr": "Inspection et réparation de fours avec briques réfractaires",
        "it": "Ispezione e riparazione di forni con mattoni refrattari",
    },
    "Inspección, demolición controlada y enladrillado de hornos\n                industriales con ladrillos refractarios. Vaciado y proyectado\n                refractario en zonas críticas durante paradas programadas, con\n                cuadrillas especializadas y supervisión técnica continua.": {
        "en": "Inspection, controlled demolition and bricking of industrial\n                furnaces with refractory bricks. Refractory casting and gunning\n                in critical zones during scheduled shutdowns, with\n                specialized crews and continuous technical supervision.",
        "fr": "Inspection, démolition contrôlée et briquetage de fours\n                industriels avec briques réfractaires. Coulage et projection\n                réfractaires dans zones critiques pendant arrêts programmés, avec\n                équipes spécialisées et supervision technique continue.",
        "it": "Ispezione, demolizione controllata e mattonatura di forni\n                industriali con mattoni refrattari. Colatura e proiezione\n                refrattarie in zone critiche durante fermi programmati, con\n                squadre specializzate e supervisione tecnica continua.",
    },
    "<span>Hornos</span>": {
        "en": "<span>Furnaces</span>",
        "fr": "<span>Fours</span>",
        "it": "<span>Forni</span>",
    },
    "<span>Refractarios</span>": {
        "en": "<span>Refractories</span>",
        "fr": "<span>Réfractaires</span>",
        "it": "<span>Refrattari</span>",
    },
    "<span>Enladrillado</span>": {
        "en": "<span>Bricklaying</span>",
        "fr": "<span>Briquetage</span>",
        "it": "<span>Mattonatura</span>",
    },
    "Mantenimiento de equipos de refrigeración y climatización": {
        "en": "Refrigeration and HVAC equipment maintenance",
        "fr": "Maintenance d'équipements de réfrigération et climatisation",
        "it": "Manutenzione di apparecchiature di refrigerazione e climatizzazione",
    },
    "Servicios · Instituciones": {
        "en": "Services · Institutions",
        "fr": "Services · Institutions",
        "it": "Servizi · Istituzioni",
    },
    "Climatización industrial y mantenimiento crítico 24/7": {
        "en": "Industrial HVAC and 24/7 critical maintenance",
        "fr": "Climatisation industrielle et maintenance critique 24/7",
        "it": "Climatizzazione industriale e manutenzione critica 24/7",
    },
    "A/C de confort, precisión y agua helada para edificios\n                corporativos, centros logísticos y operaciones de organismos\n                internacionales. Mantenimiento preventivo y respuesta a\n                emergencias todo el año.": {
        "en": "Comfort, precision and chilled-water A/C for corporate\n                buildings, logistics centers and international organization\n                operations. Preventive maintenance and emergency response\n                year-round.",
        "fr": "Climatisation de confort, de précision et eau glacée pour bâtiments\n                d'entreprise, centres logistiques et opérations d'organismes\n                internationaux. Maintenance préventive et intervention\n                d'urgence toute l'année.",
        "it": "A/C di comfort, precisione e acqua refrigerata per edifici\n                aziendali, centri logistici e operazioni di organizzazioni\n                internazionali. Manutenzione preventiva e risposta alle\n                emergenze tutto l'anno.",
    },
    "<span>Precisión</span>": {
        "en": "<span>Precision</span>",
        "fr": "<span>Précision</span>",
        "it": "<span>Precisione</span>",
    },
    # --- Equipo ---
    "04 / Áreas operativas": {
        "en": "04 / Operational areas",
        "fr": "04 / Domaines opérationnels",
        "it": "04 / Aree operative",
    },
    'Cuatro áreas, cuatro<br />\n              <span class="text-brand">canales directos</span>.': {
        "en": 'Four areas, four<br />\n              <span class="text-brand">direct channels</span>.',
        "fr": 'Quatre domaines, quatre<br />\n              <span class="text-brand">canaux directs</span>.',
        "it": 'Quattro aree, quattro<br />\n              <span class="text-brand">canali diretti</span>.',
    },
    "Sin centralitas ni intermediarios: cada departamento atiende su\n              propio canal de WhatsApp y correo. Te conectamos directamente con\n              quien resuelve tu requerimiento.": {
        "en": "No call centers or middlemen: each department runs its\n              own WhatsApp and email channel. We connect you directly with\n              whoever resolves your request.",
        "fr": "Pas de standards ni d'intermédiaires : chaque département gère son\n              propre canal WhatsApp et email. Nous vous connectons directement avec\n              celui qui résout votre demande.",
        "it": "Senza centralini né intermediari: ogni dipartimento gestisce il\n              proprio canale WhatsApp ed email. Ti colleghiamo direttamente con\n              chi risolve la tua richiesta.",
    },
    "Operaciones": {"en": "Operations", "fr": "Opérations", "it": "Operazioni"},
    "Coordinación de obra, supervisión técnica y SIHAO en sitio.\n              Cotizaciones de proyectos integrales.": {
        "en": "Site coordination, technical supervision and OHSE on site.\n              Integrated project quotes.",
        "fr": "Coordination de chantier, supervision technique et HSE sur site.\n              Devis de projets intégrés.",
        "it": "Coordinamento cantiere, supervisione tecnica e HSE in sito.\n              Preventivi di progetti integrati.",
    },
    "Compras y Procura": {
        "en": "Procurement",
        "fr": "Achats et Approvisionnement",
        "it": "Acquisti e Approvvigionamento",
    },
    "Importación, logística y gestión de proveedores certificados.\n              Materiales Morgan Thermal Ceramics.": {
        "en": "Import, logistics and management of certified suppliers.\n              Morgan Thermal Ceramics materials.",
        "fr": "Importation, logistique et gestion de fournisseurs certifiés.\n              Matériaux Morgan Thermal Ceramics.",
        "it": "Importazione, logistica e gestione di fornitori certificati.\n              Materiali Morgan Thermal Ceramics.",
    },
    "Administración": {
        "en": "Administration",
        "fr": "Administration",
        "it": "Amministrazione",
    },
    "Facturación, contratos y gestión documental. Trámites de proveedor\n              con grandes operadoras.": {
        "en": "Invoicing, contracts and document management. Supplier procedures\n              with large operators.",
        "fr": "Facturation, contrats et gestion documentaire. Démarches fournisseur\n              avec grands opérateurs.",
        "it": "Fatturazione, contratti e gestione documentale. Pratiche fornitore\n              con grandi operatori.",
    },
    "Recursos Humanos": {
        "en": "Human Resources",
        "fr": "Ressources Humaines",
        "it": "Risorse Umane",
    },
    "Postulaciones, captación de talento técnico y gestión del personal\n              certificado en operación.": {
        "en": "Applications, technical talent acquisition and management of certified\n              personnel in operation.",
        "fr": "Candidatures, recrutement de talents techniques et gestion du personnel\n              certifié en opération.",
        "it": "Candidature, acquisizione di talenti tecnici e gestione del personale\n              certificato in operazione.",
    },
    "Personal técnico certificado · Cuadrillas 24/7/365": {
        "en": "Certified technical personnel · Crews 24/7/365",
        "fr": "Personnel technique certifié · Équipes 24/7/365",
        "it": "Personale tecnico certificato · Squadre 24/7/365",
    },
    # --- Valores ---
    "05 / Valores": {"en": "05 / Values", "fr": "05 / Valeurs", "it": "05 / Valori"},
    'Lo que nos define<br />en cada\n            <span class="text-brand">proyecto</span>.': {
        "en": 'What defines us<br />in every\n            <span class="text-brand">project</span>.',
        "fr": 'Ce qui nous définit<br />dans chaque\n            <span class="text-brand">projet</span>.',
        "it": 'Ciò che ci definisce<br />in ogni\n            <span class="text-brand">progetto</span>.',
    },
    "Calidad": {"en": "Quality", "fr": "Qualité", "it": "Qualità"},
    "Productos y servicios de la más alta calidad, superando las\n              expectativas de nuestros clientes. Aprendizaje y mejora continua.": {
        "en": "Highest quality products and services, exceeding our\n              clients' expectations. Continuous learning and improvement.",
        "fr": "Produits et services de la plus haute qualité, dépassant les\n              attentes de nos clients. Apprentissage et amélioration continus.",
        "it": "Prodotti e servizi della più alta qualità, superando le\n              aspettative dei nostri clienti. Apprendimento e miglioramento continui.",
    },
    "Trabajo en Equipo": {
        "en": "Teamwork",
        "fr": "Travail d'Équipe",
        "it": "Lavoro di Squadra",
    },
    "Cooperación como base. Juntos logramos más, valorando la\n              contribución de cada individuo para alcanzar objetivos comunes.": {
        "en": "Cooperation as a foundation. Together we achieve more, valuing the\n              contribution of each individual to reach common goals.",
        "fr": "La coopération comme base. Ensemble nous accomplissons plus, en valorisant la\n              contribution de chaque individu pour atteindre des objectifs communs.",
        "it": "La cooperazione come base. Insieme otteniamo di più, valorizzando il\n              contributo di ogni individuo per raggiungere obiettivi comuni.",
    },
    "Comunicación": {
        "en": "Communication",
        "fr": "Communication",
        "it": "Comunicazione",
    },
    "Transparencia y respeto. Intercambio constructivo de ideas\n              asegurando que todos los miembros se sientan escuchados.": {
        "en": "Transparency and respect. Constructive exchange of ideas\n              ensuring every member feels heard.",
        "fr": "Transparence et respect. Échange constructif d'idées\n              garantissant que tous les membres se sentent écoutés.",
        "it": "Trasparenza e rispetto. Scambio costruttivo di idee\n              garantendo che tutti i membri si sentano ascoltati.",
    },
    "Satisfacción del Cliente": {
        "en": "Customer Satisfaction",
        "fr": "Satisfaction Client",
        "it": "Soddisfazione del Cliente",
    },
    "Superamos expectativas con servicios de alta calidad y soluciones\n              innovadoras que generan valor real en sus operaciones.": {
        "en": "We exceed expectations with high-quality services and innovative\n              solutions that generate real value in their operations.",
        "fr": "Nous dépassons les attentes avec des services de haute qualité et des solutions\n              innovantes qui génèrent une valeur réelle dans leurs opérations.",
        "it": "Superiamo le aspettative con servizi di alta qualità e soluzioni\n              innovative che generano valore reale nelle loro operazioni.",
    },
    "Adaptabilidad": {"en": "Adaptability", "fr": "Adaptabilité", "it": "Adattabilità"},
    "Evolución constante para responder eficientemente a las demandas\n              del mercado, ofreciendo soluciones actualizadas y competitivas.": {
        "en": "Constant evolution to efficiently respond to market\n              demands, offering up-to-date and competitive solutions.",
        "fr": "Évolution constante pour répondre efficacement aux exigences\n              du marché, en offrant des solutions actualisées et compétitives.",
        "it": "Evoluzione costante per rispondere efficacemente alle esigenze\n              del mercato, offrendo soluzioni aggiornate e competitive.",
    },
    "¿Próximo proyecto?": {
        "en": "Next project?",
        "fr": "Prochain projet ?",
        "it": "Prossimo progetto?",
    },
    "Hablemos de cómo podemos sumar a tu operación.": {
        "en": "Let's talk about how we can add value to your operation.",
        "fr": "Parlons de comment nous pouvons apporter de la valeur à votre opération.",
        "it": "Parliamo di come possiamo apportare valore alla tua operazione.",
    },
    # --- Políticas ---
    "Política de Calidad": {
        "en": "Quality Policy",
        "fr": "Politique Qualité",
        "it": "Politica per la Qualità",
    },
    "Política SIHAO": {
        "en": "OHSE Policy",
        "fr": "Politique HSE",
        "it": "Politica HSE",
    },
    'Sistema de Gestión\n            <span class="text-brand">en proceso de certificación</span> bajo\n            estándares internacionales.': {
        "en": 'Management System\n            <span class="text-brand">under certification</span> to\n            international standards.',
        "fr": 'Système de Gestion\n            <span class="text-brand">en cours de certification</span> selon\n            normes internationales.',
        "it": 'Sistema di Gestione\n            <span class="text-brand">in corso di certificazione</span> secondo\n            standard internazionali.',
    },
    'Asumimos el compromiso de satisfacer plenamente los requerimientos\n              de nuestros clientes y partes interesadas. Garantizamos resultados\n              confiables mediante una\n              <span class="text-white">logística eficiente</span> y asesoría\n              técnica especializada en cada fase del proyecto.': {
        "en": 'We commit to fully meeting the requirements of our\n              clients and stakeholders. We guarantee reliable results\n              through\n              <span class="text-white">efficient logistics</span> and specialized\n              technical advisory at every project phase.',
        "fr": 'Nous nous engageons à satisfaire pleinement les exigences\n              de nos clients et parties prenantes. Nous garantissons des résultats\n              fiables grâce à une\n              <span class="text-white">logistique efficace</span> et un conseil\n              technique spécialisé à chaque phase du projet.',
        "it": 'Ci impegniamo a soddisfare pienamente i requisiti dei\n              nostri clienti e stakeholder. Garantiamo risultati\n              affidabili attraverso una\n              <span class="text-white">logistica efficiente</span> e consulenza\n              tecnica specializzata in ogni fase del progetto.',
    },
    'Promovemos el desarrollo continuo de nuestro personal y una\n              cultura organizacional basada en la\n              <span class="text-white"\n                >integridad, el respeto y la responsabilidad profesional</span\n              >, impulsando la innovación y la optimización constante de\n              nuestros procesos a través de nuestro Sistema de Gestión de la\n              Calidad (SGC).': {
        "en": 'We promote the continuous development of our staff and an\n              organizational culture based on\n              <span class="text-white"\n                >integrity, respect and professional responsibility</span\n              >, driving innovation and constant optimization of\n              our processes through our Quality Management System\n              (QMS).',
        "fr": "Nous promouvons le développement continu de notre personnel et une\n              culture organisationnelle basée sur\n              <span class=\"text-white\"\n                >l'intégrité, le respect et la responsabilité professionnelle</span\n              >, stimulant l'innovation et l'optimisation constante de\n              nos processus à travers notre Système de Management de la\n              Qualité (SMQ).",
        "it": "Promuoviamo lo sviluppo continuo del nostro personale e una\n              cultura organizzativa basata su\n              <span class=\"text-white\"\n                >integrità, rispetto e responsabilità professionale</span\n              >, guidando l'innovazione e l'ottimizzazione costante dei\n              nostri processi attraverso il nostro Sistema di Gestione per la\n              Qualità (SGQ).",
    },
    "SGC en proceso de certificación": {
        "en": "QMS under certification",
        "fr": "SMQ en cours de certification",
        "it": "SGQ in corso di certificazione",
    },
    '<span class="text-brand">Seguridad</span>, salud y ambiente — sin\n            excepciones.': {
        "en": '<span class="text-brand">Safety</span>, health and environment — no\n            exceptions.',
        "fr": '<span class="text-brand">Sécurité</span>, santé et environnement — sans\n            exceptions.',
        "it": '<span class="text-brand">Sicurezza</span>, salute e ambiente — senza\n            eccezioni.',
    },
    "Mantenemos un compromiso firme con la seguridad, salud e higiene\n              ocupacional de nuestros trabajadores y con la preservación del\n              medio ambiente en todas nuestras operaciones.": {
        "en": "We maintain a firm commitment to occupational safety, health\n              and hygiene of our workers and to the preservation of\n              the environment in all our operations.",
        "fr": "Nous maintenons un engagement ferme envers la sécurité, la santé et l'hygiène\n              au travail de nos travailleurs et la préservation de\n              l'environnement dans toutes nos opérations.",
        "it": "Manteniamo un fermo impegno per la sicurezza, salute e igiene\n              del lavoro dei nostri dipendenti e per la preservazione\n              dell'ambiente in tutte le nostre operazioni.",
    },
    "Identificamos, evaluamos y controlamos los riesgos operativos de\n              forma sistemática, aplicando medidas preventivas que protejan la\n              integridad de nuestro personal, las instalaciones de nuestros\n              clientes y el entorno donde operamos.": {
        "en": "We identify, evaluate and control operational risks\n              systematically, applying preventive measures that protect the\n              integrity of our personnel, our clients' facilities\n              and the environment where we operate.",
        "fr": "Nous identifions, évaluons et contrôlons les risques opérationnels\n              de manière systématique, en appliquant des mesures préventives qui protègent\n              l'intégrité de notre personnel, les installations de nos\n              clients et l'environnement où nous opérons.",
        "it": "Identifichiamo, valutiamo e controlliamo i rischi operativi in\n              modo sistematico, applicando misure preventive che proteggono\n              l'integrità del nostro personale, le strutture dei nostri\n              clienti e l'ambiente in cui operiamo.",
    },
    ">Seguridad<": {"en": ">Safety<", "fr": ">Sécurité<", "it": ">Sicurezza<"},
    ">Higiene<": {"en": ">Hygiene<", "fr": ">Hygiène<", "it": ">Igiene<"},
    ">Ambiente<": {"en": ">Environment<", "fr": ">Environnement<", "it": ">Ambiente<"},
    # --- Capacitación ---
    "06 / Capacitación Continua": {
        "en": "06 / Continuous Training",
        "fr": "06 / Formation Continue",
        "it": "06 / Formazione Continua",
    },
    'Invertimos en la<br />\n              <span class="text-brand">formación</span> de nuestro personal.': {
        "en": 'We invest in the<br />\n              <span class="text-brand">training</span> of our personnel.',
        "fr": 'Nous investissons dans la<br />\n              <span class="text-brand">formation</span> de notre personnel.',
        "it": 'Investiamo nella<br />\n              <span class="text-brand">formazione</span> del nostro personale.',
    },
    "En Innoven creemos que la capacitación continua es lo que sostiene\n              la calidad operativa en campo. Cada miembro del equipo participa\n              en programas de formación técnica y de seguridad, actualizando\n              competencias en aislamiento, refrigeración, soldadura,\n              electricidad, prevención de riesgos y normas SIHAO.": {
        "en": "At Innoven we believe continuous training is what sustains\n              operational quality in the field. Every team member participates\n              in technical and safety training programs, updating\n              skills in insulation, refrigeration, welding,\n              electricity, risk prevention and OHSE standards.",
        "fr": "Chez Innoven, nous pensons que la formation continue est ce qui soutient\n              la qualité opérationnelle sur le terrain. Chaque membre de l'équipe participe\n              à des programmes de formation technique et de sécurité, actualisant\n              les compétences en isolation, réfrigération, soudage,\n              électricité, prévention des risques et normes HSE.",
        "it": "In Innoven crediamo che la formazione continua sia ciò che sostiene\n              la qualità operativa sul campo. Ogni membro del team partecipa\n              a programmi di formazione tecnica e di sicurezza, aggiornando\n              competenze in isolamento, refrigerazione, saldatura,\n              elettricità, prevenzione dei rischi e norme HSE.",
    },
    "Es así como garantizamos que cada intervención se ejecute con\n              criterio técnico, cuidado humano y apego estricto a los estándares\n              internacionales.": {
        "en": "This is how we ensure each intervention is executed with\n              technical judgment, human care and strict adherence to international\n              standards.",
        "fr": "C'est ainsi que nous garantissons que chaque intervention soit exécutée avec\n              jugement technique, soin humain et respect strict des standards\n              internationaux.",
        "it": "È così che garantiamo che ogni intervento sia eseguito con\n              giudizio tecnico, cura umana e stretto rispetto degli standard\n              internazionali.",
    },
    "Personal Innoven en sesión de capacitación técnica": {
        "en": "Innoven personnel in technical training session",
        "fr": "Personnel Innoven en session de formation technique",
        "it": "Personale Innoven in sessione di formazione tecnica",
    },
    "Formación técnica": {
        "en": "Technical training",
        "fr": "Formation technique",
        "it": "Formazione tecnica",
    },
    "Programa interno de actualización profesional": {
        "en": "Internal professional development program",
        "fr": "Programme interne de développement professionnel",
        "it": "Programma interno di aggiornamento professionale",
    },
    "Curso de capacitación Innoven": {
        "en": "Innoven training course",
        "fr": "Cours de formation Innoven",
        "it": "Corso di formazione Innoven",
    },
    "Capacitación en seguridad industrial": {
        "en": "Industrial safety training",
        "fr": "Formation en sécurité industrielle",
        "it": "Formazione sulla sicurezza industriale",
    },
    "Sesión de entrenamiento técnico Innoven": {
        "en": "Innoven technical training session",
        "fr": "Session d'entraînement technique Innoven",
        "it": "Sessione di addestramento tecnico Innoven",
    },
    "Personal técnico Innoven en formación continua": {
        "en": "Innoven technical personnel in continuous training",
        "fr": "Personnel technique Innoven en formation continue",
        "it": "Personale tecnico Innoven in formazione continua",
    },
    "Sesión de capacitación técnica del personal Innoven": {
        "en": "Technical training session for Innoven personnel",
        "fr": "Session de formation technique du personnel Innoven",
        "it": "Sessione di formazione tecnica del personale Innoven",
    },
    "Personal Innoven en jornada de formación": {
        "en": "Innoven personnel on training day",
        "fr": "Personnel Innoven en journée de formation",
        "it": "Personale Innoven in giornata di formazione",
    },
    "Equipo Innoven en programa interno de capacitación": {
        "en": "Innoven team in internal training program",
        "fr": "Équipe Innoven en programme interne de formation",
        "it": "Team Innoven in programma interno di formazione",
    },
    # --- Clientes ---
    "07 / Clientes": {"en": "07 / Clients", "fr": "07 / Clients", "it": "07 / Clienti"},
    'Operadores e instituciones<br />que\n            <span class="text-brand">confían</span> en nosotros.': {
        "en": 'Operators and institutions<br />who\n            <span class="text-brand">trust</span> us.',
        "fr": 'Opérateurs et institutions<br />qui nous\n            <span class="text-brand">font confiance</span>.',
        "it": 'Operatori e istituzioni<br />che si\n            <span class="text-brand">fidano</span> di noi.',
    },
    "Desde el sector industrial y energético hasta organismos\n            internacionales — un portafolio que refleja nuestra capacidad de\n            adaptación a entornos exigentes.": {
        "en": "From the industrial and energy sector to international\n            organizations — a portfolio that reflects our ability to\n            adapt to demanding environments.",
        "fr": "Du secteur industriel et énergétique aux organismes\n            internationaux — un portefeuille qui reflète notre capacité à\n            nous adapter à des environnements exigeants.",
        "it": "Dal settore industriale ed energetico fino a organizzazioni\n            internazionali — un portafoglio che riflette la nostra capacità di\n            adattamento ad ambienti esigenti.",
    },
    ">Industrial<": {"en": ">Industrial<", "fr": ">Industriel<", "it": ">Industriale<"},
    ">Energía<": {"en": ">Energy<", "fr": ">Énergie<", "it": ">Energia<"},
    ">Naviero<": {"en": ">Maritime<", "fr": ">Maritime<", "it": ">Marittimo<"},
    "Organismo Internacional": {
        "en": "International Organization",
        "fr": "Organisme International",
        "it": "Organismo Internazionale",
    },
    "ONG Internacional": {
        "en": "International NGO",
        "fr": "ONG Internationale",
        "it": "ONG Internazionale",
    },
    "Asociación Civil": {
        "en": "Civil Association",
        "fr": "Association Civile",
        "it": "Associazione Civile",
    },
    "Fundación": {"en": "Foundation", "fr": "Fondation", "it": "Fondazione"},
    ">Construcción<": {
        "en": ">Construction<",
        "fr": ">Construction<",
        "it": ">Costruzione<",
    },
    ">Residencial<": {
        "en": ">Residential<",
        "fr": ">Résidentiel<",
        "it": ">Residenziale<",
    },
    ">Inmobiliario<": {
        "en": ">Real Estate<",
        "fr": ">Immobilier<",
        "it": ">Immobiliare<",
    },
    # --- Galería ---
    'Trabajo de campo,<br /><span class="text-brand"\n              >resultados visibles</span\n            >.': {
        "en": 'Field work,<br /><span class="text-brand"\n              >visible results</span\n            >.',
        "fr": 'Travail de terrain,<br /><span class="text-brand"\n              >résultats visibles</span\n            >.',
        "it": 'Lavoro sul campo,<br /><span class="text-brand"\n              >risultati visibili</span\n            >.',
    },
    # gallery alt + lb-alt
    "Vista aérea con drone de operaciones Innoven": {
        "en": "Drone aerial view of Innoven operations",
        "fr": "Vue aérienne par drone des opérations Innoven",
        "it": "Vista aerea con drone delle operazioni Innoven",
    },
    "Operaciones Innoven en sitio": {
        "en": "Innoven operations on site",
        "fr": "Opérations Innoven sur site",
        "it": "Operazioni Innoven in sito",
    },
    "Operaciones Innoven en planta industrial": {
        "en": "Innoven operations at industrial plant",
        "fr": "Opérations Innoven en usine industrielle",
        "it": "Operazioni Innoven in impianto industriale",
    },
    "Impermeabilización de techo industrial con equipo de aire acondicionado": {
        "en": "Industrial roof waterproofing with A/C equipment",
        "fr": "Étanchéité de toit industriel avec équipement de climatisation",
        "it": "Impermeabilizzazione di tetto industriale con apparecchiatura A/C",
    },
    "Flota Innoven de vehículos JAC frente a sede operativa": {
        "en": "Innoven fleet of JAC vehicles in front of operations base",
        "fr": "Flotte Innoven de véhicules JAC devant le siège opérationnel",
        "it": "Flotta Innoven di veicoli JAC davanti alla sede operativa",
    },
    "Grúa Grove de movilización en planta refinería": {
        "en": "Grove mobilization crane at refinery plant",
        "fr": "Grue Grove de mobilisation en raffinerie",
        "it": "Gru Grove di movimentazione in impianto raffineria",
    },
    "Compactador vibratorio en obra civil industrial": {
        "en": "Vibratory compactor on industrial civil works",
        "fr": "Compacteur vibrant en travaux civils industriels",
        "it": "Compattatore vibrante in opera civile industriale",
    },
    "Armado de parrilla de acero estructural en sitio": {
        "en": "Structural steel grid assembly on site",
        "fr": "Assemblage de grille en acier structurel sur site",
        "it": "Assemblaggio di griglia in acciaio strutturale in sito",
    },
    "Techo impermeabilizado con vista a refinería al fondo": {
        "en": "Waterproofed roof with refinery in background",
        "fr": "Toit étanche avec raffinerie en arrière-plan",
        "it": "Tetto impermeabilizzato con raffineria sullo sfondo",
    },
    "Demolición de pavimento con martillo neumático": {
        "en": "Pavement demolition with pneumatic hammer",
        "fr": "Démolition de chaussée avec marteau pneumatique",
        "it": "Demolizione di pavimentazione con martello pneumatico",
    },
    "Compactación de terreno en planta industrial": {
        "en": "Soil compaction at industrial plant",
        "fr": "Compactage de terrain en usine industrielle",
        "it": "Compattazione del terreno in impianto industriale",
    },
    "Aplicación de manto asfáltico con soplete en techo industrial": {
        "en": "Application of asphalt membrane with torch on industrial roof",
        "fr": "Application de membrane asphaltique au chalumeau sur toit industriel",
        "it": "Applicazione di guaina bituminosa con cannello su tetto industriale",
    },
    "Rodillo compactador en preparación de terreno": {
        "en": "Compactor roller in ground preparation",
        "fr": "Rouleau compacteur en préparation de terrain",
        "it": "Rullo compattatore in preparazione del terreno",
    },
    "Excavación con retroexcavadora John Deere": {
        "en": "Excavation with John Deere backhoe",
        "fr": "Excavation avec rétrocaveuse John Deere",
        "it": "Scavo con escavatore John Deere",
    },
    "Grúa Grove cargada en lowboy trailer en patio de equipos": {
        "en": "Grove crane loaded on lowboy trailer at equipment yard",
        "fr": "Grue Grove chargée sur remorque lowboy au parc d'équipements",
        "it": "Gru Grove caricata su rimorchio lowboy nel piazzale attrezzature",
    },
    "Edificación civil terminada en zona urbana": {
        "en": "Completed civil building in urban area",
        "fr": "Bâtiment civil achevé en zone urbaine",
        "it": "Edificio civile completato in zona urbana",
    },
    "Trabajos civiles en planta de cemento": {
        "en": "Civil works at cement plant",
        "fr": "Travaux civils en cimenterie",
        "it": "Lavori civili in cementificio",
    },
    "Trabajos de impermeabilización en techo industrial en progreso": {
        "en": "Waterproofing work on industrial roof in progress",
        "fr": "Travaux d'étanchéité sur toit industriel en cours",
        "it": "Lavori di impermeabilizzazione su tetto industriale in corso",
    },
    "Soldadura industrial nocturna": {
        "en": "Night industrial welding",
        "fr": "Soudage industriel nocturne",
        "it": "Saldatura industriale notturna",
    },
    "Mantenimiento en planta industrial": {
        "en": "Maintenance at industrial plant",
        "fr": "Maintenance en usine industrielle",
        "it": "Manutenzione in impianto industriale",
    },
    "Impermeabilización entre unidades de aire acondicionado de techo": {
        "en": "Waterproofing between rooftop A/C units",
        "fr": "Étanchéité entre unités de climatisation de toit",
        "it": "Impermeabilizzazione tra unità A/C di copertura",
    },
    "Trabajos en planta de cemento": {
        "en": "Works at cement plant",
        "fr": "Travaux en cimenterie",
        "it": "Lavori in cementificio",
    },
    "Tablero eléctrico industrial": {
        "en": "Industrial electrical panel",
        "fr": "Tableau électrique industriel",
        "it": "Quadro elettrico industriale",
    },
    "Grúa Grove transportada en plataforma extensible": {
        "en": "Grove crane transported on extendable trailer",
        "fr": "Grue Grove transportée sur plateau extensible",
        "it": "Gru Grove trasportata su pianale estensibile",
    },
    "Equipos de refrigeración industrial": {
        "en": "Industrial refrigeration equipment",
        "fr": "Équipements de réfrigération industrielle",
        "it": "Apparecchiature di refrigerazione industriale",
    },
    "Mantenimiento Liebert": {
        "en": "Liebert maintenance",
        "fr": "Maintenance Liebert",
        "it": "Manutenzione Liebert",
    },
    "Techo impermeabilizado en planta química industrial": {
        "en": "Waterproofed roof at chemical plant",
        "fr": "Toit étanche en usine chimique industrielle",
        "it": "Tetto impermeabilizzato in impianto chimico industriale",
    },
    "Soldadura con careta protectora": {
        "en": "Welding with protective mask",
        "fr": "Soudage avec masque de protection",
        "it": "Saldatura con maschera protettiva",
    },
    "Instrumentación eléctrica": {
        "en": "Electrical instrumentation",
        "fr": "Instrumentation électrique",
        "it": "Strumentazione elettrica",
    },
    "Vista amplia de techo impermeabilizado con refinería al fondo": {
        "en": "Wide view of waterproofed roof with refinery in background",
        "fr": "Vue large de toit étanche avec raffinerie en arrière-plan",
        "it": "Ampia vista di tetto impermeabilizzato con raffineria sullo sfondo",
    },
    "Diagnóstico eléctrico": {
        "en": "Electrical diagnostics",
        "fr": "Diagnostic électrique",
        "it": "Diagnostica elettrica",
    },
    "Mantenimiento de equipos HVAC": {
        "en": "HVAC equipment maintenance",
        "fr": "Maintenance d'équipements CVC",
        "it": "Manutenzione di apparecchiature HVAC",
    },
    "Trabajos de impermeabilización con parapeto y andamios": {
        "en": "Waterproofing work with parapet and scaffolding",
        "fr": "Travaux d'étanchéité avec parapet et échafaudages",
        "it": "Lavori di impermeabilizzazione con parapetto e ponteggi",
    },
    # --- Contacto ---
    "Operaciones Innoven en planta industrial": {
        "en": "Innoven operations at industrial plant",
        "fr": "Opérations Innoven en usine industrielle",
        "it": "Operazioni Innoven in impianto industriale",
    },
    "08 / Contacto": {
        "en": "08 / Contact",
        "fr": "08 / Contact",
        "it": "08 / Contatto",
    },
    'Hablemos de tu<br /><span class="text-brand"\n                >próximo proyecto</span\n              >.': {
        "en": 'Let\'s talk about your<br /><span class="text-brand"\n                >next project</span\n              >.',
        "fr": 'Parlons de votre<br /><span class="text-brand"\n                >prochain projet</span\n              >.',
        "it": 'Parliamo del tuo<br /><span class="text-brand"\n                >prossimo progetto</span\n              >.',
    },
    "Cuéntanos qué necesita tu operación. Respondemos en menos de 24\n              horas con una propuesta técnica adaptada al alcance del proyecto.": {
        "en": "Tell us what your operation needs. We reply in under 24\n              hours with a technical proposal adapted to the project scope.",
        "fr": "Dites-nous ce dont votre opération a besoin. Nous répondons en moins de 24\n              heures avec une proposition technique adaptée à l'envergure du projet.",
        "it": "Dicci di cosa ha bisogno la tua operazione. Rispondiamo in meno di 24\n              ore con una proposta tecnica adattata all'ambito del progetto.",
    },
    "Operaciones · WhatsApp": {
        "en": "Operations · WhatsApp",
        "fr": "Opérations · WhatsApp",
        "it": "Operazioni · WhatsApp",
    },
    "Sede principal": {
        "en": "Headquarters",
        "fr": "Siège principal",
        "it": "Sede principale",
    },
    "Av. 4A con calle 78, Edif. Banco Unión<br />\n                    Piso 3, Local 03 · Sector Bella Vista<br />\n                    Maracaibo, Zulia 4002 · Venezuela": {
        "en": "4A Ave. & Calle 78, Banco Unión Bldg.<br />\n                    Floor 3, Suite 03 · Bella Vista<br />\n                    Maracaibo, Zulia 4002 · Venezuela",
        "fr": "Av. 4A et Rue 78, Édifice Banco Unión<br />\n                    3ème Étage, Local 03 · Bella Vista<br />\n                    Maracaibo, Zulia 4002 · Venezuela",
        "it": "Av. 4A e Calle 78, Edificio Banco Unión<br />\n                    3° Piano, Locale 03 · Bella Vista<br />\n                    Maracaibo, Zulia 4002 · Venezuela",
    },
    "Disponibilidad": {
        "en": "Availability",
        "fr": "Disponibilité",
        "it": "Disponibilità",
    },
    "Personal especializado para emergencias operativas": {
        "en": "Specialized staff for operational emergencies",
        "fr": "Personnel spécialisé pour urgences opérationnelles",
        "it": "Personale specializzato per emergenze operative",
    },
    ">Nombre *<": {"en": ">Name *<", "fr": ">Nom *<", "it": ">Nome *<"},
    ">Empresa<": {"en": ">Company<", "fr": ">Entreprise<", "it": ">Azienda<"},
    ">Email *<": {"en": ">Email *<", "fr": ">Email *<", "it": ">Email *<"},
    ">Teléfono<": {"en": ">Phone<", "fr": ">Téléphone<", "it": ">Telefono<"},
    "Tu nombre completo": {
        "en": "Your full name",
        "fr": "Votre nom complet",
        "it": "Il tuo nome completo",
    },
    "Nombre de tu empresa": {
        "en": "Your company name",
        "fr": "Nom de votre entreprise",
        "it": "Nome della tua azienda",
    },
    "tu@empresa.com": {
        "en": "you@company.com",
        "fr": "vous@entreprise.com",
        "it": "tu@azienda.com",
    },
    ">Servicio de interés *<": {
        "en": ">Service of interest *<",
        "fr": ">Service d'intérêt *<",
        "it": ">Servizio di interesse *<",
    },
    "Selecciona un servicio": {
        "en": "Select a service",
        "fr": "Sélectionnez un service",
        "it": "Seleziona un servizio",
    },
    "Aislamiento e Integridad Térmica": {
        "en": "Thermal Insulation & Integrity",
        "fr": "Isolation et Intégrité Thermiques",
        "it": "Isolamento e Integrità Termica",
    },
    "Procura de materiales / equipos": {
        "en": "Procurement of materials / equipment",
        "fr": "Approvisionnement de matériaux / équipements",
        "it": "Approvvigionamento di materiali / attrezzature",
    },
    "Proyecto integral / Otro": {
        "en": "Integrated project / Other",
        "fr": "Projet intégré / Autre",
        "it": "Progetto integrato / Altro",
    },
    ">Detalle del proyecto *<": {
        "en": ">Project details *<",
        "fr": ">Détails du projet *<",
        "it": ">Dettagli del progetto *<",
    },
    "Cuéntanos sobre el alcance, ubicación y plazos estimados del proyecto...": {
        "en": "Tell us about the scope, location and estimated timeline of the project...",
        "fr": "Décrivez l'envergure, le lieu et les délais estimés du projet...",
        "it": "Raccontaci ambito, posizione e tempistiche stimate del progetto...",
    },
    "Por favor verifica que no eres un robot.": {
        "en": "Please verify that you are not a robot.",
        "fr": "Veuillez vérifier que vous n'êtes pas un robot.",
        "it": "Verifica di non essere un robot.",
    },
    "Enviar solicitud": {
        "en": "Send request",
        "fr": "Envoyer la demande",
        "it": "Invia richiesta",
    },
    "Al enviar este formulario aceptas que INNOVEN C.A. utilice tus\n                datos exclusivamente para responder tu solicitud comercial.": {
        "en": "By submitting this form you agree that INNOVEN C.A. will use your\n                data exclusively to respond to your commercial request.",
        "fr": "En soumettant ce formulaire, vous acceptez que INNOVEN C.A. utilise vos\n                données exclusivement pour répondre à votre demande commerciale.",
        "it": "Inviando questo modulo accetti che INNOVEN C.A. utilizzi i tuoi\n                dati esclusivamente per rispondere alla tua richiesta commerciale.",
    },
    # --- Postulaciones CTA ---
    'Postulaciones a\n              <span class="text-brand">vacantes</span>': {
        "en": 'Apply to\n              <span class="text-brand">open positions</span>',
        "fr": 'Postuler aux\n              <span class="text-brand">postes ouverts</span>',
        "it": 'Candidati alle\n              <span class="text-brand">posizioni aperte</span>',
    },
    "Buscamos talento técnico y profesional en ingeniería, operaciones\n              de campo, procura y áreas comerciales para sumarse a un equipo que\n              opera en los sectores industrial y energético de Venezuela.": {
        "en": "We seek technical and professional talent in engineering, field\n              operations, procurement and commercial areas to join a team that\n              operates in the industrial and energy sectors of Venezuela.",
        "fr": "Nous recherchons des talents techniques et professionnels en ingénierie, opérations\n              de terrain, approvisionnement et secteurs commerciaux pour rejoindre une équipe qui\n              opère dans les secteurs industriel et énergétique du Venezuela.",
        "it": "Cerchiamo talenti tecnici e professionali in ingegneria, operazioni\n              sul campo, approvvigionamento e aree commerciali per unirsi a un team che\n              opera nei settori industriale ed energetico del Venezuela.",
    },
    "Operaciones 24/7/365": {
        "en": "Operations 24/7/365",
        "fr": "Opérations 24/7/365",
        "it": "Operazioni 24/7/365",
    },
    "Equipo técnico especializado": {
        "en": "Specialized technical team",
        "fr": "Équipe technique spécialisée",
        "it": "Team tecnico specializzato",
    },
    "Sectores industrial y energético": {
        "en": "Industrial and energy sectors",
        "fr": "Secteurs industriel et énergétique",
        "it": "Settori industriale ed energetico",
    },
    "Crecimiento profesional": {
        "en": "Professional growth",
        "fr": "Croissance professionnelle",
        "it": "Crescita professionale",
    },
    "Áreas con vacantes activas": {
        "en": "Areas with active openings",
        "fr": "Domaines avec postes ouverts",
        "it": "Aree con posizioni aperte",
    },
    "Ingeniería Mecánica · Civil · Eléctrica": {
        "en": "Mechanical · Civil · Electrical Engineering",
        "fr": "Ingénierie Mécanique · Civile · Électrique",
        "it": "Ingegneria Meccanica · Civile · Elettrica",
    },
    "Operaciones de campo y supervisión": {
        "en": "Field operations and supervision",
        "fr": "Opérations de terrain et supervision",
        "it": "Operazioni sul campo e supervisione",
    },
    "Procura, logística y almacén": {
        "en": "Procurement, logistics and warehouse",
        "fr": "Approvisionnement, logistique et entrepôt",
        "it": "Approvvigionamento, logistica e magazzino",
    },
    "Comercial y atención al cliente": {
        "en": "Commercial and customer service",
        "fr": "Commercial et service client",
        "it": "Commerciale e servizio clienti",
    },
    "Administración y finanzas": {
        "en": "Administration and finance",
        "fr": "Administration et finances",
        "it": "Amministrazione e finanza",
    },
    "SIHAO · Calidad": {
        "en": "OHSE · Quality",
        "fr": "HSE · Qualité",
        "it": "HSE · Qualità",
    },
    "¿No ves tu área? El formulario incluye campo libre para que\n                  puedas postularte igualmente.": {
        "en": "Don't see your area? The form includes a free field so you\n                  can apply anyway.",
        "fr": "Vous ne voyez pas votre domaine ? Le formulaire inclut un champ libre pour que\n                  vous puissiez postuler quand même.",
        "it": "Non vedi la tua area? Il modulo include un campo libero per poterti\n                  candidare comunque.",
    },
    # --- In Memoriam ---
    'aria-label="In memoriam"': {
        "en": 'aria-label="In memoriam"',
        "fr": 'aria-label="In memoriam"',
        "it": 'aria-label="In memoriam"',
    },
    "Retrato de Javier López, socio y amigo de Innoven": {
        "en": "Portrait of Javier López, partner and friend of Innoven",
        "fr": "Portrait de Javier López, associé et ami d'Innoven",
        "it": "Ritratto di Javier López, socio e amico di Innoven",
    },
    "Socio, compañero y amigo. Su criterio, su trabajo y su entrega siguen\n          siendo parte de todo lo que hacemos. Lo recordamos siempre con\n          gratitud y cariño.": {
        "en": "Partner, colleague and friend. His judgment, his work and his dedication\n          remain part of everything we do. We remember him always with\n          gratitude and affection.",
        "fr": "Associé, collègue et ami. Son jugement, son travail et son dévouement font\n          toujours partie de tout ce que nous faisons. Nous nous souvenons toujours de lui avec\n          gratitude et affection.",
        "it": "Socio, collega e amico. Il suo giudizio, il suo lavoro e la sua dedizione restano\n          parte di tutto ciò che facciamo. Lo ricordiamo sempre con\n          gratitudine e affetto.",
    },
    # --- Footer ---
    'alt="Innoven Suministros y Servicios"': {
        "en": 'alt="Innoven Supplies & Services"',
        "fr": 'alt="Innoven Fournitures et Services"',
        "it": 'alt="Innoven Forniture e Servizi"',
    },
    "Empresa venezolana especializada en la prestación de servicios\n              industriales integrales y procura para el sector industrial y\n              energético.": {
        "en": "Venezuelan company specialized in providing integrated\n              industrial services and procurement for the industrial and\n              energy sectors.",
        "fr": "Entreprise vénézuélienne spécialisée dans la prestation de services\n              industriels intégrés et l'approvisionnement pour les secteurs industriel et\n              énergétique.",
        "it": "Azienda venezuelana specializzata nella fornitura di servizi\n              industriali integrati e approvvigionamento per i settori industriale ed\n              energetico.",
    },
    "Av. 4A con calle 78, Edif. Banco Unión<br />\n              Piso 3, Local 03 · Sector Bella Vista<br />\n              Maracaibo, Zulia 4002 · Venezuela": {
        "en": "4A Ave. & Calle 78, Banco Unión Bldg.<br />\n              Floor 3, Suite 03 · Bella Vista<br />\n              Maracaibo, Zulia 4002 · Venezuela",
        "fr": "Av. 4A et Rue 78, Édifice Banco Unión<br />\n              3ème Étage, Local 03 · Bella Vista<br />\n              Maracaibo, Zulia 4002 · Venezuela",
        "it": "Av. 4A e Calle 78, Edificio Banco Unión<br />\n              3° Piano, Locale 03 · Bella Vista<br />\n              Maracaibo, Zulia 4002 · Venezuela",
    },
    ">Servicios<": {"en": ">Services<", "fr": ">Services<", "it": ">Servizi<"},
    ">Empresa<": {"en": ">Company<", "fr": ">Entreprise<", "it": ">Azienda<"},
    ">Aislamiento Térmico<": {
        "en": ">Thermal Insulation<",
        "fr": ">Isolation Thermique<",
        "it": ">Isolamento Termico<",
    },
    ">Refrigeración Industrial<": {
        "en": ">Industrial Refrigeration<",
        "fr": ">Réfrigération Industrielle<",
        "it": ">Refrigerazione Industriale<",
    },
    ">Civil e Industrial<": {
        "en": ">Civil & Industrial<",
        "fr": ">Civil et Industriel<",
        "it": ">Civile e Industriale<",
    },
    ">Empacaduras<": {"en": ">Gaskets<", "fr": ">Joints<", "it": ">Guarnizioni<"},
    'class="hover:text-brand transition"\n                  >Nosotros</a': {
        "en": 'class="hover:text-brand transition"\n                  >About</a',
        "fr": 'class="hover:text-brand transition"\n                  >À Propos</a',
        "it": 'class="hover:text-brand transition"\n                  >Chi Siamo</a',
    },
    'class="hover:text-brand transition"\n                  >Sectores</a': {
        "en": 'class="hover:text-brand transition"\n                  >Sectors</a',
        "fr": 'class="hover:text-brand transition"\n                  >Secteurs</a',
        "it": 'class="hover:text-brand transition"\n                  >Settori</a',
    },
    'class="hover:text-brand transition">Equipo</a>': {
        "en": 'class="hover:text-brand transition">Team</a>',
        "fr": 'class="hover:text-brand transition">Équipe</a>',
        "it": 'class="hover:text-brand transition">Team</a>',
    },
    'class="hover:text-brand transition">Morgan</a>': {
        "en": 'class="hover:text-brand transition">Morgan</a>',
        "fr": 'class="hover:text-brand transition">Morgan</a>',
        "it": 'class="hover:text-brand transition">Morgan</a>',
    },
    'class="hover:text-brand transition"\n                  >Clientes</a': {
        "en": 'class="hover:text-brand transition"\n                  >Clients</a',
        "fr": 'class="hover:text-brand transition"\n                  >Clients</a',
        "it": 'class="hover:text-brand transition"\n                  >Clienti</a',
    },
    'class="hover:text-brand transition"\n                  >Postulaciones</a': {
        "en": 'class="hover:text-brand transition"\n                  >Careers</a',
        "fr": 'class="hover:text-brand transition"\n                  >Carrières</a',
        "it": 'class="hover:text-brand transition"\n                  >Carriere</a',
    },
    "Contacto directo": {
        "en": "Direct contact",
        "fr": "Contact direct",
        "it": "Contatto diretto",
    },
    ">Operaciones</span": {
        "en": ">Operations</span",
        "fr": ">Opérations</span",
        "it": ">Operazioni</span",
    },
    ">Administración</span": {
        "en": ">Administration</span",
        "fr": ">Administration</span",
        "it": ">Amministrazione</span",
    },
    ">Compras y Procura</span": {
        "en": ">Procurement</span",
        "fr": ">Achats et Approvisionnement</span",
        "it": ">Acquisti e Approvvigionamento</span",
    },
    ">Recursos Humanos</span": {
        "en": ">Human Resources</span",
        "fr": ">Ressources Humaines</span",
        "it": ">Risorse Umane</span",
    },
    "INNOVEN C.A. — Suministros y\n            Servicios. Todos los derechos reservados.": {
        "en": "INNOVEN C.A. — Supplies &\n            Services. All rights reserved.",
        "fr": "INNOVEN C.A. — Fournitures et\n            Services. Tous droits réservés.",
        "it": "INNOVEN C.A. — Forniture e\n            Servizi. Tutti i diritti riservati.",
    },
    'aria-label="Web developed by 1bite Studio"': {
        "en": 'aria-label="Web developed by 1bite Studio"',
        "fr": 'aria-label="Site développé par 1bite Studio"',
        "it": 'aria-label="Sito sviluppato da 1bite Studio"',
    },
    # --- Don't see sector + final ones ---
    "Cuéntanos tu caso": {
        "en": "Tell us your case",
        "fr": "Parlez-nous de votre cas",
        "it": "Raccontaci il tuo caso",
    },
    "Trabaja con nosotros": {
        "en": "Work with us",
        "fr": "Travaillez avec nous",
        "it": "Lavora con noi",
    },
}

# ============================================================ MAIN


def apply_translations(text, lang):
    # Apply in dict insertion order, longest first as a tiebreak
    items = sorted(T.items(), key=lambda kv: -len(kv[0]))
    for src, tr in items:
        if lang in tr:
            text = text.replace(src, tr[lang])
    return text


def inject_structural(text, active_lang):
    """Inject hreflang, lang switcher (desktop+mobile), CSS, JS into the HTML."""
    # 1. CSS for switcher (inside <style>)
    text = replace_or_insert(text, CSS_S, CSS_E, SWITCHER_CSS, CSS_ANCHOR)

    # 2. hreflang block (after canonical)
    text = replace_or_insert(
        text, HREFLANG_S, HREFLANG_E, HREFLANG_BLOCK, HREFLANG_ANCHOR
    )

    # 3. desktop switcher (before #menu-btn — must be position="before" so we don't break the button tag)
    text = replace_or_insert(
        text,
        SW_S,
        SW_E,
        desktop_switcher(active_lang),
        DESKTOP_SWITCHER_ANCHOR,
        position="before",
    )

    # 4. mobile switcher (after mobile <nav> opens)
    text = replace_or_insert(
        text, SWM_S, SWM_E, mobile_switcher(active_lang), MOBILE_SWITCHER_ANCHOR
    )

    # 5. JS init (after first comment in main script)
    text = replace_or_insert(text, JS_S, JS_E, LANG_JS, JS_ANCHOR)

    return text


def main():
    # --- Pass 1: rewrite ES (index.html) with structural injections only ---
    with open(SRC, "r", encoding="utf-8") as f:
        es = f.read()
    es_out = inject_structural(es, "es")
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(es_out)
    print(f"Wrote ES: {SRC}")

    # --- Pass 2: each locale: paths + head fixes + structural + translations ---
    for lang in LANGS:
        text = es_out  # start from ES with structural already injected
        # path fixes for subdirectory
        for src, dst in PATH_FIXES:
            text = text.replace(src, dst)
        # head fixes
        for src, dst in head_fixes(lang):
            text = text.replace(src, dst)
        # adjust hreflang URLs in the locale (already absolute so no change)
        # adjust lang switcher to mark this lang as active (re-inject)
        # We need to swap the desktop + mobile switcher with active=lang
        text = re.sub(
            re.escape(SW_S) + r"[\s\S]*?" + re.escape(SW_E),
            SW_S + "\n" + desktop_switcher(lang) + "\n" + SW_E,
            text,
        )
        text = re.sub(
            re.escape(SWM_S) + r"[\s\S]*?" + re.escape(SWM_E),
            SWM_S + "\n" + mobile_switcher(lang) + "\n" + SWM_E,
            text,
        )
        # Adjust switcher relative paths: in /en/, ES = "../", EN = "./" etc.
        # But we kept absolute paths "/", "/en/" — those work in both local server (root) and prod.
        # translations
        text = apply_translations(text, lang)

        out_dir = os.path.join(ROOT, lang)
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, "index.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Wrote {lang.upper()}: {out}")

    print("\nDone. Run grep checks to find remaining Spanish.")


if __name__ == "__main__":
    main()
