# Contribuir a Stay Sidekick

## Objetivo de esta guia

Esta guia resume como preparar el entorno, que comprobaciones ejecutar y que convenciones seguir antes de proponer cambios en Stay Sidekick. Esta pensada para contribuciones pequenas, trazables y faciles de revisar.

## Requisitos previos reales del proyecto

- Node.js 18 o superior
- pnpm 10 o superior (se activa automaticamente vía `corepack enable`)
- Python 3.12
- Docker y Docker Compose v2 si quieres validar el stack completo
- PostgreSQL solo es necesario si no trabajas con Docker Compose

Antes de tocar codigo o documentacion, revisa tambien [README.md](README.md), [DEPLOY.md](DEPLOY.md) y [docs/backend/VENV_SETUP.md](docs/backend/VENV_SETUP.md).

## Arranque local rapido

### Frontend Angular + sitio web 11ty

Desde la raiz del repositorio:

```bash
pnpm install
pnpm run install:all
pnpm run dev
```

Atajos disponibles desde la raiz:

```bash
pnpm run dev:web
pnpm run dev:app
```

## Backend Flask

Prepara las variables de entorno de la raiz y del backend a partir de sus ejemplos y crea el entorno virtual en `backend/.venv`.

```bash
python -m venv backend/.venv
backend/.venv/Scripts/Activate.ps1
pip install -r backend/requirements.txt pytest
cd backend
python run.py
```

Si trabajas en otro shell o sistema operativo, usa el equivalente documentado en [docs/backend/VENV_SETUP.md](docs/backend/VENV_SETUP.md).

## Stack completo con Docker

Para validar el comportamiento integrado de nginx, frontend, web, backend y PostgreSQL:

```bash
docker compose up -d --build
docker compose ps
```

Los comandos operativos de apoyo estan descritos en [docs/devops/docker-local.md](docs/devops/docker-local.md).

## Checks conocidos antes de proponer cambios

Ejecuta solo lo que afecte a tu cambio, pero no abras una propuesta sin comprobar al menos la parte tocada.

### Backend

```bash
ruff check backend/app
pytest backend/tests/ -v
```

### Frontend Angular

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm run build
pnpm exec ng test --watch=false
```

### Sitio web 11ty

```bash
cd web
pnpm install --frozen-lockfile
pnpm run build
```

## Convenciones de ramas y commits

- crea una rama antes de editar
- usa `dev-*` para trabajo normal, `fix-*` para correcciones y `hotfix-*` para incidencias urgentes
- manten commits atomicos y en español
- no uses scope en el mensaje de commit
- si haces un merge manual, sigue el formato `merge: rama-origen -> rama-destino; descripcion`

## Como plantear cambios buenos de revisar

- limita cada rama a un objetivo claro
- evita refactors incidentales si no son necesarios para resolver el problema
- si cambias rutas, comandos, variables o comportamiento visible, actualiza la documentacion afectada en la misma iteracion
- explica en la propuesta que has cambiado, como lo has validado y que queda fuera de alcance

## Secretos, binarios y artefactos generados

- no subas `.env`, credenciales, JWT reales, cookies, exports de proveedores ni datos personales
- no anadas logs, coberturas, caches, entornos virtuales o artefactos de build salvo que el repositorio ya los gestione de forma explicita
- no conviertas credenciales de desarrollo o seed local en valores de produccion

## Cambios en automatizacion o governance aun no aprobados

Si una propuesta afecta a plantillas de GitHub, automatizaciones de comunidad o flujos que todavia no se quieren activar de forma definitiva, deja el material como borrador local o nota de trabajo y no lo conviertas en cambio final dentro de `.github/` sin aprobacion expresa.

## Regla practica para esta base de codigo

En este repositorio suele ser mejor una contribucion pequena, comprobable y bien documentada que una correccion amplia con varias decisiones mezcladas. Si tienes dudas, reduce alcance antes de abrir mas frentes.