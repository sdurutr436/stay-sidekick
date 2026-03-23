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
- **Por qué:** Permite restringir qué dominios pueden llamar a la API. Solo los orígenes listados en `ALLOWED_ORIGINS` podrán enviar solicitudes, lo que evita peticiones desde dominios no autorizados. Configurado con `supports_credentials=True` para permitir el envío de cookies CSRF.
- **Docs:** https://flask-cors.readthedocs.io/

### flask-limiter `3.12.x`
- **Propósito:** Rate limiting por IP.
- **Por qué:** Protege el endpoint de contacto contra abuso (spam, fuerza bruta). Configurable por variable de entorno (`RATE_LIMIT_CONTACT`).
- **Docs:** https://flask-limiter.readthedocs.io/

### PyJWT `2.9.x`
- **Propósito:** Generación y verificación de JSON Web Tokens (JWT).
- **Por qué:** Librería ligera y sin dependencias transitivas pesadas para firmar tokens HS256. Se usará en las rutas autenticadas del panel (heatmaps, vault, notificaciones, etc.). No introduce sesiones en el servidor — el estado vive en el token del cliente.
- **Docs:** https://pyjwt.readthedocs.io/

### CSRF — Double-Submit Cookie (sin librería)
- **Propósito:** Protección CSRF stateless para formularios públicos (sin sesión).
- **Por qué:** Usa el patrón *Double-Submit Cookie*: el backend genera un token aleatorio (`secrets.token_urlsafe`), lo envía como cookie `SameSite=Strict`, y espera que el frontend lo devuelva en la cabecera `X-CSRF-Token`. No requiere sesión ni estado en el servidor. Se implementa como decorador (`@csrf_protect`) sin dependencias externas.

### Honeypot (sin librería)
- **Propósito:** Detección de bots simples que rellenan todos los campos del formulario.
- **Por qué:** Un campo oculto (`website`) que los usuarios legítimos no ven pero los bots rellenan automáticamente. Si llega con contenido, se rechaza. Se integra en el esquema Marshmallow con `validate.Length(max=0)`.

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
- **Por qué:** Se utiliza para la verificación server-side del captcha Turnstile contra la API de Cloudflare, y también para el envío de notificaciones al webhook de Discord. Es la librería HTTP más utilizada y probada del ecosistema Python.
- **Docs:** https://docs.python-requests.org/

---

## Notificaciones

### smtplib + email (stdlib)
- **Propósito:** Envío de correo electrónico vía Gmail SMTP.
- **Por qué:** No requiere dependencias externas — forma parte de la biblioteca estándar de Python. Se conecta al servidor SMTP de Gmail (`smtp.gmail.com:587`) con STARTTLS y autenticación mediante *App Password* (contraseña de aplicación de Google). Cada solicitud de contacto válida genera un email al correo configurado en `MAIL_RECIPIENT`.
- **Configuración necesaria:**
  - `GMAIL_USER` → cuenta Gmail remitente.
  - `GMAIL_APP_PASSWORD` → contraseña de aplicación de 16 caracteres (no la contraseña de Gmail). Generarla en https://myaccount.google.com/apppasswords tras activar la verificación en dos pasos.
  - `MAIL_RECIPIENT` → correo destino que recibe las solicitudes.
- **Docs:** https://docs.python.org/3/library/smtplib.html

### Discord Webhooks (vía requests)
- **Propósito:** Aviso instantáneo en un canal de Discord.
- **Por qué:** Los webhooks de Discord son gratuitos, no requieren bot ni librería extra, y permiten enviar embeds enriquecidos con un simple POST JSON. Se reutiliza `requests` que ya está en el proyecto. Cada solicitud válida envía un embed con los datos de contacto al canal configurado.
- **Configuración necesaria:**
  - `DISCORD_WEBHOOK_URL` → URL del webhook creado en Discord (canal → Editar → Integraciones → Webhooks).
- **Docs:** https://discord.com/developers/docs/resources/webhook

---

## Estructura del proyecto

```
backend/app/
├── __init__.py              # App factory
├── config.py                # Configuración (.env)
├── extensions.py            # CORS, limiter
│
├── common/                  # Utilidades compartidas
│   ├── sanitizers/          # text, phone, email (nh3, phonenumbers, email-validator)
│   └── notifications/       # gmail (smtplib), discord (requests)
│
├── security/                # Seguridad transversal
│   ├── csrf.py              # Double-Submit Cookie (stateless)
│   ├── honeypot.py          # Campo oculto anti-bot
│   └── jwt.py               # JWT HS256 (PyJWT)
│
├── contact/                 # Feature: formulario público
│   ├── routes.py            # Blueprint /api/contact + /api/csrf-token
│   ├── schemas.py           # ContactFormSchema (Marshmallow)
│   └── service.py           # Orquestación: validar → captcha → notificar
│
├── services/                # Servicios compartidos
│   └── turnstile.py         # Verificación Cloudflare Turnstile
│
├── exceptions/              # Excepciones personalizadas
├── models/                  # Modelos de datos (futuro)
└── repositories/            # Repositorios de datos (futuro)
```

## Resumen de flujo de seguridad

```
Frontend (Angular) ──GET /api/csrf-token──▶ Backend (Flask)
                                               │
                                          Cookie csrf_token
                                               │
Frontend ──POST /api/contact──▶ Backend        ▼
  (X-CSRF-Token header)           │
                                  ▼
                           ┌─────────────┐
                           │  CORS check  │ ← flask-cors (supports_credentials)
                           └──────┬───────┘
                                  ▼
                           ┌─────────────┐
                           │ Rate limit   │ ← flask-limiter
                           └──────┬───────┘
                                  ▼
                           ┌──────────────┐
                           │ CSRF verify   │ ← Double-Submit Cookie
                           └──────┬───────┘
                                  ▼
                           ┌─────────────────────────┐
                           │ Marshmallow @pre_load    │
                           │  · nh3 (strip HTML/XSS) │
                           │  · Unicode NFC normalize │
                           │  · Trim + collapse ws    │
                           │  · Honeypot check (max=0)│
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
                        ┌─────────┴─────────┐
                        │                    │
                        ▼                    ▼
              ┌──────────────┐     ┌──────────────────┐
              │ Gmail SMTP   │     │ Discord Webhook   │
              │ (smtplib)    │     │ (requests POST)   │
              └──────────────┘     └──────────────────┘
                        │                    │
                        └─────────┬──────────┘
                                  ▼
                             200 OK / 422 / 403
```

### Rutas autenticadas (futuro)

```
Frontend ──POST /api/auth/login──▶ Backend
                                      │
                                 JWT (HS256, PyJWT)
                                      │
Frontend ──GET /api/panel/...──▶ Backend
  (Authorization: Bearer <token>)  │
                                   ▼
                            ┌──────────────┐
                            │ @jwt_required │ ← PyJWT
                            └──────┬───────┘
                                   ▼
                            Ruta protegida
```
