# ADR: Separación de `/web` y `/frontend` como proyectos independientes

**Estado:** Aceptado
**Fecha:** 2026-04-01
**Contexto:** Se evaluó si era factible mover el directorio `/web` (11ty) dentro de `/frontend` (Angular) para unificar todo el código de presentación bajo una sola raíz.

---

## Contexto y problema

El proyecto tiene dos capas de presentación con naturalezas distintas:

| Directorio | Tecnología | Tipo | Propósito |
|------------|-----------|------|-----------|
| `/frontend` | Angular 21 | SPA (client-side) | App dinámica: panel de usuario, formularios, rutas protegidas |
| `/web` | 11ty + Nunjucks | SSG (static) | Sitio público: landing, legales, empresa, producto |

Ambos comparten la misma base de estilos SCSS (viven en `frontend/src/styles/`) y producen HTML/CSS con las mismas clases BEM, dando continuidad visual al usuario.

La pregunta es: ¿debe `/web` vivir dentro de `/frontend`?

---

## Opciones consideradas

### Opción A — Mantener `/web` y `/frontend` separados (decisión adoptada)

```
tfg-alberti/
├── frontend/   # Angular SPA
├── web/        # 11ty SSG
└── backend/    # Flask API
```

### Opción B — Anidar `/web` dentro de `/frontend`

```
tfg-alberti/
├── frontend/
│   ├── src/        # Angular
│   └── web/        # 11ty dentro de Angular
└── backend/
```

---

## Decisión: Opción A

Se mantienen `/web` y `/frontend` como proyectos independientes al mismo nivel.

---

## Justificación

### 1. Docker — build context contaminado

Con la Opción B, el contexto de build de Angular (`COPY frontend/ .`) incluiría los `node_modules` de 11ty, el directorio `_site/` de output y las plantillas Nunjucks. Esto obliga a un `.dockerignore` complejo y frágil. Cualquier cambio en 11ty invalida la capa de caché del Dockerfile de Angular.

Con la Opción A, cada Dockerfile copia solo su propio directorio:

```dockerfile
# Angular
COPY frontend/ .

# 11ty
COPY web/ .
```

Contextos mínimos, capas de caché independientes.

### 2. Railway — rootDirectory no estándar

Railway identifica los servicios por `rootDirectory`. Con la Opción B:

- Angular → `rootDirectory: frontend` ✓
- 11ty   → `rootDirectory: frontend/web` ✗ (confuso, subrutas no son estándar en Railway)

Railway espera que cada servicio deployable sea una raíz de proyecto. Una ruta `frontend/web` viola esta convención y puede causar problemas con la auto-detección de Nixpacks, que intentaría reconocer si `frontend/web` es un proyecto Angular (por proximidad al `angular.json` del padre).

Con la Opción A:

- Angular → `rootDirectory: frontend` ✓
- 11ty   → `rootDirectory: web` ✓

Configuración limpia, un servicio por directorio raíz.

### 3. Confusión semántica

`frontend/web` es un nombre contradictorio. "La parte web del frontend" no significa nada concreto. La distinción correcta es:

- `/frontend` = **app** (SPA, requiere JS, rutas cliente, autenticación)
- `/web` = **sitio** (SSG, HTML puro, indexable por buscadores, sin JS necesario)

Son conceptualmente paralelos, no jerárquicos. Anidar uno dentro del otro distorsiona el modelo mental del proyecto.

### 4. Angular CLI no debe conocer 11ty

`angular.json` asume que su directorio raíz contiene solo el proyecto Angular. Los comandos `ng build`, `ng lint`, `ng test` y el servidor de desarrollo operan desde `frontend/`. Tener un subdirectorio con otro sistema de build (`package.json`, `node_modules`, `_site/`) dentro del workspace Angular introduce ruido en el árbol de ficheros y puede interferir con herramientas que hacen glob sobre la carpeta del proyecto.

### 5. El SCSS compartido ya funciona sin unificación

La Opción A consigue compartir los estilos mediante el argumento `--load-path` de Sass:

```bash
# web/package.json
sass src/assets/styles/main.scss:_site/assets/styles/main.css \
  --load-path=../frontend/src/styles
```

Ambos proyectos compilan desde exactamente los mismos archivos fuente. No es necesario colocarlos en el mismo árbol de directorios para compartirlos.

---

## Consecuencias

### Para el desarrollo local

- Se mantiene el orquestador raíz (`package.json` + `dev.sh` / `dev.bat`) que levanta ambos con `concurrently`.
- El desarrollador trabaja con dos servidores en paralelo: `:8080` (11ty) y `:4200` (Angular).

### Para Docker

Cada servicio tiene su propio `Dockerfile` mínimo:

```
tfg-alberti/
├── frontend/Dockerfile   # node:alpine → build Angular → nginx
├── web/Dockerfile        # node:alpine → build 11ty → nginx/serve
└── backend/Dockerfile    # python:slim → gunicorn
```

Un `docker-compose.yml` en la raíz puede orquestarlos todos.

### Para Railway

Cada servicio se despliega de forma independiente:

| Servicio | `rootDirectory` | Build command | Deploy |
|----------|----------------|---------------|--------|
| Angular  | `frontend`     | `npm run build` | Static / Node |
| 11ty     | `web`          | `npm run build` | Static |
| Flask    | `backend`      | — | Python |

### Alternativa futura: npm workspaces

Si en el futuro se quisiera una gestión de dependencias unificada, se podría migrar a **npm workspaces** desde la raíz, convirtiendo `frontend/` y `web/` en paquetes del workspace. Esto permitiría `npm install` una sola vez en raíz. Esta refactorización no cambia la estructura de directorios ni afecta a Docker/Railway.
