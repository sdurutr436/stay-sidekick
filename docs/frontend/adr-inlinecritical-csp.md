# ADR: inlineCritical desactivado en Angular por incompatibilidad con CSP

## Contexto

Angular en modo `production` activa por defecto la herramienta **Beasties**
(antes Critters), que extrae el CSS crítico de la primera vista e inyecta un
`<style>` inline en el HTML para mejorar el tiempo de renderizado inicial (CLS).
Como efecto secundario, el CSS global restante se carga con el siguiente patrón:

```html
<link rel="stylesheet" href="styles-HASH.css" media="print" onload="this.media='all'">
```

El atributo `onload="this.media='all'"` es un **inline event handler**. El
navegador lo trata como JavaScript inline, por lo que está controlado por la
directiva `script-src` de la Content Security Policy, no por `style-src`.

## Problema

La CSP configurada en nginx (tanto local como Railway) no incluye `'unsafe-inline'`
en `script-src`, por razones de seguridad. El navegador bloquea silenciosamente
el `onload`, la hoja de estilos se queda con `media="print"` para siempre y no
se aplica a la pantalla. Los estilos de Angular no se renderizan.

El CSS sí llega al navegador (respuesta HTTP 200), lo que hace el bug difícil de
detectar sin revisar los headers de seguridad.

## Decisión

Se desactiva `inlineCritical` en la configuración `production` de `angular.json`:

```json
"optimization": {
  "scripts": true,
  "styles": {
    "minify": true,
    "inlineCritical": false
  },
  "fonts": true
}
```

Esto genera un `<link rel="stylesheet" href="...">` estándar, sin `onload`, que
el navegador carga normalmente sin violar la CSP.

## Alternativas descartadas

- **`'unsafe-inline'` en `script-src`**: debilita la CSP y abre la puerta a XSS.
- **Nonce por petición**: requeriría que nginx inyecte un nonce dinámico en cada
  respuesta HTML y lo incluya en la cabecera CSP. Complejidad alta sin beneficio
  real dado el tamaño del proyecto.

## Consecuencias

- Se pierde la optimización de CSS crítico inline (el navegador hace una petición
  adicional para la hoja de estilos antes del primer renderizado).
- La CSP permanece estricta, sin `'unsafe-inline'` en `script-src`.
- El comportamiento es idéntico en local (Docker Compose) y en Railway, ya que
  el cambio es de build-time en el Dockerfile del frontend.
