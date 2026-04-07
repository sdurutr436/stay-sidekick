# Despliegue en Railway — Stay Sidekick

> Guía paso a paso para desplegar los 4 servicios + PostgreSQL en Railway usando Dockerfiles. Cubre CI/CD automático desde ramas `dev` y `main`.

---

## 0. Arquitectura en Railway

La app tiene 5 servicios en Railway (4 contenedores gestionados + 1 base de datos):

```
Internet (HTTPS)
      │
   [nginx]  ← único servicio con dominio público
      │ red privada interna (.railway.internal)
      ├── [frontend]  Angular SPA      puerto 80
      ├── [web]       11ty estático    puerto 80
      └── [backend]   Flask API        puerto 5000
                           │
                      [PostgreSQL]  ← plugin Railway
```

Sólo `nginx` tiene dominio público. El resto se comunica por la red privada interna de Railway.

---

## 1. Cambios obligatorios en el código ANTES de desplegar

Railway usa red privada **IPv6** entre servicios (`.railway.internal`). Los contenedores internos deben escuchar en dual-stack (IPv4 + IPv6). El nginx proxy necesita un parche para evitar el cacheo de DNS.

### 1.1 `nginx/nginx.conf` — Red privada Railway

Sustituye el archivo completo. Los `upstream` con nombres docker-compose no funcionan en Railway:

```nginx
# =============================================================================
# NGINX — Proxy inverso Railway
# Usa la red privada .railway.internal con resolver Railway (fd12::10).
# El truco set $var fuerza re-resolución DNS en cada petición (evita cacheo).
# =============================================================================

server {
    listen 80;
    listen [::]:80;           # IPv6: salud del healthcheck Railway
    server_name localhost;

    # DNS resolver interno de Railway, TTL 1s para evitar IPs caducadas
    resolver [fd12::10] ipv6=on valid=1s;

    # Variables para forzar re-resolución DNS por petición
    set $frontend_url http://frontend.railway.internal:80;
    set $web_url      http://web.railway.internal:80;
    set $backend_url  http://backend.railway.internal:5000;

    # ── API Flask ─────────────────────────────────────────────────────────────
    location /api/ {
        proxy_pass         $backend_url;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }

    # ── Angular SPA (/app/) ───────────────────────────────────────────────────
    location /app/ {
        rewrite ^/app/(.*) /$1 break;
        proxy_pass         $frontend_url;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    }

    # ── 11ty sitio estático ───────────────────────────────────────────────────
    location / {
        proxy_pass         $web_url;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    }
}
```

> **Por qué `set $var`**: nginx cachea DNS al arrancar. Si un servicio se redeploya en Railway cambia de IP (IPv6). Sin `set $var`, nginx mandaría peticiones a la IP vieja y fallaría. Con la variable, nginx re-resuelve antes de cada proxy_pass.

### 1.2 `frontend/nginx.conf` — Dual-stack IPv6

Añade `listen [::]:80`:

