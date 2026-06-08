---
id: autenticacion-y-seguridad
title: Autenticación y seguridad
sidebar_position: 3
description: JWT HS256, CSRF double-submit, rate limit por IP, Fernet para API keys y headers de seguridad.
---

# Autenticación y seguridad

Stay Sidekick no implementa una sola capa de seguridad: combina **cinco mecanismos** que se solapan para defenderse de fuerza bruta, CSRF, exfiltración de credenciales y abuso de endpoints públicos.

## 1. JWT HS256

[`app/auth/`](https://github.com/sdurutr436/stay-sidekick/tree/main/backend/app/auth) emite tokens firmados con `JWT_SECRET_KEY`.

- **Algoritmo**: HS256 (clave simétrica).
- **TTL**: configurable con `JWT_ACCESS_TOKEN_HOURS` (default `1`).
- **Claims**: `sub` (id de usuario), `empresa_id`, `rol`, `exp`, `iat`.
- **Refresh** mediante endpoint dedicado que valida la cookie HttpOnly del usuario.

El cliente (SPA Angular) guarda el token en `localStorage` y lo inyecta como `Authorization: Bearer <token>` en cada request gracias a un interceptor HTTP.

## 2. Hashing BCrypt

`app/auth/passwords.py` usa BCrypt con factor de coste configurable. Nunca se guarda la contraseña en claro ni reversible. El factor se calibra para tardar ~250 ms en la máquina objetivo, lo suficiente para frenar ataques de fuerza bruta sin penalizar la UX.

## 3. CSRF *double-submit cookie*

`app/security/csrf.py` aplica el patrón **double-submit cookie**:

1. El backend genera un token aleatorio y lo manda en una cookie `csrf_token`.
2. El cliente debe reenviar ese mismo valor en la cabecera `X-CSRF-Token` de cualquier `POST/PUT/PATCH/DELETE`.
3. Si los dos valores no coinciden, el `before_request` global devuelve 403.

Este patrón evita la falsificación de peticiones cross-site sin necesidad de almacenar el token en BD (a diferencia del *synchronizer token pattern*).

## 4. Rate limiting

`Flask-Limiter` aplica límites por IP en endpoints sensibles:

| Endpoint | Default | Variable |
|----------|---------|----------|
| Formulario de contacto | `5/hour` | `RATE_LIMIT_CONTACT` |
| Solicitud de empresa | `3/day` | hard-coded |
| Login | `10/minute` | hard-coded |

El storage del limiter es configurable con `RATE_LIMIT_STORAGE_URI` (default `memory://`). En multi-instancia se recomienda Redis.

## 5. Cifrado Fernet

`app/common/crypto.py` envuelve `cryptography.fernet.Fernet` para cifrar las **API keys de PMS y de IA** que cada empresa configura. La clave maestra `FERNET_KEY` (32 bytes en base64 urlsafe) está fuera de BD y vive en `backend/.env` o en Railway secrets. Sin la clave, los valores cifrados en BD son inutilizables.

## Cabeceras de seguridad

Aplicadas por nginx (no por Flask) sobre toda respuesta:

- `Strict-Transport-Security` (HSTS).
- `Content-Security-Policy` estricta — sin `'unsafe-inline'` en scripts, exigiendo `inlineCritical: false` en Angular.
- `X-Frame-Options: SAMEORIGIN`.
- `X-Content-Type-Options: nosniff`.
- `Referrer-Policy: strict-origin-when-cross-origin`.

## CORS

`ALLOWED_ORIGINS` del `backend/.env` lista los orígenes permitidos separados por coma. En Docker el compose lo sobreescribe a `http://localhost` (todo el tráfico pasa por nginx).
