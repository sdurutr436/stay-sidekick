---
id: estilos-scss
title: Estilos SCSS compartidos
sidebar_position: 4
description: Arquitectura ITCSS y nomenclatura BEM compartida entre el sitio 11ty y la SPA Angular.
---

# Estilos SCSS compartidos

El sitio 11ty y la SPA Angular **comparten exactamente los mismos estilos**. Ambos compilan desde [`frontend/src/styles/`](https://github.com/sdurutr436/stay-sidekick/tree/main/frontend/src/styles), siguiendo arquitectura [ITCSS](https://www.xfive.co/blog/itcss-scalable-maintainable-css-architecture/) y nomenclatura [BEM](https://getbem.com/).

## Cómo se conecta el sitio 11ty con esos estilos

El entry SCSS del sitio es `web/src/assets/styles/main.scss`, que solo importa los `@forward` del directorio compartido. La magia está en el `--load-path` pasado al CLI de Sass:

```jsonc
// web/package.json
"build:css": "sass src/assets/styles/main.scss:_site/assets/styles/main.css --load-path=../frontend/src/styles --no-source-map --style=compressed"
```

Con `--load-path` apuntando al directorio del frontend, los `@use 'settings/colores'` dentro del SCSS compartido resuelven a `frontend/src/styles/settings/_colores.scss`.

## Capas ITCSS

```
frontend/src/styles/
├── settings/   # Variables: tipografía, colores, breakpoints, espaciado
├── tools/      # Mixins reutilizables (responsive, flex, tipografía)
├── generic/    # Reset CSS
├── elements/   # Estilos base de elementos HTML sin clase
├── layout/     # Grid 12 columnas, flex, contenedor
├── components/ # Átomos y organismos BEM (button, badge, header, footer…)
├── utilities/  # Clases utilitarias de alta especificidad (.u-hidden, .u-sr-only)
└── animations/ # Keyframes y clases de animación (.a-fade-in…)
```

La carga ordenada va de **baja a alta especificidad**: primero variables y mixins (no emiten CSS), luego resets globales, luego elementos, layout, componentes y por último utilities/animations.

## Añadir un componente SCSS nuevo

1. Crear `frontend/src/styles/components/_<nombre>.scss` con bloques BEM (`.bloque__elemento--modificador`).
2. Añadir `@forward '<nombre>';` en `frontend/src/styles/components/_index.scss`.
3. El estilo queda disponible al instante en el sitio 11ty y en la SPA Angular sin más pasos.

## Watch en desarrollo

`eleventy.config.js` declara `addWatchTarget('../frontend/src/styles/')` para que Eleventy reinicie el build cuando cambien los estilos. En paralelo, `sass --watch` recompila el CSS — los dos procesos los lanza `npm-run-all --parallel` desde el script `start`.
