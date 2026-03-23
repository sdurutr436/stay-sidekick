# Dependencias del Backend — Documentación de Librerías

Este documento detalla cada librería añadida al backend, su propósito, motivo de elección y enlace a la documentación oficial.

---

## Framework y Configuración

### Flask `3.1.x`
- **Propósito:** Micro-framework web para Python.
- **Por qué:** Ligero, extensible y estándar de facto para APIs REST en Python. Permite construir la aplicación con el patrón *application factory*.
- **Docs:** https://flask.palletsprojects.com/

### python-dotenv `1.1.x`
- **Propósito:** Carga variables de entorno desde archivos `.env`.
- **Por qué:** Evita hardcodear secretos (claves Turnstile, SECRET_KEY) en el código. Facilita el desarrollo local y la configuración por entorno.
- **Docs:** https://saurabh-kumar.com/python-dotenv/

---

## Seguridad y Sanitización

### nh3 `0.2.x`
- **Propósito:** Sanitización de HTML para prevención de XSS.
- **Por qué:** Es el reemplazo recomendado de `bleach` (que fue declarado en modo mantenimiento en enero de 2023). `nh3` es un binding de Python sobre la librería Rust [ammonia](https://github.com/rust-ammonia/ammonia), lo que le otorga un rendimiento muy superior y una base de código auditada en memoria segura. Se utiliza en modo *zero-tags* (sin etiquetas permitidas) para eliminar cualquier HTML del contenido enviado por el usuario.
- **Docs:** https://nh3.readthedocs.io/

### flask-cors `5.0.x`
- **Propósito:** Gestión de CORS (Cross-Origin Resource Sharing).
- **Por qué:** Permite restringir qué dominios pueden llamar a la API. Solo los orígenes listados en `ALLOWED_ORIGINS` podrán enviar solicitudes, lo que evita peticiones desde dominios no autorizados.
- **Docs:** https://flask-cors.readthedocs.io/

### flask-limiter `3.12.x`
- **Propósito:** Rate limiting por IP.
- **Por qué:** Protege el endpoint de contacto contra abuso (spam, fuerza bruta). Configurable por variable de entorno (`RATE_LIMIT_CONTACT`).
- **Docs:** https://flask-limiter.readthedocs.io/

---

## Validación de Datos

### marshmallow `3.26.x`
- **Propósito:** Serialización, deserialización y validación de esquemas de datos.
- **Por qué:** Permite definir un esquema (`ContactFormSchema`) que valida tipos, longitudes, campos obligatorios y aplica sanitización en el hook `@pre_load`. Es la librería estándar de validación en el ecosistema Flask y separa la lógica de validación de las rutas.
- **Docs:** https://marshmallow.readthedocs.io/

### email-validator `2.2.x`
- **Propósito:** Validación de direcciones de correo electrónico según RFC 5322.
- **Por qué:** Va más allá de una simple regex: comprueba sintaxis completa, normaliza la parte local y el dominio (IDNA/punycode), y opcionalmente verifica registros DNS (MX/A). Es la librería recomendada por `wtforms` y `marshmallow`.
- **Docs:** https://github.com/JoshData/python-email-validator

### phonenumbers `8.13.x`
- **Propósito:** Parseo, validación y formateo de números de teléfono.
- **Por qué:** Es el port oficial en Python de la librería `libphonenumber` de Google. Valida números por país, detecta formatos inválidos y normaliza a formato E.164 (`+34612345678`). Esto asegura consistencia en la base de datos independientemente de cómo el usuario introduzca el número.
- **Docs:** https://github.com/daviddrysdale/python-phonenumbers

---

## HTTP

### requests `2.32.x`
- **Propósito:** Cliente HTTP para Python.
- **Por qué:** Se utiliza para la verificación server-side del captcha Turnstile contra la API de Cloudflare (`https://challenges.cloudflare.com/turnstile/v0/siteverify`). Es la librería HTTP más utilizada y probada del ecosistema Python.
- **Docs:** https://docs.python-requests.org/

---

## Resumen de flujo de seguridad

```
Frontend (Angular) ──POST JSON──▶ Backend (Flask)
                                      │
                                      ▼
                                 ┌─────────────┐
                                 │  CORS check  │ ← flask-cors
                                 └──────┬───────┘
                                        ▼
                                 ┌─────────────┐
                                 │ Rate limit   │ ← flask-limiter
                                 └──────┬───────┘
                                        ▼
                                 ┌─────────────────────────┐
                                 │ Marshmallow @pre_load    │
                                 │  · nh3 (strip HTML/XSS) │
                                 │  · Unicode NFC normalize │
                                 │  · Trim + collapse ws    │
                                 └──────┬──────────────────┘
                                        ▼
                                 ┌─────────────────────────┐
                                 │ Marshmallow validation   │
                                 │  · email-validator       │
                                 │  · phonenumbers          │
                                 │  · lengths, required…    │
                                 └──────┬──────────────────┘
                                        ▼
                                 ┌─────────────────────────┐
                                 │ Turnstile verify (POST)  │ ← requests
                                 └──────┬──────────────────┘
                                        ▼
                                   200 OK / 422 / 403
```
