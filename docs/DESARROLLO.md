# Guía de desarrollo

## Puertos y servicios

| Servicio | URL | Comando |
|----------|-----|---------|
| Sitio estático (11ty) | http://localhost:8080 | `npm run dev:web` |
| App Angular | http://localhost:4200 | `npm run dev:app` |
| API Flask | http://localhost:5000 | `cd backend && python run.py` |

## Inicio de todos los servicios frontend

Desde la raíz del proyecto:

```bash
# Linux / macOS
./dev.sh

# Windows
dev.bat

# Cualquier plataforma (requiere npm install en raíz primero)
npm run dev
```

El script levanta 11ty y Angular en paralelo con salida de logs diferenciada por color. Si alguno de los dos falla, el otro también se detiene (`--kill-others-on-fail`).

## Estilos SCSS compartidos

La arquitectura de estilos sigue **ITCSS** con nomenclatura **BEM**. Los archivos viven en `frontend/src/styles/` y son compilados por ambos proyectos:

- **Angular** los compila automáticamente via `@angular/build`.
- **11ty** los compila con `sass --load-path=../frontend/src/styles` (ver `web/package.json`).

Esto garantiza que el sitio estático y la app dinámica compartan exactamente los mismos estilos y que navegar entre ambos sea visualmente transparente.

### Capas ITCSS

```
Settings   → Variables (tipografía, colores, breakpoints, espaciado)
Tools      → Mixins reutilizables (responsive, flex, tipografía)
Generic    → Reset CSS
Elements   → Estilos de elementos HTML sin clase
Layout     → Grid 12 col, flex utilities, contenedor
Components → Átomos y organismos BEM (button, badge, logo, header, footer…)
Utilities  → Clases de ayuda de alta especificidad (.u-hidden, .u-sr-only…)
Animations → Keyframes y clases de animación (.a-fade-in…)
```

### Añadir un nuevo componente SCSS

1. Crear `frontend/src/styles/components/_nombre.scss`
2. Añadir `@import 'nombre';` en `frontend/src/styles/components/_index.scss`
3. El componente queda disponible tanto en Angular como en 11ty sin ningún paso adicional.

## Componentes Angular

Los componentes son **standalone** (Angular 21). Los estilos del componente (`.scss`) se mantienen **vacíos** de forma intencionada — todos los estilos son globales.

```
frontend/src/app/components/
├── header/   # header.ts | header.html | header.scss (vacío)
└── footer/   # footer.ts | footer.html | footer.scss (vacío)
```

## Plantillas Nunjucks (11ty)

```
web/src/
├── _includes/
│   ├── layouts/base.njk      # Layout HTML completo
│   └── partials/
│       ├── header.njk        # BEM idéntico a header.html de Angular
│       └── footer.njk        # BEM idéntico a footer.html de Angular
├── _data/site.js             # Datos globales: nombre, año, urls
├── index.njk                 # Landing page
├── producto/                 # /producto/funcionalidades, /precios…
├── legal/                    # /legal/privacidad, /terminos, /cookies
└── empresa/                  # /empresa/sobre-nosotros, /contacto…
```

El layout base carga el CSS compilado desde `/assets/styles/main.css`.

## Backend Flask

Ver [docs/backend/VENV_SETUP.md](backend/VENV_SETUP.md) para la configuración del entorno virtual y [docs/backend/DEPENDENCIAS.md](backend/DEPENDENCIAS.md) para el detalle de librerías.

```bash
cd backend
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env   # rellenar variables
python run.py
```

## Ramas activas

| Rama | Propósito |
|------|-----------|
| `main` | Código estable, infraestructura y documentación |
| `dev-componentes-11ty-angular` | Componentes Angular (header, footer, estilos ITCSS) |
| `dev-componentes-11ty-njk` | Sitio estático 11ty con Nunjucks |
