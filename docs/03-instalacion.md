# 03-instalacion

## Indice

- [3.1. Objetivo del capitulo](#31-objetivo-del-capitulo)
- [3.2. Requisitos previos](#32-requisitos-previos)
  - [Requisitos de software (local)](#requisitos-de-software-local)
  - [Versiones y runtimes usados en Docker](#versiones-y-runtimes-usados-en-docker)
  - [Puertos usados](#puertos-usados)
- [3.3. Estructura de despliegue y scripts existentes](#33-estructura-de-despliegue-y-scripts-existentes)
  - [Dockerfiles del proyecto](#dockerfiles-del-proyecto)
  - [Scripts de instalacion y arranque](#scripts-de-instalacion-y-arranque)
- [3.4. Variables de entorno necesarias](#34-variables-de-entorno-necesarias)
  - [Archivos de entorno](#archivos-de-entorno)
  - [Variables raiz (.env)](#variables-raiz-env)
  - [Variables backend (backend/.env)](#variables-backend-backendenv)
  - [Variables web (web/.env)](#variables-web-webenv)
- [3.5. Instalacion y arranque con Docker (recomendado)](#35-instalacion-y-arranque-con-docker-recomendado)
  - [Paso 1. Preparar entorno](#paso-1-preparar-entorno)
  - [Paso 2. Construir y levantar servicios](#paso-2-construir-y-levantar-servicios)
  - [Paso 3. Verificacion funcional](#paso-3-verificacion-funcional)
  - [Credenciales de acceso seed local](#credenciales-de-acceso-seed-local)
- [3.6. Instalacion y arranque sin Docker (modo desarrollo)](#36-instalacion-y-arranque-sin-docker-modo-desarrollo)
  - [Paso 1. Instalar dependencias Node en raiz, web y frontend](#paso-1-instalar-dependencias-node-en-raiz-web-y-frontend)
  - [Paso 2. Preparar backend Python](#paso-2-preparar-backend-python)
  - [Paso 3. Levantar web y frontend](#paso-3-levantar-web-y-frontend)
  - [Paso 4. Levantar backend](#paso-4-levantar-backend)
- [3.7. Comandos utiles de operacion](#37-comandos-utiles-de-operacion)
- [3.8. Errores frecuentes y solucion](#38-errores-frecuentes-y-solucion)

## 3.1. Objetivo del capitulo

Este capitulo define el procedimiento de instalacion y preparacion del entorno de Stay Sidekick con un enfoque reproducible y verificable. Se documentan los requisitos previos, las versiones reales usadas por el proyecto, los scripts de arranque, la arquitectura de contenedores y las variables de entorno necesarias para ejecucion local y despliegue.

## 3.2. Requisitos previos

### Requisitos de software (local)

Para desarrollo local sin contenedores:

- Node.js >= 18 (recomendado: 20 LTS).
- npm >= 10.
- Python 3.12.
- pip para Python 3.
- Git para clonar el repositorio.

Para ejecucion con contenedores (modo recomendado):

- Docker 24 o superior.
- Docker Compose v2 (plugin de Docker).

### Versiones y runtimes usados en Docker

Las imagenes declaradas en los Dockerfiles y compose del proyecto son:

- Backend: `python:3.12-slim`.
- Frontend build: `node:20-alpine`.
- Web build (11ty): `node:20-alpine`.
- Frontend serve: `nginx:alpine`.
- Web serve: `nginx:alpine`.
- Reverse proxy principal: `nginx:alpine`.
- Base de datos: `postgres:16-alpine`.

### Puertos usados

- `80`: entrada publica local via Nginx (Docker Compose).
- `4200`: Angular en desarrollo local sin Docker.
- `8080`: 11ty en desarrollo local sin Docker.
- `5000`: API Flask.
- `5432`: PostgreSQL interno de contenedores.

## 3.3. Estructura de despliegue y scripts existentes

### Dockerfiles del proyecto

| Archivo | Rol | Detalle clave |
|---|---|---|
| `backend/Dockerfile` | API Flask + Gunicorn | Aplica `flask db upgrade` y arranca Gunicorn en `PORT` |
| `frontend/Dockerfile` | Build Angular + servido Nginx | Build con `--base-href=/menu/` |
| `web/Dockerfile` | Build 11ty + servido Nginx | Requiere contexto de build en raiz para SCSS compartido |
| `nginx/Dockerfile` | Reverse proxy | Usa config distinta para local y Railway via `RAILWAY=true/false` |

Este diseno permite separar build y runtime en frontend/web (multi-stage), y mantener un backend con migraciones automaticas en arranque.

### Scripts de instalacion y arranque

| Archivo/Script | Uso |
|---|---|
| `dev.sh` | Arranca web + frontend en Linux/macOS e instala dependencias faltantes |
| `dev.bat` | Arranca web + frontend en Windows e instala dependencias faltantes |
| `npm run dev` (raiz) | Ejecuta `web` y `frontend` en paralelo con `concurrently` |
| `npm run dev:web` (raiz) | Levanta 11ty |
| `npm run dev:app` (raiz) | Levanta Angular |
| `npm run install:all` (raiz) | Instala dependencias de `frontend` y `web` |
| `docker compose up -d --build` | Construye y levanta stack completo |

## 3.4. Variables de entorno necesarias

### Archivos de entorno

El proyecto utiliza tres niveles de configuracion:

- `.env` (raiz): variables de PostgreSQL y `DATABASE_URL` para Compose.
- `backend/.env`: configuracion de Flask, JWT, integraciones y seguridad.
- `web/.env`: `TURNSTILE_SITE_KEY` publica para 11ty.

Archivo adicional de desarrollo:

- `backend/.env.dev`: entorno de pruebas con valores no sensibles para `docker-compose.dev.yml`.

### Variables raiz (.env)

Copiar desde `.env.example`.

| Variable | Obligatoria | Descripcion |
|---|---|---|
| `POSTGRES_DB` | Si | Nombre de base de datos |
| `POSTGRES_USER` | Si | Usuario de PostgreSQL |
| `POSTGRES_PASSWORD` | Si | Password de PostgreSQL |
| `DATABASE_URL` | Si | URL completa de conexion a PostgreSQL |
| `TURNSTILE_SITE_KEY` | Recomendado | Site key publica para build de `web` |

### Variables backend (backend/.env)

Copiar desde `backend/.env.example`.

| Variable | Obligatoria | Descripcion |
|---|---|---|
| `FLASK_ENV` | Si | Entorno (`development` o `production`) |
| `SECRET_KEY` | Si | Clave de Flask |
| `PORT` | No | Puerto de escucha (Docker usa `5000`) |
| `ALLOWED_ORIGINS` | Si | Origenes CORS separados por coma |
| `TURNSTILE_SECRET_KEY` | Si en formularios publicos | Secret de Cloudflare Turnstile |
| `TURNSTILE_VERIFY_URL` | No | Endpoint de verificacion Turnstile |
| `GOOGLE_CLIENT_ID` | Opcional | OAuth Google Contacts |
| `GOOGLE_CLIENT_SECRET` | Opcional | OAuth Google Contacts |
| `GOOGLE_REDIRECT_URI` | Opcional | Callback OAuth |
| `FRONTEND_BASE_URL` | Si | URL base para redirects post OAuth |
| `GMAIL_USER` | Opcional | Cuenta de envio SMTP |
| `GMAIL_APP_PASSWORD` | Opcional | Password de aplicacion Gmail |
| `MAIL_RECIPIENT` | Opcional | Destinatario de formularios |
| `DISCORD_WEBHOOK_URL` | Opcional | Webhook de solicitudes |
| `DISCORD_WEBHOOK_CONTACT_URL` | Opcional | Webhook de contacto general |
| `RATE_LIMIT_CONTACT` | No | Limite de peticiones formulario |
| `JWT_SECRET_KEY` | Si | Firma de tokens JWT |
| `JWT_ACCESS_TOKEN_HOURS` | No | Duracion del token |
| `FERNET_KEY` | Si | Cifrado de API keys en BD |
| `AI_DEFAULT_PROVIDER` | No | Proveedor IA por defecto |
| `AI_DEFAULT_MODEL` | No | Modelo IA por defecto |
| `AI_DEFAULT_API_KEY` | Opcional | API key global del sistema |
| `AI_FREE_LIMIT_DAILY` | No | Limite diario free tier |
| `AI_FREE_LIMIT_WEEKLY` | No | Limite semanal free tier |
| `AI_PROMPT_ADMIN_IPS` | No | IPs permitidas para prompts admin |
| `DATABASE_URL` | Si | Conexion a PostgreSQL |
| `SMOOBU_API_KEY` | Opcional | Integracion PMS Smoobu |

Nota: `MAX_UPLOAD_BYTES` no aparece en `backend/.env.example`, pero el codigo lo soporta con valor por defecto de 10 MB.

### Matriz de variables obligatorias por entorno

La siguiente tabla resume que variables son imprescindibles segun el entorno de ejecucion.

| Variable | Docker local minimo | Desarrollo sin Docker | Produccion |
|---|:---:|:---:|:---:|
| `POSTGRES_DB` | Si | No | No |
| `POSTGRES_USER` | Si | No | No |
| `POSTGRES_PASSWORD` | Si | No | No |
| `DATABASE_URL` (raiz) | Si | No | No |
| `DATABASE_URL` (backend) | No (inyectada por compose) | Si | Si |
| `SECRET_KEY` | Si | Si | Si |
| `JWT_SECRET_KEY` | Si | Si | Si |
| `FERNET_KEY` | Si | Si | Si |
| `ALLOWED_ORIGINS` | No (compose la fuerza) | Si | Si |
| `FRONTEND_BASE_URL` | Si | Si | Si |
| `TURNSTILE_SITE_KEY` | Recomendado | Recomendado | Si |
| `TURNSTILE_SECRET_KEY` | Si si se usa formulario publico | Si si se usa formulario publico | Si |
| `GOOGLE_CLIENT_ID` | Opcional | Opcional | Opcional |
| `GOOGLE_CLIENT_SECRET` | Opcional | Opcional | Opcional |
| `GOOGLE_REDIRECT_URI` | Opcional | Opcional | Opcional |
| `GMAIL_USER` | Opcional | Opcional | Opcional |
| `GMAIL_APP_PASSWORD` | Opcional | Opcional | Opcional |
| `MAIL_RECIPIENT` | Opcional | Opcional | Opcional |
| `DISCORD_WEBHOOK_URL` | Opcional | Opcional | Opcional |
| `DISCORD_WEBHOOK_CONTACT_URL` | Opcional | Opcional | Opcional |
| `SMOOBU_API_KEY` | Opcional | Opcional | Opcional |

### Variables web (web/.env)

Copiar desde `web/.env.example`.

| Variable | Obligatoria | Descripcion |
|---|---|---|
| `TURNSTILE_SITE_KEY` | Si | Site key publica usada en formularios del sitio 11ty |

## 3.5. Instalacion y arranque con Docker (recomendado)

### Paso 1. Preparar entorno

1. Clonar repositorio.
2. Crear archivos `.env` requeridos.

Linux/macOS:

```bash
git clone https://github.com/sdurutr436/stay-sidekick.git
cd stay-sidekick
cp .env.example .env
cp backend/.env.example backend/.env
cp web/.env.example web/.env
```

Windows PowerShell:

```powershell
git clone https://github.com/sdurutr436/stay-sidekick.git
cd stay-sidekick
Copy-Item .env.example .env
Copy-Item backend/.env.example backend/.env
Copy-Item web/.env.example web/.env
```

### Paso 2. Construir y levantar servicios

```bash
docker compose up -d --build
```

Para entorno de desarrollo con overrides seguros:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

El override de desarrollo usa `backend/.env.dev` para permitir pruebas funcionales sin secretos reales.

### Paso 3. Verificacion funcional

```bash
docker compose ps
curl -s http://localhost/api/health
```

Resultado esperado en health:

```json
{"status":"ok"}
```

Comprobacion adicional recomendada:

```bash
docker compose logs --tail=30 backend
```

La salida debe mostrar la aplicacion de migraciones y el arranque de Gunicorn sin errores.

URLs de acceso:

- `http://localhost/` -> sitio 11ty.
- `http://localhost/menu/` -> app Angular.
- `http://localhost/api/` -> API Flask.

### Credenciales de acceso seed local

El seed cargado en `backend/seed.sql` crea usuario de desarrollo:

- Email: `dev@staysidekick.es`
- Password: `admin123`
- Rol: `admin` (con `es_superadmin=true`)

Si la base ya existia sin seed, reiniciar volumen:

```bash
docker compose down -v
docker compose up -d --build
```

## 3.6. Instalacion y arranque sin Docker (modo desarrollo)

### Paso 1. Instalar dependencias Node en raiz, web y frontend

En la raiz del proyecto:

```bash
npm install
npm run install:all
```

### Paso 2. Preparar backend Python

Desde `backend/`:

Linux/macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Paso 3. Levantar web y frontend

Opcion A (script automatico):

- Linux/macOS: `./dev.sh`
- Windows: `dev.bat`

Opcion B (comando npm):

```bash
npm run dev
```

### Paso 4. Levantar backend

Con el entorno Python activo, desde `backend/`:

```bash
python run.py
```

Nota: en modo sin Docker es necesario disponer de PostgreSQL accesible en el `DATABASE_URL` configurado.

Para validar rapidamente el backend en este modo:

```bash
curl -s http://localhost:5000/api/health
```

## 3.7. Comandos utiles de operacion

```bash
docker compose logs -f
docker compose logs -f backend
docker compose restart backend
docker compose stop
docker compose down
```

Para limpiar completamente base local:

```bash
docker compose down -v
```

## 3.8. Errores frecuentes y solucion

- `backend/.env not found`:
  crear `backend/.env` desde `backend/.env.example`.
- `DATABASE_URL variable is not set`:
  revisar `.env` de raiz.
- `KeyError: SECRET_KEY`:
  definir `SECRET_KEY` en `backend/.env`.
- `Port 80 already in use`:
  liberar puerto o cambiar mapeo en `docker-compose.yml`.
- `No se cargan tablas iniciales`:
  reconstruir volumen con `docker compose down -v` y volver a levantar.
