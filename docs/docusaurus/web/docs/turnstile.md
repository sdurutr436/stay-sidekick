---
id: turnstile
title: Cloudflare Turnstile
sidebar_position: 5
description: Cómo se inyecta la site key del antibot en las plantillas y dónde se valida en el backend.
---

# Cloudflare Turnstile

El sitio 11ty usa **Turnstile** como antibot en los formularios públicos (contacto y solicitud de empresa). La integración se reparte entre tres puntos: variable de entorno, datafile expuesto a Nunjucks, y script en el `<head>` del layout.

## 1. Variable de entorno

| Variable | Dónde | Cómo se rellena |
|----------|-------|-----------------|
| `TURNSTILE_SITE_KEY` | `web/.env` (local) o `ARG TURNSTILE_SITE_KEY` (Docker) | Site key pública de Cloudflare; en local sirve la test key oficial `1x00000000000000000000AA`. |

En Docker no hace falta editar `.env`: el `Dockerfile` recibe el `ARG TURNSTILE_SITE_KEY` y lo exporta como `ENV` antes de `pnpm run build`, por lo que `process.env.TURNSTILE_SITE_KEY` queda disponible para Eleventy.

## 2. Datafile

[`web/src/_data/config.js`](https://github.com/sdurutr436/stay-sidekick/blob/main/web/src/_data/config.js) lee la variable y la expone como `config.turnstileSiteKey`:

```js
require('dotenv').config();
module.exports = {
  turnstileSiteKey: process.env.TURNSTILE_SITE_KEY || '',
};
```

Eleventy carga automáticamente todo lo que esté en `_data/` y lo inyecta a las plantillas como variable global.

## 3. Uso en plantillas

En el `<head>` del layout base se incluye el script de Turnstile referenciando la site key:

```njk
<script
  src="https://challenges.cloudflare.com/turnstile/v0/api.js"
  data-sitekey="{{ config.turnstileSiteKey }}"
  defer
></script>
```

En el formulario, el widget se renderiza con:

```html
<div class="cf-turnstile" data-sitekey="{{ config.turnstileSiteKey }}"></div>
```

El widget genera un token que el formulario envía al backend Flask. Allí, el endpoint público verifica el token contra `https://challenges.cloudflare.com/turnstile/v0/siteverify` usando `TURNSTILE_SECRET_KEY` (variable de `backend/.env`). Si la verificación falla, devuelve 403.

## Capas adicionales antiabuso

Turnstile no va solo: el endpoint público combina **tres barreras** para mitigar spam y fuerza bruta:

1. **Turnstile** (validación cliente + verificación servidor).
2. **Campo honeypot** oculto — si trae valor, el bot se autodescarta.
3. **Rate limit por IP** (Flask-Limiter) — default `5/hour`, configurable con `RATE_LIMIT_CONTACT`.