```nginx
server {
    listen 80;
    listen [::]:80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 1.3 `web/nginx.conf` — Dual-stack IPv6

```nginx
server {
    listen 80;
    listen [::]:80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

### 1.4 `backend/Dockerfile` — Gunicorn con dual-stack

Cambia el CMD del Dockerfile para usar Gunicorn (el propio comentario del archivo lo pedía):

```dockerfile
# Añadir gunicorn a requirements.txt primero
CMD ["gunicorn", "--bind", "[::]:5000", "--workers", "2", "run:app"]
```

Y en `backend/requirements.txt` añade:
```
gunicorn==21.2.0
```

`[::]:5000` en Linux crea un socket dual-stack (IPv4 + IPv6) gracias a que `IPV6_V6ONLY=0` es el valor por defecto del kernel.

> Si necesitas mantener `run.py` para desarrollo local, el Dockerfile en Railway usará el CMD de Gunicorn igualmente. No hace falta tocar `run.py`.

---

## 2. Archivos `railway.toml` por servicio

Cada servicio necesita su propio `railway.toml`. Railway lo busca en el directorio raíz configurado para el servicio.

### `nginx/railway.toml`
```toml
[build]
builder = "DOCKERFILE"

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 60
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### `frontend/railway.toml`
```toml
[build]
builder = "DOCKERFILE"

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 60
restartPolicyType = "ON_FAILURE"
```

### `web/railway.toml`

> El web service NO puede tener Root Directory en `web/` porque su Dockerfile necesita el contexto de la raíz del repo (copia `frontend/src/styles/`). Este `railway.toml` va en la **raíz del proyecto**.

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "web/Dockerfile"

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 90
restartPolicyType = "ON_FAILURE"
```

### `backend/railway.toml`
```toml
[build]
builder = "DOCKERFILE"

[deploy]
healthcheckPath = "/api/health"
healthcheckTimeout = 120
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

> Necesitarás crear el endpoint `/api/health` en Flask si no existe: que devuelva `{"status": "ok"}` con código 200.

---

## 3. Configuración en Railway Dashboard (setup inicial)

### 3.1 Crear el proyecto

1. Entra en [railway.app](https://railway.app) → New Project
2. Selecciona **Deploy from GitHub repo** → elige el repositorio del TFG
3. Railway creará un servicio vacío. Renómbralo a `nginx`.

### 3.2 Añadir los 5 servicios

Para cada servicio adicional: click en **+ New** → **GitHub Repo** (mismo repo) o **Add Service**.

Los 5 servicios del proyecto:
- `nginx` (dominio público)
- `frontend`
- `web`
- `backend`
- `postgres` (añadido como **Database → PostgreSQL**)

### 3.3 Configurar cada servicio

> **Sobre `railway.toml`**: No hay un campo "Config File Path" en el dashboard. Railway auto-detecta el `railway.toml` dentro del **Root Directory** de cada servicio. Solo hay que configurar el Root Directory correctamente y Railway se encarga del resto.

Entra en cada servicio → **Settings** y configura:

#### Servicio `nginx`
| Ajuste | Valor |
|--------|-------|
| Root Directory | `nginx` |
| Branch | `main` |
| Builder | Dockerfile *(o lo detecta automáticamente por el railway.toml)* |

Variables:
```
PORT=80
RAILWAY=true
```

> `RAILWAY=true` activa `nginx.railway.conf` (red privada Railway) en lugar del `nginx.conf` de docker-compose. Sin esta variable, el proxy no funciona en Railway.

Dominio: en **Settings → Networking** → Generate Domain (o añade tu dominio personalizado).

#### Servicio `frontend`
| Ajuste | Valor |
|--------|-------|
| Root Directory | `frontend` |
| Branch | `main` |
| Builder | Dockerfile |

Sin dominio público (sólo acceso interno vía red privada).

#### Servicio `web`
| Ajuste | Valor |
|--------|-------|
| Root Directory | *(vacío — raíz del repo)* |
| Branch | `main` |
| Builder | Dockerfile |

Variables:
```
TURNSTILE_SITE_KEY=tu-site-key-publica-de-cloudflare
```

Sin dominio público.

> **Importante**: Root Directory vacío es lo que permite que el Dockerfile de `web/` acceda a `frontend/src/styles/` durante el build. Railway encontrará el `railway.toml` de la raíz automáticamente.

#### Servicio `backend`
| Ajuste | Valor |
|--------|-------|
| Root Directory | `backend` |
| Branch | `main` |
| Builder | Dockerfile |

Variables (todas las de `.env.example`):
```
FLASK_ENV=production
SECRET_KEY=<genera con: python -c "import secrets; print(secrets.token_urlsafe(32))">
ALLOWED_ORIGINS=https://tu-dominio.up.railway.app
DATABASE_URL=${{ Postgres.DATABASE_URL }}
JWT_SECRET_KEY=<genera igual que SECRET_KEY>
JWT_ACCESS_TOKEN_HOURS=1
FERNET_KEY=<genera con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
TURNSTILE_SECRET_KEY=tu-secret-key-de-cloudflare
TURNSTILE_VERIFY_URL=https://challenges.cloudflare.com/turnstile/v0/siteverify
GMAIL_USER=tu-correo@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
MAIL_RECIPIENT=destinatario@ejemplo.com
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/TU_ID/TU_TOKEN
RATE_LIMIT_CONTACT=5/hour
```

> `${{ Postgres.DATABASE_URL }}` es una **referencia variable** — Railway inyecta automáticamente la URL de la base de datos del servicio `Postgres`. No escribas la URL a mano.

#### Servicio `postgres`
Railway lo gestiona. No hay configuración manual. Ve a la pestaña **Variables** del servicio Postgres para copiar los valores si los necesitas.

---

## 4. CI/CD — Ramas dev y main

### 4.1 Arquitectura de entornos

Railway usa **Environments** para aislar producción de staging:

```
main branch  →  entorno "production"  →  dominio público real
dev branch   →  entorno "staging"     →  dominio de pruebas
```

Los dos entornos son completamente independientes: base de datos propia, variables propias, no se tocan entre ellos.

### 4.2 Crear el entorno staging

1. **Project Settings → Environments → New Environment**
2. Nómbralo `staging`
3. Selecciona **Duplicate environment** → copia `production`
4. Railway copiará todos los servicios y variables (en estado staged, pendientes de revisar)
5. Revisa y despliega el entorno staging

### 4.3 Cambiar la rama en cada servicio del entorno staging

En el entorno `staging`, entra en cada servicio → **Settings → Source → Branch** → cambia a `dev`.

Así:
- Push a `dev` → despliega automáticamente en `staging`
- Push a `main` (o merge de `dev` → `main`) → despliega automáticamente en `production`

### 4.4 Activar "Wait for CI" (evita despliegues rotos)

Para que Railway no desplie si los tests de GitHub Actions fallan:

1. Cada servicio → **Settings → Deploy → Wait for CI** → activar
2. Railway esperará a que el workflow de GitHub Actions pase antes de desplegar
3. Si el workflow falla → Railway marca el deploy como `SKIPPED`, producción no se toca

### 4.5 Flujo normal de trabajo

```
Desarrollo local
      │
      ▼
git push origin dev
      │
      ├── GitHub Actions corre tests
      │         │
      │    ✓ pass → Railway despliega en staging automáticamente
      │    ✗ fail → Railway cancela el deploy (staging queda igual)
      │
      ▼
Revisas en staging → ok
      │
      ▼
git checkout main && git merge dev && git push origin main
      │
      ├── GitHub Actions corre tests en main
      │         │
      │    ✓ pass → Railway despliega en production automáticamente
      │    ✗ fail → Railway cancela el deploy (production queda igual)
```

---

## 5. Primer despliegue — checklist

- [ ] Hacer los cambios de código de la sección 1 (nginx.conf, dual-stack, gunicorn)
- [ ] Crear los archivos `railway.toml` de la sección 2
- [ ] Commit y push a `main`
- [ ] Crear proyecto en Railway y conectar el repo
- [ ] Añadir los 5 servicios con la configuración de la sección 3
- [ ] Configurar todas las variables de entorno del backend
- [ ] Verificar que `${{ Postgres.DATABASE_URL }}` se resuelve correctamente (pestaña Variables del backend, botón "Show value")
- [ ] Disparar el primer deploy manual (dashboard → Deploy)
- [ ] Revisar logs de build de cada servicio
- [ ] Verificar logs de runtime del nginx (busca errores de resolución DNS)
- [ ] Acceder al dominio público y comprobar:
  - `/` → carga el sitio 11ty
  - `/app/` → carga el panel Angular
  - `/api/health` → devuelve `{"status": "ok"}`
- [ ] Crear entorno staging y repetir para la rama `dev`

---

## 6. Troubleshooting habitual

### `502 Bad Gateway` en nginx
**Causa**: nginx no puede resolver el hostname `.railway.internal`.  
**Diagnóstico**: Logs del servicio nginx → busca `could not be resolved`.  
**Solución**: Confirma que los nombres de servicio en Railway coinciden exactamente con los que usa nginx (`frontend`, `web`, `backend`). Los nombres son case-sensitive.

### Build falla en el servicio `web` — no encuentra `frontend/src/styles/`
**Causa**: Root Directory del servicio `web` no está vacío.  
**Solución**: Settings del servicio → Root Directory → borrarlo todo (dejar en blanco).

### Flask no es alcanzable desde nginx (Connection refused / timeout)
**Causa**: Gunicorn no escucha en IPv6 o el puerto es distinto al configurado en nginx.  
**Solución**: Confirma que el CMD del Dockerfile usa `[::]:5000` y que en `nginx.conf` el backend apunta a `5000`.

### Variables de entorno no disponibles en build (`TURNSTILE_SITE_KEY` vacío)
**Causa**: La variable existe en runtime pero no está declarada como `ARG` en el Dockerfile.  
**Diagnóstico**: El `web/Dockerfile` ya tiene `ARG TURNSTILE_SITE_KEY` en el stage de build. Railway inyecta automáticamente todas las variables como build args — sólo hay que tenerlo declarado.  
**Solución**: Confirma que la variable está en la pestaña Variables del servicio `web` en Railway, no sólo en backend.

### Deploy de `main` explota después de un merge
**Causa**: Los cambios en `dev` no se probaron en staging, o las migraciones de BD rompieron algo.  
**Solución a futuro**: 
1. Activa "Wait for CI" (sección 4.4)
2. Añade un `preDeployCommand` en `backend/railway.toml` para correr migraciones antes del arranque (no manualmente)
3. Haz el merge a main sólo cuando staging esté verde

### Postgres: `FATAL: password authentication failed`
**Causa**: `DATABASE_URL` está hardcodeada en lugar de usar la referencia `${{ Postgres.DATABASE_URL }}`.  
**Solución**: Usa siempre la referencia variable. Railway actualiza automáticamente las credenciales cuando rota contraseñas.

---

## 7. Variables de entorno — resumen completo

### Servicio `nginx`
| Variable | Valor |
|----------|-------|
| `PORT` | `80` |

### Servicio `web`
| Variable | Valor |
|----------|-------|
| `TURNSTILE_SITE_KEY` | clave pública de Cloudflare Turnstile |

### Servicio `backend`
| Variable | Valor |
|----------|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | clave aleatoria (mín. 32 chars) |
| `ALLOWED_ORIGINS` | URL del dominio nginx (ej. `https://staysidekick.up.railway.app`) |
| `DATABASE_URL` | `${{ Postgres.DATABASE_URL }}` |
| `JWT_SECRET_KEY` | clave aleatoria (mín. 32 chars) |
| `JWT_ACCESS_TOKEN_HOURS` | `1` |
| `FERNET_KEY` | clave Fernet generada con `Fernet.generate_key()` |
| `TURNSTILE_SECRET_KEY` | clave secreta de Cloudflare Turnstile |
| `TURNSTILE_VERIFY_URL` | `https://challenges.cloudflare.com/turnstile/v0/siteverify` |
| `GMAIL_USER` | cuenta Gmail |
| `GMAIL_APP_PASSWORD` | contraseña de aplicación de 16 chars |
| `MAIL_RECIPIENT` | email destinatario del formulario de contacto |
| `DISCORD_WEBHOOK_URL` | URL del webhook de Discord |
| `RATE_LIMIT_CONTACT` | `5/hour` |

---

## 8. Dónde vive cada `railway.toml`

No existe un campo "Config File Path" en el dashboard de Railway. El `railway.toml` se detecta automáticamente desde el **Root Directory** de cada servicio. La tabla es informativa para saber qué fichero aplica a cada servicio:

| Servicio | Root Directory | railway.toml aplicado |
|----------|---------------|----------------------|
| nginx | `nginx` | `nginx/railway.toml` |
| frontend | `frontend` | `frontend/railway.toml` |
| web | *(vacío)* | `railway.toml` (raíz del repo) |
| backend | `backend` | `backend/railway.toml` |
