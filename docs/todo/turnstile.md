# TODO: Integrar Cloudflare Turnstile en el formulario de contacto

## ¿Qué es Turnstile?

Cloudflare Turnstile es un sistema CAPTCHA de privacidad amigable que no requiere que el usuario
resuelva puzzles. Detecta bots de forma transparente mediante señales de comportamiento del cliente.
Es gratuito y no rastrea a los usuarios.

## Pasos de integración manual

### 1. Crear una cuenta en Cloudflare y registrar el sitio

1. Ve a [https://dash.cloudflare.com](https://dash.cloudflare.com) e inicia sesión o crea una cuenta.
2. En el menú lateral, navega a **Turnstile**.
3. Haz clic en **Añadir sitio web**.
4. Introduce el dominio del sitio (p. ej. `staysidekick.com` o el dominio de Railway).
5. Selecciona el modo de widget: **Managed** (recomendado — sin interacción visible para usuarios legítimos).
6. Haz clic en **Crear**.
7. Copia la **Clave del sitio (Site Key)** y la **Clave secreta (Secret Key)**.

### 2. Añadir el script de Turnstile en el layout base

En `web/src/_includes/layouts/base.njk`, añade antes del cierre de `</body>`:

```html
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
```

### 3. Insertar el widget en el formulario de contacto

En `web/src/empresa/contacto.njk`, localiza el comentario:

```njk
{# TODO: Insertar widget Turnstile aquí — ver docs/todo/turnstile.md #}
```

Y reemplázalo por:

```html
<div
  class="cf-turnstile"
  data-sitekey="<TU_SITE_KEY>"
  data-theme="light"
></div>
```

Sustituye `<TU_SITE_KEY>` por la clave del sitio obtenida en el paso 1.
**Nunca** expongas la clave secreta en el frontend.

### 4. Verificar el token en el endpoint serverless (backend)

Cuando el formulario se envíe al endpoint serverless (aún pendiente de implementar), el servidor
debe verificar el token `cf-turnstile-response` que Turnstile añade automáticamente al formulario.

Ejemplo de verificación con `fetch` desde Node.js / Python:

```
POST https://challenges.cloudflare.com/turnstile/v0/siteverify
Content-Type: application/x-www-form-urlencoded

secret=<TU_SECRET_KEY>&response=<TOKEN_DEL_FORMULARIO>&remoteip=<IP_DEL_CLIENTE>
```

La respuesta incluye un campo `success: true/false`. Rechazar envíos con `success: false`.

### 5. Variables de entorno

La clave secreta debe almacenarse como variable de entorno en el servidor:

```
TURNSTILE_SECRET_KEY=<TU_SECRET_KEY>
```

**Nunca** incluir la clave secreta en el repositorio.

## Documentación oficial

- [Turnstile — Guía de inicio](https://developers.cloudflare.com/turnstile/get-started/)
- [Verificación del lado del servidor](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/)
