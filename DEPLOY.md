# Despliegue — Stay Sidekick

Guía consolidada para desplegar el stack completo (nginx · Angular · 11ty · Flask · PostgreSQL).
Para el detalle completo consulta los documentos enlazados en cada sección.

---

## 1. Requisitos previos

| Herramienta | Versión mínima |
|-------------|---------------|
| Docker      | 24+           |
| Docker Compose | v2 (plugin) |
| Git         | cualquiera    |

Para despliegue en producción (Railway): cuenta en [railway.app](https://railway.app) y repositorio en GitHub.

---

## 2. Despliegue local con Docker Compose

```bash
# 1. Clonar el repositorio
git clone https://github.com/sdurutr436/tfg-alberti.git
cd tfg-alberti

# 2. Preparar los archivos de entorno
cp .env.example .env                  # credenciales PostgreSQL — editar POSTGRES_PASSWORD
cp backend/.env.example backend/.env  # claves Flask, JWT, SMTP, Discord…
# web/.env ya está incluido con la site key de prueba de Turnstile

# 3. Construir imágenes y arrancar
docker compose up --build             # foreground (ver logs en tiempo real)
docker compose up -d --build          # background
```

**URLs tras arrancar:**

| URL | Servicio |
|-----|---------|
| http://localhost/ | Sitio estático (11ty) |
| http://localhost/menu/ | App Angular |
| http://localhost/api/ | API REST Flask |

**Verificar que todo arrancó correctamente:**

```bash
docker compose ps
# NAME                    IMAGE                    COMMAND                  SERVICE    CREATED          STATUS                    PORTS
# tfg-alberti-nginx-1     tfg-alberti-nginx        "/docker-entrypoint.…"   nginx      10 seconds ago   Up 9 seconds              0.0.0.0:80->80/tcp
# tfg-alberti-backend-1   tfg-alberti-backend      "/bin/sh -c 'flask d…"   backend    10 seconds ago   Up 8 seconds
# tfg-alberti-frontend-1  tfg-alberti-frontend     "/docker-entrypoint.…"   frontend   10 seconds ago   Up 9 seconds
# tfg-alberti-web-1       tfg-alberti-web          "/docker-entrypoint.…"   web        10 seconds ago   Up 9 seconds
# tfg-alberti-postgres-1  postgres:16-alpine       "docker-entrypoint.s…"   postgres   10 seconds ago   Up 9 seconds (healthy)

docker compose logs --tail=5 backend
# backend-1  | [INFO] Starting gunicorn 21.2.0
# backend-1  | [INFO] Listening at: :::5000 (1)
# backend-1  | [INFO] Using worker: sync
# backend-1  | [INFO] Booting worker with pid: 8
# backend-1  | [INFO] Booting worker with pid: 9

curl -s http://localhost/api/health
# {"status": "ok"}
```

> Las salidas anteriores son de ejemplo. Reemplazar con capturas reales tras `docker compose up -d --build` (ver [docs/todo/t-evidencias-docker.md](docs/todo/t-evidencias-docker.md)).

Referencia completa de comandos y troubleshooting: [docs/devops/docker-local.md](docs/devops/docker-local.md)

---

## 3. Despliegue en producción (Railway)

Railway ejecuta los 5 servicios en contenedores con red privada `.railway.internal`. Solo `nginx` tiene dominio público.

```
Internet (HTTPS)
      │
   [nginx]  ← único servicio con dominio público
      │ red privada .railway.internal
      ├── [frontend]  Angular SPA      :80
      ├── [web]       11ty estático    :80
      └── [backend]   Flask API        :5000
                           │
                      [PostgreSQL]  ← plugin Railway
```

### Pasos resumidos

1. Crear proyecto en [railway.app](https://railway.app) → New Project → Deploy from GitHub repo.
2. Añadir los 5 servicios (nginx, frontend, web, backend, postgres como Database Plugin).
3. Configurar el **Root Directory** de cada servicio:
   - `nginx` → `nginx/`
   - `frontend` → `frontend/`
   - `web` → *(vacío — contexto raíz necesario para SCSS compartido)*
   - `backend` → `backend/`
4. Añadir la variable `RAILWAY=true` al servicio `nginx` (activa `nginx.railway.conf`).
5. Añadir todas las variables de entorno del backend (sección 4 de este documento).
6. Activar **Wait for CI** en cada servicio para que Railway no despliegue si los tests fallan.
7. Disparar el primer deploy manual desde el dashboard.

Guía paso a paso completa: [docs/railway_deployment.md](docs/railway_deployment.md)

---

## 4. Variables de entorno

### `.env` (raíz del proyecto — PostgreSQL local)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `POSTGRES_DB` | Nombre de la base de datos | `stay_sidekick` |
| `POSTGRES_USER` | Usuario de PostgreSQL | `postgres` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | *(cambiar en producción)* |
| `DATABASE_URL` | URI de conexión completa | `postgresql://postgres:****@postgres:5432/stay_sidekick` |

### `backend/.env` (API Flask)

| Variable | Descripción |
|----------|-------------|
| `FLASK_ENV` | `development` / `production` |
| `SECRET_KEY` | Clave aleatoria Flask (mín. 32 chars) |
| `JWT_SECRET_KEY` | Clave para firmar tokens JWT |
| `TURNSTILE_SECRET_KEY` | Secret key de Cloudflare Turnstile |
| `GMAIL_USER` | Cuenta Gmail para notificaciones |
| `GMAIL_APP_PASSWORD` | Contraseña de aplicación Gmail (16 chars) |
| `MAIL_RECIPIENT` | Correo que recibe los formularios |
| `DISCORD_WEBHOOK_URL` | Webhook de Discord (solicitudes empresa) |
| `DISCORD_WEBHOOK_CONTACT_URL` | Webhook de Discord (contacto general) |
| `FERNET_KEY` | Clave Fernet para cifrado de API keys en BD |
| `GOOGLE_CLIENT_ID` | OAuth Google (sincronización contactos) |
| `GOOGLE_CLIENT_SECRET` | OAuth Google (sincronización contactos) |

### Railway — servicio `backend`

En Railway, `DATABASE_URL` se configura como referencia variable: `${{ Postgres.DATABASE_URL }}`.
No escribir la URL a mano — Railway la actualiza automáticamente al rotar credenciales.

---

## 5. Verificación post-despliegue

```bash
# Health check básico
curl -s http://localhost/api/health
# {"status": "ok"}

curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health
# 200

# Headers de seguridad
curl -I http://localhost/
# X-Frame-Options: SAMEORIGIN
# X-Content-Type-Options: nosniff
# Referrer-Policy: strict-origin-when-cross-origin
# Content-Security-Policy: default-src 'self'; ...
```

En Railway, sustituir `http://localhost` por el dominio público del servicio nginx.

Verificación completa con ejemplos de login y endpoints autenticados: [docs/devops/docker-local.md — Verificación y pruebas](docs/devops/docker-local.md#verificación-y-pruebas)

---

## 6. Troubleshooting

**`DATABASE_URL variable is not set`**
→ Falta crear el `.env` raíz. Ejecutar `cp .env.example .env` y rellenar `POSTGRES_PASSWORD`.

**`backend/.env not found`**
→ Ejecutar `cp backend/.env.example backend/.env` y completar las variables.

**Puerto 80 ocupado**
→ Identificar el proceso con `sudo lsof -i :80` y detenerlo, o cambiar el mapeo en `docker-compose.yml` a `"8080:80"`.

**`502 Bad Gateway` en nginx (Railway)**
→ nginx no puede resolver el hostname `.railway.internal`. Confirmar que los nombres de servicio coinciden exactamente. Consultar [docs/railway_deployment.md — Troubleshooting](docs/railway_deployment.md#6-troubleshooting-habitual).

**La base de datos no tiene las tablas**
→ El schema solo se aplica la primera vez que se crea el volumen. Ejecutar:
`docker compose down -v && docker compose up -d --build`

**Flask no inicia: `KeyError: SECRET_KEY`**
→ La variable `SECRET_KEY` es obligatoria. Verificar que `backend/.env` existe y tiene la variable definida.
