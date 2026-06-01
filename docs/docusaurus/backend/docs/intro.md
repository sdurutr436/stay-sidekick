---
id: intro
title: Introducción
slug: /
sidebar_position: 1
description: Documentación de la API Flask de Stay Sidekick — multiempresa, JWT, RGPD-aware.
---

# API Flask — backend

Este sitio Docusaurus documenta el subproyecto [`backend/`](https://github.com/sdurutr436/stay-sidekick/tree/main/backend) de Stay Sidekick: la **API REST** del panel privado, escrita en **Python 3.12** con **Flask**, **SQLAlchemy** y autenticación **JWT HS256**.

La documentación de cada módulo, clase y función se genera de forma automática con **`pydoc-markdown`** y se publica bajo el bloque "API (pydoc-markdown)" de la barra lateral.

## Visión general

| Pieza | Tecnología | Punto de entrada |
|-------|------------|------------------|
| Framework HTTP | Flask 3 + Blueprints | [`backend/app/__init__.py`](https://github.com/sdurutr436/stay-sidekick/blob/main/backend/app/__init__.py) |
| ORM | SQLAlchemy + Alembic | [`backend/app/models/`](https://github.com/sdurutr436/stay-sidekick/tree/main/backend/app/models), [`backend/migrations/`](https://github.com/sdurutr436/stay-sidekick/tree/main/backend/migrations) |
| Auth | JWT HS256 + BCrypt + CSRF | [`backend/app/auth/`](https://github.com/sdurutr436/stay-sidekick/tree/main/backend/app/auth) |
| Tests | pytest + coverage ≥ 90 % | [`backend/tests/`](https://github.com/sdurutr436/stay-sidekick/tree/main/backend/tests) |
| Lint | ruff | [`backend/ruff.toml`](https://github.com/sdurutr436/stay-sidekick/blob/main/backend/ruff.toml) |
| Despliegue | Gunicorn + Docker + Railway | [`backend/Dockerfile`](https://github.com/sdurutr436/stay-sidekick/blob/main/backend/Dockerfile) |

## Estructura del paquete `app/`

```
backend/app/
├── __init__.py             # create_app: factory + registro de Blueprints
├── config.py               # Carga .env y normaliza configuración por entorno
├── extensions.py           # SQLAlchemy, Migrate, JWT, Limiter, Bcrypt
├── exceptions.py           # Excepciones de dominio y handlers globales
├── auth/                   # Login, JWT, refresh, BCrypt, cambio password
├── common/                 # crypto.py (Fernet), utilidades comunes
├── security/               # CSRF double-submit, honeypot, headers
├── empresas/               # Multi-tenant: alta y gestión de empresas
├── perfil/                 # Cuenta del usuario autenticado y configuración por empresa
├── solicitud/              # Solicitud pública de alta de empresa
├── contact/                # Formulario público de contacto
├── models/                 # ORM SQLAlchemy: User, Empresa, PlantillaVault, AiUsageLog…
├── normalizador_pms/       # Adaptadores de PMS (Smoobu como referencia)
├── h_maestro_apartamentos/         # Herramienta: maestro de apartamentos
├── h_mapa_de_calor/                # Herramienta: mapa de calor operativo
├── h_notificaciones_tardias/       # Herramienta: avisos de check-in tardío
├── h_sincronizador_contactos/      # Herramienta: sync Google Contacts
└── h_vault_comunicaciones/         # Herramienta: vault con asistente IA
```

> Las herramientas operativas (`h_*`) son **módulos autocontenidos**: cada uno expone un Blueprint Flask, sus rutas, su servicio y, en su caso, un cliente externo (PMS, Google, IA). Esta separación hace que añadir una herramienta nueva sea aislado y no toque código de las existentes.

## Cómo se genera esta documentación

El script `prebuild` ejecuta `pydoc-markdown` con la configuración de [`pydoc-markdown.yml`](https://github.com/sdurutr436/stay-sidekick/blob/main/docs/docusaurus/backend/pydoc-markdown.yml):

1. **`PythonLoader`** localiza los módulos listados en `loaders.modules` añadiendo `backend/` al `search_path`.
2. **`FilterProcessor`** descarta nombres privados (los que empiezan por `_`, salvo `__init__`).
3. **`SmartProcessor`** detecta automáticamente el estilo de docstring (Google, NumPy, reST) y lo convierte en MD.
4. **`CrossrefProcessor`** convierte los `:class:` / `:meth:` en enlaces internos.
5. **`DocusaurusRenderer`** genera un fichero `docs/api/<modulo>.md` por cada módulo de Python y un `sidebar.json` que Docusaurus puede leer.

Cualquier función, clase o método con docstring aparece publicada al ejecutar `pnpm build`.

## Lectura recomendada

- [Arquitectura](arquitectura) — factory `create_app`, registro de Blueprints, ciclo request/response.
- [Autenticación y seguridad](autenticacion-y-seguridad) — JWT, CSRF, rate limit, cifrado Fernet.
- [Módulos h_*](modulos-h) — qué hace cada herramienta operativa.
- **API (pydoc-markdown)** — el detalle de cada función pública.
