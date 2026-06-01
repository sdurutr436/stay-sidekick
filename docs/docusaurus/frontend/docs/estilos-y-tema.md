---
id: estilos-y-tema
title: Estilos y tema claro/oscuro
sidebar_position: 4
description: Cómo se aplica la paleta ITCSS y cómo se persiste el modo del usuario.
---

# Estilos y tema claro/oscuro

La SPA usa la misma arquitectura SCSS que el sitio 11ty (ITCSS + BEM), descrita en detalle en la documentación de [`web/`](https://sdurutr436.github.io/stay-sidekick/web/estilos-scss/). Aquí se explica cómo Angular consume esos estilos y cómo se gestiona el modo claro/oscuro persistido por usuario.

## Carga del SCSS global

El entry `frontend/src/styles.scss` re-exporta el directorio compartido:

```scss
@use 'settings';
@use 'tools';
@use 'generic';
@use 'elements';
@use 'layout';
@use 'components';
@use 'utilities';
@use 'animations';
```

`angular.json` declara este entry en `architect.build.options.styles`, por lo que se inyecta como `<link rel="stylesheet">` en el `index.html`.

> Importante: **`inlineCritical: false`** en `angular.json → optimization.styles`. Sin este flag, el builder de Angular usaría Beasties para inlinear CSS crítico con `onload=`, lo cual viola la CSP estricta de nginx y rompería el render.

## Modo claro/oscuro

El servicio [`ThemeService`](https://github.com/sdurutr436/stay-sidekick/blob/main/frontend/src/app/services/theme.service.ts) gestiona el modo. Funcionamiento:

1. Al arrancar, lee el modo guardado en `localStorage` con la clave `stay-sidekick.theme`.
2. Si no hay valor, aplica `prefers-color-scheme` del sistema.
3. Aplica el atributo `data-theme="light"` o `data-theme="dark"` al `<html>`.
4. Cualquier componente puede llamar `themeService.toggle()` para alternar.

Las variables SCSS están definidas dos veces — una bajo `:root` (modo claro) y otra bajo `:root[data-theme='dark']`. El resto del SCSS sólo usa esas variables, lo que evita duplicar reglas por modo.

## Animaciones

Las clases prefijadas con `.a-` (en `styles/animations/`) son globales y reutilizables: `.a-fade-in`, `.a-slide-up`, `.a-spinner`. Se aplican con `[class.a-fade-in]="cargado"` desde la plantilla.

## Tipografía y escala

Las variables tipográficas viven en `styles/settings/_tipografia.scss`. La escala modular se aplica con el mixin `tipografia($variant)` (en `tools/_tipografia.scss`) que centraliza familia, peso, tamaño y alto de línea por variante.

```scss
.card-herramienta__titulo {
  @include tipografia('h3');
}
```

Esta indirección permite cambiar la jerarquía tipográfica en un único punto sin tocar componentes.
