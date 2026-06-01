# 3. Instalacion

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
  - [Preparacion de entorno y arranque](#preparacion-de-entorno-y-arranque)
  - [Variables de entorno](#variables-de-entorno)
  - [Puertos y red](#puertos-y-red)
  - [Base de datos y migraciones](#base-de-datos-y-migraciones)
  - [Notificaciones (email y Discord)](#notificaciones-email-y-discord)
  - [Frontend y sitio publico](#frontend-y-sitio-publico)

## 3.1. Objetivo del capitulo

Este capitulo define el procedimiento de instalacion y preparacion del entorno de Stay Sidekick con un enfoque reproducible y verificable. Se documentan los requisitos previos, las versiones reales usadas por el proyecto, los scripts de arranque, la arquitectura de contenedores y las variables de entorno necesarias para ejecucion local y despliegue.

## 3.2. Requisitos previos

### Requisitos de software (local)

Para desarrollo local sin contenedores:

- Node.js >= 18 (recomendado: 20 LTS).
- pnpm >= 10 (se activa con `corepack enable`).
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

Este diseño permite separar build y runtime en frontend/web (multi-stage), y mantener un backend con migraciones automaticas en arranque.

### Scripts de instalacion y arranque

| Archivo/Script | Uso |
|---|---|
| `dev.sh` | Arranca web + frontend en Linux/macOS e instala dependencias faltantes |
| `dev.bat` | Arranca web + frontend en Windows e instala dependencias faltantes |
| `pnpm run dev` (raiz) | Ejecuta `web` y `frontend` en paralelo con `concurrently` |
| `pnpm run dev:web` (raiz) | Levanta 11ty |
| `pnpm run dev:app` (raiz) | Levanta Angular |
| `pnpm run install:all` (raiz) | Instala dependencias de `frontend` y `web` |
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
| `MAIL_GUN_API_KEY` | Opcional | Clave privada de la cuenta de Mailgun (envio HTTP) |
| `MAIL_GUN_DOMAIN` | Opcional | Dominio verificado en Mailgun (ej. `stay-sidekick.com`) |
| `MAIL_GUN_API_URL` | No | Base de la API de Mailgun (`https://api.eu.mailgun.net` o `https://api.mailgun.net`) |
| `MAIL_FROM` | Opcional | Direccion visible en el `From:` y destino de notificaciones publicas. Si esta vacia se usa `noreply@<MAIL_GUN_DOMAIN>` |
| `DISCORD_WEBHOOK_URL` | Opcional | Webhook de solicitudes de empresa |
| `DISCORD_WEBHOOK_CONTACT_URL` | Opcional | Webhook de contacto general |
| `DISCORD_WEBHOOK_OPERATIONS_URL` | Opcional | Webhook de operacion/errores del backend |
| `DISCORD_WEBHOOK_AI_OBSERVABILITY_URL` | Opcional | Canal especifico de observabilidad IA (si vacio, cae al de operacion) |
| `RATE_LIMIT_CONTACT` | No | Limite de peticiones formulario |
| `RATE_LIMIT_STORAGE_URI` | No | Backend de Flask-Limiter (por defecto `memory://`) |
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
| `MAIL_GUN_API_KEY` | Opcional | Opcional | Opcional |
| `MAIL_GUN_DOMAIN` | Opcional | Opcional | Opcional |
| `MAIL_GUN_API_URL` | Opcional | Opcional | Opcional |
| `MAIL_FROM` | Opcional | Opcional | Opcional |
| `DISCORD_WEBHOOK_URL` | Opcional | Opcional | Opcional |
| `DISCORD_WEBHOOK_CONTACT_URL` | Opcional | Opcional | Opcional |
| `DISCORD_WEBHOOK_OPERATIONS_URL` | Opcional | Opcional | Opcional |
| `DISCORD_WEBHOOK_AI_OBSERVABILITY_URL` | Opcional | Opcional | Opcional |
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
corepack enable
pnpm install
pnpm run install:all
```

#### Scripts de postinstalacion permitidos (pnpm v10)

A partir de pnpm 10, los scripts de `postinstall` de las dependencias se bloquean por defecto como medida de seguridad. Solo se ejecutan los paquetes declarados explicitamente en `pnpm.onlyBuiltDependencies` del `package.json` correspondiente.

| Paquete | Donde | Por que se necesita |
|---|---|---|
| `esbuild` | `frontend/` | Binario nativo usado por `@angular/build` para compilar Angular |
| `@parcel/watcher` | `frontend/` y `web/` | Watcher nativo de archivos en `ng serve` y `eleventy --serve` |
| `lmdb` | `frontend/` | Cache persistente del builder de Angular |
| `msgpackr-extract` | `frontend/` | Serializacion binaria usada por la cache del builder |

Si tras un `pnpm install` aparece el aviso `Ignored build scripts: <lista>`, revisar que esos paquetes esten en `onlyBuiltDependencies`. Para aprobar nuevos paquetes de forma interactiva:

```bash
pnpm approve-builds
```

El comando reescribe el `package.json` del directorio actual con la lista actualizada.

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

Opcion B (comando pnpm):

```bash
pnpm run dev
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

### Preparacion de entorno y arranque

- `env file ./backend/.env not found` (o `./web/.env`):
  Compose marca esos `.env` como `required: true`. Crearlos copiando desde el correspondiente `*.env.example` antes de arrancar.
- `env file ./backend/.env.dev not found`:
  solo aplica si se usa el override de desarrollo (`docker-compose.dev.yml`). El archivo existe en el repositorio; si falta, comprobar que la rama es la correcta o restaurarlo desde git.
- `docker: 'compose' is not a docker command`:
  el sistema usa Docker Compose v1. Instalar el plugin v2 (`docker compose`) o, como alternativa puntual, usar `docker-compose` con guion.
- `Cannot connect to the Docker daemon`:
  Docker Desktop o el servicio `docker` no esta arrancado. Iniciarlo y reintentar.

### Variables de entorno

- `DATABASE_URL variable is not set`:
  revisar `.env` de raiz. Recordar que los `.env` no interpolan variables, debe ser una URL literal.
- `KeyError: 'SECRET_KEY'`:
  definir `SECRET_KEY` en `backend/.env`. La aplicacion no arranca sin esa clave.
- `KeyError: 'JWT_SECRET_KEY'`:
  definir `JWT_SECRET_KEY` en `backend/.env`. Generar con `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
- `cryptography.fernet.InvalidToken` o errores con `FERNET_KEY`:
  la clave debe ser una Fernet valida (32 bytes en base64 urlsafe). Generar con `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
- CORS bloqueado en navegador desde Angular local:
  comprobar que `ALLOWED_ORIGINS` incluye el origen exacto (`http://localhost:4200` o `http://localhost`). En Docker, el compose lo fuerza a `http://localhost`.

### Puertos y red

- `Port 80 already in use` (o `bind: address already in use`):
  liberar el puerto (otro Nginx, IIS o Skype antiguos suelen ocuparlo) o cambiar el mapeo de `nginx` en `docker-compose.yml`.
- `Port 5432 already in use`:
  hay un Postgres local corriendo. PostgreSQL del compose no se expone al host por defecto, pero si se ha modificado el compose, parar el servicio local o cambiar mapeo.
- La API responde pero los formularios fallan con 403 Turnstile:
  revisar que `TURNSTILE_SECRET_KEY` (backend) y `TURNSTILE_SITE_KEY` (web) son del mismo par. Para desarrollo, usar las claves de prueba oficiales de Cloudflare.

### Base de datos y migraciones

- `No se cargan tablas iniciales` o el seed no aparece:
  el volumen `postgres_data` ya existia y los scripts de `docker-entrypoint-initdb.d/` solo se ejecutan en la primera creacion. Reconstruir con `docker compose down -v` y volver a levantar.
- `alembic.util.exc.CommandError: Can't locate revision`:
  base de datos antigua con una revision no presente en el codigo actual. Hacer `docker compose down -v` para regenerarla desde `schema.sql`.
- `psycopg2.OperationalError: could not connect to server`:
  el backend arranco antes que Postgres. El compose define `depends_on: service_healthy`; si persiste, revisar logs de `postgres` y reintentar `docker compose up -d`.

### Notificaciones (email y Discord)

- Los formularios funcionan pero no llega correo:
  comprobar que `MAIL_GUN_API_KEY`, `MAIL_GUN_DOMAIN` y `MAIL_FROM` estan rellenos. El envio se hace por HTTP contra la API de Mailgun usando `MAIL_GUN_API_URL` como base (por defecto la region EU). Si `MAIL_FROM` esta vacio se usa `noreply@<MAIL_GUN_DOMAIN>`; verifica tambien que el dominio este activo en el panel de Mailgun.
- No llegan mensajes a Discord:
  verificar que el webhook esta activo en el servidor de Discord. `DISCORD_WEBHOOK_AI_OBSERVABILITY_URL` es opcional; si se deja vacio, los eventos de IA caen al webhook de operaciones.

### Frontend y sitio publico

- El navegador muestra una version antigua tras `docker compose up --build`:
  vaciar cache (Ctrl+Shift+R) o cerrar sesion del Service Worker. Angular sirve con hash en los nombres de fichero, pero el `index.html` puede estar cacheado.
- 404 en `/menu/`:
  reconstruir el frontend con `docker compose build --no-cache frontend`. El build de Angular usa `--base-href=/menu/` y un fallo de build deja el SPA sin assets.
