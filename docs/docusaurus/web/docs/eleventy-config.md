---
id: eleventy-config
title: Configuración de Eleventy
sidebar_position: 2
description: Desglose del eleventy.config.js — passthrough copy, watch targets, shortcodes y dirs.
---

# Configuración de Eleventy

El archivo [`web/eleventy.config.js`](https://github.com/sdurutr436/stay-sidekick/blob/main/web/eleventy.config.js) define el comportamiento del generador: qué se copia tal cual, qué se observa para reconstruir y qué shortcodes globales están disponibles en las plantillas.

## Estructura del config

```js
module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy('src/assets/img');
  eleventyConfig.addPassthroughCopy('src/assets/fonts');
  eleventyConfig.addPassthroughCopy('src/assets/js');
  eleventyConfig.addPassthroughCopy('src/robots.txt');

  eleventyConfig.addWatchTarget('../frontend/src/styles/');

  eleventyConfig.addShortcode('year', () => String(new Date().getFullYear()));

  return {
    templateFormats: ['njk', 'html', 'md'],
    markdownTemplateEngine: 'njk',
    htmlTemplateEngine: 'njk',
    dir: {
      input: 'src',
      output: '_site',
      includes: '_includes',
      layouts: '_includes/layouts',
      data: '_data',
    },
  };
};
```

## Bloques explicados

### `addPassthroughCopy`

Le dice a Eleventy que copie esos paths tal cual al output sin procesarlos. Necesario para:

- **`src/assets/img/`** — imágenes, favicon y OG-images. Eleventy preserva la estructura interna.
- **`src/assets/fonts/`** — tipografías auto-alojadas para evitar dependencia de Google Fonts (mejor CSP y rendimiento).
- **`src/assets/js/`** — JavaScript vanilla (p.ej. el banner de cookies).
- **`src/robots.txt`** — archivo de raíz para indexación.

> **Importante:** el CSS no entra como passthrough — se compila con Sass directamente sobre `_site/assets/styles/main.css` desde el script `build:css` del `package.json`. Eso evita carreras entre la copia de Eleventy y la salida de Sass.

### `addWatchTarget`

Eleventy reinicia el build cuando cambian archivos en `../frontend/src/styles/`. Como el SCSS es compartido con la SPA Angular y vive fuera del input de Eleventy, hay que añadirlo explícitamente para que `eleventy --serve` reaccione al editar variables, mixins o componentes BEM.

### Shortcodes

Sólo uno por ahora: `{% year %}` devuelve el año actual. Útil en el footer (`© 2026 Stay Sidekick`) sin hardcodear la fecha. Añadir nuevos shortcodes globales aquí los hace disponibles a todas las plantillas Nunjucks.

### Bloque `dir`

| Propiedad | Valor | Para qué sirve |
|-----------|-------|----------------|
| `input` | `src` | Directorio de plantillas y datos |
| `output` | `_site` | Carpeta servida por nginx en producción |
| `includes` | `_includes` | Resolución de `{% include %}` |
| `layouts` | `_includes/layouts` | Resolución de `layout:` en frontmatter |
| `data` | `_data` | Datos globales (`site`, `config`) inyectados en todas las plantillas |

`templateFormats` limita a `njk`, `html` y `md`. `markdownTemplateEngine: 'njk'` permite usar sintaxis Nunjucks dentro de archivos `.md`.
