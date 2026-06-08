---
id: intro
title: Introducción
slug: /
sidebar_position: 1
description: Documentación del sitio estático 11ty + Nunjucks de Stay Sidekick.
---

# Sitio estático — 11ty + Nunjucks

Este sitio Docusaurus documenta el subproyecto [`web/`](https://github.com/sdurutr436/stay-sidekick/tree/main/web) de Stay Sidekick: la **landing pública** (páginas de marketing, legales y empresa) construida con **Eleventy 3** y plantillas **Nunjucks**, con estilos SCSS compartidos con la SPA Angular.

## Visión general

| Pieza | Tecnología | Punto de entrada |
|-------|------------|------------------|
| Generador estático | [Eleventy 3](https://www.11ty.dev/) | [`web/eleventy.config.js`](https://github.com/sdurutr436/stay-sidekick/blob/main/web/eleventy.config.js) |
| Motor de plantillas | [Nunjucks](https://mozilla.github.io/nunjucks/) | [`web/src/_includes/`](https://github.com/sdurutr436/stay-sidekick/tree/main/web/src/_includes) |
| Estilos | SCSS compilado con `sass` desde [`frontend/src/styles/`](https://github.com/sdurutr436/stay-sidekick/tree/main/frontend/src/styles) | [`web/src/assets/styles/main.scss`](https://github.com/sdurutr436/stay-sidekick/blob/main/web/src/assets/styles/main.scss) |
| Variables al runtime | dotenv → `_data/config.js` | [`web/src/_data/config.js`](https://github.com/sdurutr436/stay-sidekick/blob/main/web/src/_data/config.js) |
| Antibot del formulario | Cloudflare Turnstile | inyectado en `<head>` de cada layout |

## Estructura de carpetas

```
web/
├── eleventy.config.js          # Configuración 11ty (output, watch, shortcodes)
├── package.json                # Scripts pnpm: build:css, build:11ty, build, start
├── nginx.conf                  # Servido en /  detrás del proxy nginx
├── Dockerfile                  # Multi-stage build (Node 20 + nginx:alpine)
└── src/
    ├── _includes/
    │   ├── layouts/base.njk    # Layout HTML completo (head, header, footer)
    │   └── partials/           # Header, footer y banner de cookies
    ├── _data/
    │   ├── site.js             # Datos globales del sitio
    │   └── config.js           # Variables de entorno (Turnstile site key)
    ├── assets/
    │   ├── styles/main.scss    # Entry SCSS que carga ../frontend/src/styles/
    │   ├── img/                # Imágenes (incluido favicon)
    │   ├── fonts/              # Tipografías auto-alojadas
    │   └── js/                 # JS vanilla del banner de cookies
    ├── empresa/                # /empresa/sobre-nosotros, /contacto…
    ├── legal/                  # /legal/privacidad, /terminos, /cookies
    └── producto/               # /producto/funcionalidades, /precios…
```

## Flujo de build

1. **`pnpm install`** instala Eleventy, Sass, dotenv y `npm-run-all` (`pnpm.onlyBuiltDependencies` aprueba el postinstall de `@parcel/watcher`).
2. **`pnpm run build:css`** compila `src/assets/styles/main.scss` → `_site/assets/styles/main.css` cargando los SCSS compartidos con la SPA Angular mediante `--load-path=../frontend/src/styles`.
3. **`pnpm run build:11ty`** ejecuta Eleventy: convierte cada `.njk` en `src/` a HTML en `_site/`, aplica los `passthrough copy` (`img`, `fonts`, `js`, `robots.txt`) y respeta los `addWatchTarget` para reconstruir cuando cambian los estilos compartidos.

En desarrollo, `pnpm start` lanza Sass y Eleventy en paralelo con `npm-run-all`, y el sitio queda en `http://localhost:8080`.

## Lectura recomendada

- [Configuración de Eleventy](eleventy-config) — qué hace cada bloque de `eleventy.config.js` y cómo añadir shortcodes nuevos.
- [Plantillas Nunjucks](plantillas-nunjucks) — layouts, partials y convenciones para las páginas.
- [Estilos SCSS compartidos](estilos-scss) — la arquitectura ITCSS común con la SPA Angular.
- [Cloudflare Turnstile](turnstile) — cómo se inyecta la site key y se valida en backend.
