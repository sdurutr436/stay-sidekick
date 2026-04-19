# Docker — Despliegue local

Referencia completa para levantar y operar el stack completo de Stay Sidekick
en local con Docker Compose.

## Servicios incluidos

| Servicio | Imagen / Build | Puerto interno | Descripción |
|----------|---------------|----------------|-------------|
| `nginx` | `./nginx` | 80 → **localhost:80** | Proxy inverso, único punto de entrada |
| `frontend` | `./frontend` | 80 | Angular SPA (servida por nginx interno) |
| `web` | `./web` | 80 | Sitio estático 11ty (servido por nginx interno) |
| `backend` | `./backend` | 5000 | API REST Flask |
| `postgres` | `postgres:16-alpine` | 5432 (interno) | PostgreSQL 16 con volumen persistente |

## Primer uso

```bash
# 1. Copiar y completar el .env del backend
cp backend/.env.example backend/.env
# Editar backend/.env con tus claves reales (SMTP, Discord, JWT…)

# 2. El web/.env ya está creado con la key de prueba de Turnstile
#    (1x00000000000000000000AA — siempre OK en desarrollo)
#    Para producción, editar web/.env con la site key real de Cloudflare.
```

## Arrancar el stack

```bash
# Construir todas las imágenes y arrancar en foreground (ver logs en tiempo real)
docker compose up --build

# Construir y arrancar en background
docker compose up -d --build

# Solo arrancar (sin reconstruir imágenes)
docker compose up -d
```

## Estado y logs

```bash
# Ver qué contenedores están corriendo y su estado
docker compose ps

# Seguir los logs de todos los servicios
docker compose logs -f

# Logs de un servicio concreto
docker compose logs -f backend
docker compose logs -f web
docker compose logs -f frontend
docker compose logs -f nginx
docker compose logs -f postgres

# Últimas N líneas de un servicio
docker compose logs --tail=50 backend
```

## Reiniciar y parar

```bash
# Reiniciar un único servicio (útil tras cambiar su .env)
docker compose restart backend
docker compose restart web

# Reiniciar todos los servicios
docker compose restart

# Parar todos los contenedores (conserva volúmenes y datos)
docker compose stop

# Parar y eliminar contenedores (conserva el volumen postgres_data)
docker compose down

# Parar, eliminar contenedores Y borrar la base de datos
docker compose down -v
```

## Reconstruir solo un servicio

Cuando cambias código en un servicio y no quieres reconstruir todo:

```bash
docker compose up -d --build backend
docker compose up -d --build web
docker compose up -d --build frontend
```

## Base de datos

- Los datos de PostgreSQL se almacenan en el volumen `postgres_data`.
- El schema inicial (`backend/db/schema.sql`) se aplica automáticamente solo la **primera vez** que se crea el volumen.
- Si necesitas aplicar el schema de nuevo (desarrollo), borrar el volumen:

```bash
docker compose down -v          # borra postgres_data
docker compose up -d --build    # recrea con schema limpio
```

Para conectarse a la base de datos desde el host (con cualquier cliente SQL):

```
Host:     localhost
Puerto:   5432        # expuesto solo si añades ports: en el servicio postgres
Usuario:  postgres
Password: postgres
DB:       stay_sidekick
```

> El servicio `postgres` no expone el puerto 5432 al host por defecto para mayor seguridad.
> Si necesitas acceso directo, añade temporalmente `ports: ["5432:5432"]` en `docker-compose.yml`.

Para ejecutar comandos SQL directamente:

```bash
docker compose exec postgres psql -U postgres -d stay_sidekick
```

## Variables de entorno

### `backend/.env`

Copiar desde `backend/.env.example` y completar:

| Variable | Descripción |
|----------|-------------|
| `FLASK_ENV` | `development` / `production` |
| `SECRET_KEY` | Clave aleatoria para Flask sessions |
| `JWT_SECRET_KEY` | Clave para firmar tokens JWT |
| `TURNSTILE_SECRET_KEY` | Secret key de Cloudflare Turnstile (privada) |
| `GMAIL_USER` | Cuenta Gmail para envío de notificaciones |
| `GMAIL_APP_PASSWORD` | Contraseña de aplicación Gmail (16 caracteres) |
| `MAIL_RECIPIENT` | Correo que recibe las solicitudes de contacto |
| `DISCORD_WEBHOOK_URL` | Webhook de Discord para notificaciones |

> `DATABASE_URL` y `ALLOWED_ORIGINS` son inyectadas automáticamente por `docker-compose.yml` para el entorno Docker. No es necesario cambiarlas.

### `web/.env`

| Variable | Descripción |
|----------|-------------|
| `TURNSTILE_SITE_KEY` | Site key **pública** de Cloudflare Turnstile |

En desarrollo usa `1x00000000000000000000AA` (key de prueba oficial, siempre OK).
En producción, sustituir por la site key real obtenida en el [Dashboard de Cloudflare](https://dash.cloudflare.com/).

## URLs tras arrancar

| URL | Servicio |
|-----|---------|
| http://localhost/ | Sitio estático (11ty) |
| http://localhost/app/ | App Angular |
| http://localhost/api/ | API REST Flask |

## Troubleshooting

**`web/.env not found`**
→ El fichero `web/.env` no existe. Crearlo con `TURNSTILE_SITE_KEY=1x00000000000000000000AA` para desarrollo.

**`backend/.env not found`**
→ Ejecutar `cp backend/.env.example backend/.env` y rellenar las variables.

**Puerto 80 ocupado**
→ Otro proceso usa el puerto 80. Identificarlo con `sudo lsof -i :80` y detenerlo,
o cambiar el mapeo en `docker-compose.yml` a `"8080:80"`.

**Cambios en el código no se reflejan**
→ Reconstruir la imagen del servicio afectado: `docker compose up -d --build <servicio>`.

**La base de datos no tiene las tablas**
→ El schema solo se aplica la primera vez que se crea el volumen. Borrar el volumen y relanzar:
`docker compose down -v && docker compose up -d --build`.
