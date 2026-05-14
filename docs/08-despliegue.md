# 8. Despliegue

**Documentos de referencia para evaluación y operación**

Esta sección resume la estrategia de despliegue de Stay Sidekick. El detalle
operativo completo está en:

| Documento | Contenido |
| --------- | --------- |
| [**DEPLOY.md**](../DEPLOY.md) | Guía consolidada: arranque local y Railway, variables de entorno, verificación, troubleshooting |
| [**railway_deployment.md**](railway_deployment.md) | Procedimiento paso a paso en Railway: servicios, entornos, CI gating y checklist |

---

## Índice

- [8.1. Entorno de despliegue](#81-entorno-de-despliegue)
- [8.2. Arquitectura de contenedores](#82-arquitectura-de-contenedores)
- [8.3. Configuración de CI/CD](#83-configuración-de-cicd)
  - [8.3.1. Pipeline de integración continua (CI)](#831-pipeline-de-integración-continua-ci)
  - [8.3.2. Pipeline de publicación de imágenes (CD)](#832-pipeline-de-publicación-de-imágenes-cd)
- [8.4. Proceso de despliegue en producción](#84-proceso-de-despliegue-en-producción)
  - [8.4.1. Preparación del entorno](#841-preparación-del-entorno)
  - [8.4.2. Variables de entorno](#842-variables-de-entorno)
  - [8.4.3. Despliegue del stack](#843-despliegue-del-stack)
  - [8.4.4. Verificación funcional](#844-verificación-funcional)
- [8.5. URL de la aplicación en producción](#85-url-de-la-aplicación-en-producción)

---

## 8.1. Entorno de despliegue

Stay Sidekick utiliza un enfoque híbrido:

- **Producción** en **Railway** (servicios containerizados, red privada interna y
  dominio público expuesto solo por nginx).
- **Validación previa/local** con **Docker Compose** sobre máquina de desarrollo,
  replicando el stack completo (nginx + frontend + web + backend + postgres).

Esta estrategia permite mantener un entorno de desarrollo reproducible y, al
mismo tiempo, una puesta en producción gestionada por plataforma, con despliegue
automático por rama y control por CI.

| Componente | Tecnología |
|---|---|
| Plataforma cloud | Railway |
| Entorno local reproducible | Docker Engine + Docker Compose v2 |
| Proxy inverso | nginx |
| Backend API | Flask + Gunicorn |
| Frontend SPA | Angular |
| Sitio estático | 11ty |
| Base de datos | PostgreSQL 16 |
| CI/CD | GitHub Actions + Docker Hub |

---

## 8.2. Arquitectura de contenedores

El sistema se organiza en 5 servicios. Solo nginx se publica hacia Internet; el
resto se comunica por red interna.

```
Internet (HTTPS)
      │
  [nginx]  ← único servicio con dominio público
      │ red privada interna (.railway.internal en Railway)
      ├── [frontend]  Angular SPA      :80
      ├── [web]       11ty estático    :80
      └── [backend]   Flask + Gunicorn :5000
                           │
                      [PostgreSQL]
```

En local, el enrutamiento se mantiene con el mismo patrón mediante
`docker-compose.yml`: 

- `/api/*` -> backend
- `/menu/*` -> frontend
- `/*` -> web (11ty)

En Railway, `nginx/nginx.railway.conf` añade resolver IPv6 (`fd12::10`) y
re-resolución DNS por petición para evitar errores cuando los servicios cambian
de IP tras un redeploy.

| Servicio | Contexto/imagen | Puerto público | Puerto interno |
|---|---|---|---|
| `nginx` | `nginx/Dockerfile` | Sí (`80`) | `80` |
| `frontend` | `frontend/Dockerfile` | No | `80` |
| `web` | `web/Dockerfile` | No | `80` |
| `backend` | `backend/Dockerfile` | No | `5000` |
| `postgres` | `postgres:16-alpine` | No | `5432` |

---

## 8.3. Configuración de CI/CD

### 8.3.1. Pipeline de integración continua (CI)

La integración continua está separada por capa y se ejecuta con GitHub Actions.

**1) CI Python (`.github/workflows/ci-python.yml`)**

- Disparador: `push` y `pull_request` sobre `main`.
- Job `lint`: `ruff check backend/app`.
- Job `tests`: arranca servicio `postgres:16-alpine`, instala dependencias y
  ejecuta `pytest backend/tests/ -v`.

**2) CI Angular tests (`.github/workflows/ci-angular-tests.yml`)**

- Disparador: `push` a cualquier rama y `pull_request` a `main`.
- Job `test-frontend`: `npx ng test --watch=false` y generación de cobertura.
- Subida de artefacto `frontend/coverage/` (retención 14 días).
- Job `deploy-check`: build de producción Angular tras pasar tests.

**3) CI Angular build (`.github/workflows/ci-angular.yml`)**

- Build de frontend en `main` y PR contra `main`.
- Verifica que la SPA compila en modo de integración.

**4) CI Web (`.github/workflows/ci-web.yml`)**

- Build del sitio estático 11ty en `main` y PR.

### 8.3.2. Pipeline de publicación de imágenes (CD)

La publicación de contenedores se gestiona con
`.github/workflows/docker-publish.yml`.

Flujo:

1. Se activa al completar uno de estos workflows en `main`:
   `CI Angular`, `CI 11ty`, `CI Python`.
2. Job `verificar`: consulta vía API de GitHub el estado del mismo SHA.
3. Solo si los tres concluyen en `success`, se ejecuta `publicar`.
4. Se construyen y publican en Docker Hub las imágenes:
   - `stay-sidekick-backend`
   - `stay-sidekick-frontend`
   - `stay-sidekick-web`
   - `stay-sidekick-nginx`
5. El tag usado es el SHA corto del commit.

Este gating evita publicar imágenes cuando alguna capa no ha superado su CI.

---

## 8.4. Proceso de despliegue en producción

### 8.4.1. Preparación del entorno

En Railway se crea un proyecto con 5 servicios:

- `nginx` (público)
- `frontend`
- `web`
- `backend`
- `postgres` (Database Plugin)

Configuración clave por servicio:

- `nginx`: root directory `nginx/`, variable `RAILWAY=true`.
- `frontend`: root directory `frontend/`.
- `backend`: root directory `backend/`.
- `web`: root directory vacío (usa contexto raíz para compilar SCSS compartido).

Además, se recomienda activar **Wait for CI** para no desplegar cambios que no
hayan pasado previamente los workflows de GitHub Actions.

### 8.4.2. Variables de entorno

Variables mínimas relevantes para producción:

| Servicio | Variable | Finalidad |
|---|---|---|
| `backend` | `FLASK_ENV=production` | Modo de ejecución |
| `backend` | `SECRET_KEY` | Seguridad Flask |
| `backend` | `JWT_SECRET_KEY` | Firma de JWT |
| `backend` | `DATABASE_URL` | Conexión PostgreSQL |
| `backend` | `FERNET_KEY` | Cifrado de claves externas |
| `backend` | `TURNSTILE_SECRET_KEY` | Validación anti-bots |
| `backend` | `ALLOWED_ORIGINS` | Origen permitido del dominio público |
| `nginx` | `PORT` | Puerto de escucha en Railway |
| `nginx` | `FRONTEND_PORT`, `WEB_PORT`, `BACKEND_PORT` | Puertos internos de proxy |

En Railway, `DATABASE_URL` se configura como referencia al servicio de base de
datos (`${{ Postgres.DATABASE_URL }}`), evitando hardcodear credenciales.

### 8.4.3. Despliegue del stack

El despliegue se produce por integración con GitHub:

- Rama `main` -> entorno `production`.
- Rama `dev` -> entorno `staging` (cuando está configurado en Railway).

Secuencia recomendada:

1. Push a rama de destino.
2. Esperar finalización correcta de CI.
3. Railway despliega automáticamente (o manualmente si se fuerza desde dashboard).
4. Revisar healthchecks de cada servicio (`/healthz` en nginx y `/api/health` en backend).

Para validación local equivalente antes de publicar:

```bash
docker compose up -d --build
docker compose ps
```

### 8.4.4. Verificación funcional

Comprobaciones mínimas post-despliegue:

```bash
# Health del proxy
curl -s https://<dominio-nginx>/healthz

# Health del backend vía proxy
curl -s https://<dominio-nginx>/api/health

# API protegida sin token (debe devolver 401/403 y no HTML)
curl -i https://<dominio-nginx>/api/usuarios
```

Resultado esperado:

- nginx responde correctamente al healthcheck.
- backend devuelve `{"status":"ok"}` en `/api/health`.
- el proxy enruta rutas `/menu/`, `/api/` y `/` a sus servicios correctos.

---

## 8.5. URL de la aplicación en producción

El acceso público se realiza exclusivamente por el servicio `nginx` de Railway.

| Recurso | URL |
|---|---|
| Aplicación en producción (nginx) | `https://staysidekick.up.railway.app` |

> Si Railway regenera el dominio o se configura dominio personalizado, esta URL
> debe actualizarse en la memoria y en `ALLOWED_ORIGINS` del backend.
