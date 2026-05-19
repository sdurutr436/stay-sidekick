<div align="center">

  # Stay Sidekick

  <img src="web/src/assets/img/favicon/stay-sidekick-fav-icon-600x600.webp" alt="Stay-sidekick" width="180"/>

  ## La capa satélite para la gestión operacional en tu empresa vacacional

  > **Accede directamente:** [https://stay-sidekick.com](https://stay-sidekick.com)

</div>

---

<div align="center">

[![CI Python](https://github.com/sdurutr436/stay-sidekick/actions/workflows/ci-python.yml/badge.svg)](https://github.com/sdurutr436/stay-sidekick/actions/workflows/ci-python.yml)
[![CI Angular](https://github.com/sdurutr436/stay-sidekick/actions/workflows/ci-angular.yml/badge.svg)](https://github.com/sdurutr436/stay-sidekick/actions/workflows/ci-angular.yml)
[![Tests Angular](https://github.com/sdurutr436/stay-sidekick/actions/workflows/ci-angular-tests.yml/badge.svg)](https://github.com/sdurutr436/stay-sidekick/actions/workflows/ci-angular-tests.yml)
[![CI 11ty](https://github.com/sdurutr436/stay-sidekick/actions/workflows/ci-web.yml/badge.svg)](https://github.com/sdurutr436/stay-sidekick/actions/workflows/ci-web.yml)

</div>

---

Stay Sidekick es una plataforma web para equipos de alojamiento turístico que agrupa, en un mismo stack, una landing pública, un panel de trabajo privado y una API REST para operaciones como gestión de solicitudes, herramientas multiempresa, sincronización de contactos y automatizaciones de apoyo.

- Producción pública: [stay-sidekick.up.railway.app](https://stay-sidekick.up.railway.app)
- Imágenes publicadas: [Docker Hub - sdurutr436](https://hub.docker.com/u/sdurutr436)

## Qué incluye

- `web/`: sitio estático con contenido público, legal y corporativo.
- `frontend/`: SPA Angular para el panel operativo.
- `backend/`: API REST Flask para autenticación, negocio y notificaciones.
- `nginx/`: proxy inverso que publica `/`, `/menu/` y `/api/` en una única entrada.

## Arquitectura

El proyecto está dividido en tres capas independientes:

## Stack técnico

| Área | Stack real del repositorio |
|------|-----------------------------|
| Sitio público | ![11ty](https://img.shields.io/badge/-11ty-000000?style=flat-square&logo=eleventy&logoColor=white) ![Nunjucks](https://img.shields.io/badge/-Nunjucks-1C6D28?style=flat-square&logo=nunjucks&logoColor=white) ![Sass](https://img.shields.io/badge/-Sass-CC6699?style=flat-square&logo=sass&logoColor=white) |
| Aplicación | ![Angular](https://img.shields.io/badge/-Angular%2021-DD0031?style=flat-square&logo=angular&logoColor=white) |
| Backend | ![Flask](https://img.shields.io/badge/-Flask-000000?style=flat-square&logo=flask&logoColor=white) ![Gunicorn](https://img.shields.io/badge/-Gunicorn-499848?style=flat-square) ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) |
| Infraestructura | ![Docker Compose](https://img.shields.io/badge/-Docker%20Compose-2496ED?style=flat-square&logo=docker&logoColor=white) ![Railway](https://img.shields.io/badge/-Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white) ![Nginx](https://img.shields.io/badge/-Nginx-009639?style=flat-square&logo=nginx&logoColor=white) |
| Calidad | ![GitHub Actions](https://img.shields.io/badge/-GitHub%20Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white) ![Ruff](https://img.shields.io/badge/-Ruff-D7FF64?style=flat-square) ![Pytest](https://img.shields.io/badge/-Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white) ![Angular Build](https://img.shields.io/badge/-Angular%20Build-DD0031?style=flat-square&logo=angular&logoColor=white) ![Angular Tests](https://img.shields.io/badge/-Angular%20Tests-C21325?style=flat-square&logo=angular&logoColor=white) |

Los estilos SCSS son **compartidos** entre `web/` y `frontend/`: ambos compilan desde `frontend/src/styles/` siguiendo la arquitectura [ITCSS](https://www.xfive.co/blog/itcss-scalable-maintainable-css-architecture/) con nomenclatura [BEM](https://getbem.com/).

### Arquitectura Docker

```mermaid
graph TD
    Cliente(["Cliente HTTP"])

    subgraph app-net["app-net (red interna Docker)"]
        Nginx["nginx · Nginx:alpine · :80"]
        Frontend["frontend · Angular+Nginx · :80"]
        Web["web · 11ty+Nginx · :80"]
        Backend["backend · Flask+Gunicorn · :5000"]
        Postgres[("postgres · PostgreSQL 16 · :5432")]
    end

    Cliente -->|"HTTP :80 — único puerto expuesto al host"| Nginx
    Nginx -->|"/api/*"| Backend
    Nginx -->|"/menu/*"| Frontend
    Nginx -->|"/*"| Web
    Backend -->|"SQL :5432"| Postgres
```

Una petición autenticada recorre el siguiente camino: el cliente envía la solicitud HTTP al puerto 80 del host, donde **nginx** actúa como proxy inverso y la enruta según el prefijo — `/api/*` se redirige al **backend** Flask (Gunicorn en puerto 5000), que consulta **PostgreSQL** (puerto 5432) y devuelve una respuesta JSON. nginx reenvía esa respuesta al cliente. El resto de rutas sirven la SPA Angular (`/menu/*`) o el sitio estático 11ty (`/*`). Todo el tráfico entre servicios circula por la red interna `app-net`; el único puerto expuesto al host es el 80.

## Inicio rápido

### Prerrequisitos

- `Node.js` 18 o superior
- `npm` 10 o superior
- `Python` 3.12 o superior
- `Docker` version 24 o más, para levantar el stack completo

### Levantar frontend + sitio estático (una sola orden)

**Linux / macOS:**
```bash
chmod +x dev.sh
./dev.sh
```

**Windows:**
```bat
dev.bat
```

Alternativa directa con npm:

```bash
npm install
npm run dev
```

Esto levanta en paralelo:
- **http://localhost:8080** — Sitio estático (11ty)
- **http://localhost:4200** — App Angular

### Arranque por servicio
```bash
# Sitio estático
npm run dev:web        # cd web && npm start

# App Angular
npm run dev:app        # cd frontend && npm start

# Backend Flask (ver docs/backend/VENV_SETUP.md)
cd backend && python run.py
```

### Instalar todas las dependencias Node de una vez

```bash
npm run install:all
```

### Levantar con Docker (entorno completo)

Docker levanta todos los servicios juntos (nginx, frontend, web, backend, PostgreSQL) en
un único comando. Es la forma más fácil de probar el stack completo en local.

**Primer uso** -> preparar los `.env`:
```bash
cp .env.example .env                   # variables de PostgreSQL y Turnstile
cp backend/.env.example backend/.env   # completar con tus valores
# web/.env ya está incluido con la key de prueba de Turnstile (dev)
```

**Levantar:**
```bash
docker compose up --build        # construye imágenes y arranca (foreground)
docker compose up -d --build     # igual pero en background
```

> Primera vez: si el volumen ya existía sin el seed, borrar y recrear:
> ```bash
> docker compose down -v && docker compose up -d --build
> ```

**Comandos útiles:**
```bash
docker compose ps                # ver qué contenedores están corriendo
docker compose logs -f           # seguir logs de todos los servicios
docker compose logs -f backend   # logs solo del backend
docker compose restart backend   # reiniciar un único servicio
docker compose stop              # parar todos los contenedores (conserva datos)
docker compose down              # parar y eliminar contenedores (conserva volúmenes)
docker compose down -v           # parar, eliminar contenedores Y la base de datos
```

**URLs tras levantar:**

| URL | Servicio |
|-----|---------|
| http://localhost/ | Sitio estático (11ty) |
| http://localhost/menu/ | App Angular |
| http://localhost/api/ | API Flask |

**Credenciales de acceso (creadas por el seed de desarrollo):**

| Campo | Valor |
|-------|-------|
| Email | `dev@staysidekick.es` |
| Contraseña | `admin123` |
| Rol | `admin` (con `es_superadmin=true`) |

> Estas credenciales son solo para entorno local. En producción, generar credenciales nuevas.

## Estructura del proyecto

```
tfg-alberti/
├── web/                    # Sitio estático — 11ty + Nunjucks
│   ├── src/
│   │   ├── _includes/      # Layouts y partials Nunjucks
│   │   ├── _data/          # Datos globales del sitio
│   │   ├── assets/styles/  # SCSS entry (compila desde frontend/src/styles/)
│   │   ├── producto/       # Páginas de producto
│   │   ├── legal/          # Páginas legales
│   │   └── empresa/        # Páginas de empresa
│   └── eleventy.config.js
│
├── frontend/               # App Angular (SPA)
│   └── src/
│       ├── app/
│       │   └── components/ # Componentes standalone (header, footer…)
│       └── styles/         # SCSS compartido con web/ (ITCSS)
│           ├── settings/   # Variables: tipografía, colores, breakpoints
│           ├── tools/      # Mixins reutilizables
│           ├── generic/    # Resets CSS
│           ├── elements/   # Estilos base de elementos HTML
│           ├── layout/     # Grid, flex, contenedor
│           ├── components/ # Átomos y organismos BEM
│           ├── utilities/  # Clases de utilidad
│           └── animations/ # Keyframes y transiciones
│
├── backend/                # API REST Flask
│   └── app/
│       ├── contact/        # Módulo de formulario de contacto
│       ├── security/       # CSRF, honeypot, JWT
│       └── services/       # Gmail, Discord, Turnstile
│
├── docs/                   # Documentación del proyecto
├── package.json            # Orquestador de desarrollo (concurrently)
├── dev.sh                  # Inicio rápido Linux / macOS
└── dev.bat                 # Inicio rápido Windows
```

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [DEPLOY.md](DEPLOY.md) | Despliegue local y producción en Railway |
| [docs/01-introduccion.md](docs/01-introduccion.md) a [docs/10-conclusiones.md](docs/10-conclusiones.md) | Memoria técnica principal del proyecto |
| [docs/DESARROLLO.md](docs/DESARROLLO.md) | Guía de entorno y flujo de trabajo |
| [docs/backend/DEPENDENCIAS.md](docs/backend/DEPENDENCIAS.md) | Dependencias del backend y justificación |
| [docs/backend/VENV_SETUP.md](docs/backend/VENV_SETUP.md) | Entorno virtual Python |
| [docs/design/decisiones_disenio.md](docs/design/decisiones_disenio.md) | Decisiones de diseño y arquitectura |
| [docs/propuesta_formal/propuesta_formal_sergio_duran_2DAW.md](docs/propuesta_formal/propuesta_formal_sergio_duran_2DAW.md) | Propuesta formal del proyecto |

## Colaboración y mantenimiento

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)
- [LICENSE](LICENSE)