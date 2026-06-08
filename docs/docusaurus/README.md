# Documentación de API — Docusaurus

Este directorio contiene **tres sitios Docusaurus independientes** que generan la documentación técnica de cada uno de los subproyectos de Stay Sidekick. Los tres se publican como un único despliegue en GitHub Pages bajo `https://sdurutr436.github.io/stay-sidekick/` con una landing común que enlaza cada sitio.

## Estructura

| Sitio | Subproyecto | Generador | URL en producción |
|-------|-------------|-----------|-------------------|
| [`web/`](web/) | `web/` — 11ty + Nunjucks | Docusaurus + Markdown manual | `/stay-sidekick/web/` |
| [`frontend/`](frontend/) | `frontend/` — Angular + TypeScript | Docusaurus + `docusaurus-plugin-typedoc` | `/stay-sidekick/frontend/` |
| [`backend/`](backend/) | `backend/` — Flask + Python | Docusaurus + `pydoc-markdown` | `/stay-sidekick/backend/` |

La landing pública (`index.html`) se ensambla en CI por el workflow [`deploy-docs.yml`](../../.github/workflows/deploy-docs.yml) y enlaza a los tres sitios.

## Comandos por sitio

Cada sitio es un proyecto pnpm autónomo. Desde la raíz del repo:

```bash
# Levantar el sitio en modo dev (recarga en caliente)
pnpm -C docs/docusaurus/web start
pnpm -C docs/docusaurus/frontend start
pnpm -C docs/docusaurus/backend start

# Build de producción
pnpm -C docs/docusaurus/web build
pnpm -C docs/docusaurus/frontend build
pnpm -C docs/docusaurus/backend build
```

El sitio `frontend/` ejecuta TypeDoc como pre-build (genera Markdown a `docs/api/` antes de que Docusaurus lo compile). El sitio `backend/` ejecuta `pydoc-markdown` como pre-build sobre `backend/app/` para volcar Markdown a `docs/api/`.

## Convenciones comunes

- **Frontmatter YAML** obligatorio en todo Markdown servido como página de documentación. Mínimo:
  ```yaml
  ---
  id: identificador-unico-en-el-sitio
  title: Título visible en la barra superior y la pestaña del navegador
  sidebar_position: 1
  ---
  ```
- **Versiones**: Docusaurus 3.x, React 18.x, Node 20 LTS, pnpm 10.x — alineadas con el resto del repo.
- **Estilo**: el `src/css/custom.css` de cada sitio extiende la paleta Infima de Docusaurus con los colores corporativos definidos en `frontend/src/styles/settings/_colores.scss`.

## Despliegue

El workflow [`deploy-docs.yml`](../../.github/workflows/deploy-docs.yml) se dispara en cada push a `main` que toque `docs/docusaurus/**`, `frontend/src/**`, `web/src/**` o `backend/app/**`. Construye los tres sitios en paralelo, ensambla la landing y publica en la rama `gh-pages` mediante `actions/deploy-pages`.
