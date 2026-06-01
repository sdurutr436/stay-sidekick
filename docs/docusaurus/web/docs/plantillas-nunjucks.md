---
id: plantillas-nunjucks
title: Plantillas Nunjucks
sidebar_position: 3
description: Layout base, partials reutilizables y convenciones de páginas en el sitio 11ty.
---

# Plantillas Nunjucks

El sitio usa Nunjucks como motor de plantillas. Sigue una jerarquía simple **layout → page → partial** que evita la duplicación de marcado en el `<head>`, header y footer.

## Layout base

Toda página hereda de [`web/src/_includes/layouts/base.njk`](https://github.com/sdurutr436/stay-sidekick/blob/main/web/src/_includes/layouts/base.njk):

```html
<!doctype html>
<html lang="es">
  <head>
    <!-- meta, OG, favicon, CSS, Turnstile script -->
  </head>
  <body>
    {% include "partials/header.njk" %}
    <main>{{ content | safe }}</main>
    {% include "partials/footer.njk" %}
    {% include "partials/cookie-banner.njk" %}
  </body>
</html>
```

Las páginas concretas declaran el layout en su frontmatter:

```yaml
---
layout: layouts/base.njk
title: Funcionalidades — Stay Sidekick
description: Catálogo de herramientas operacionales para alquiler vacacional.
permalink: /producto/funcionalidades/
---
```

## Partials reutilizables

| Partial | Función |
|---------|---------|
| `partials/header.njk` | Logo, navegación principal y CTA hacia el panel. Mismo BEM que `frontend/src/app/components/header/`. |
| `partials/footer.njk` | Enlaces legales, RRSS y créditos. Usa el shortcode `{% year %}`. |
| `partials/cookie-banner.njk` | Banner de cookies técnicas; persistencia en `localStorage`. |

> **Regla**: el HTML de `header.njk` y `footer.njk` debe ser **idéntico en BEM** al de los componentes Angular equivalentes (`frontend/src/app/components/header/header.html` y `footer.html`). Eso garantiza que el usuario perciba la misma navegación pasando de la landing a la SPA.

## Datos inyectados

Todas las plantillas reciben dos diccionarios globales desde [`web/src/_data/`](https://github.com/sdurutr436/stay-sidekick/tree/main/web/src/_data):

- `site` — nombre de marca, año, URLs, claims comerciales (`web/src/_data/site.js`).
- `config` — variables de entorno expuestas al runtime, hoy sólo `config.turnstileSiteKey` (`web/src/_data/config.js`).

Ejemplo de uso en una plantilla:

```njk
<meta name="description" content="{{ site.tagline }}">
<script
  src="https://challenges.cloudflare.com/turnstile/v0/api.js"
  data-sitekey="{{ config.turnstileSiteKey }}"
  defer
></script>
```

## Convenciones

- Cada página vive en `web/src/<area>/<slug>.njk` y declara `permalink:` para forzar la URL pública.
- Las áreas son `empresa/`, `legal/` y `producto/`. Las páginas raíz (`index.njk`, `login/`, `solicitud/`, `cambio-password/`) viven directamente en `src/`.
- El `sitemap.njk` se regenera en cada build a partir del listado de páginas con `eleventyExcludeFromCollections: false` (todas por defecto).
