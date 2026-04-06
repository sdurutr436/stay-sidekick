# Claves y secretos que necesitas generar

Este documento recoge todas las variables de entorno que **debes generar antes de arrancar** la aplicación en cualquier entorno (desarrollo, staging, producción).

Copia las instrucciones de generación y pega el resultado en el fichero `.env` correspondiente. **Nunca compartas estas claves** ni las subas a Git (están excluidas por `.gitignore`).

---

## 1. `SECRET_KEY` — Flask session secret

Usada por Flask para firmar cookies de sesión.

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Dónde:** `backend/.env`  
**Variable:** `SECRET_KEY`

---

## 2. `JWT_SECRET_KEY` — Firmado de tokens JWT

Usada para firmar y verificar los tokens de autenticación del panel.

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Dónde:** `backend/.env`  
**Variable:** `JWT_SECRET_KEY`

---

## 3. `FERNET_KEY` — Cifrado de API keys en base de datos

Clave simétrica Fernet para cifrar las API keys de PMS (Smoobu, Beds24...) y otros secretos antes de persistirlos en PostgreSQL.

> **Importante:** Si pierdes esta clave, todas las API keys almacenadas en BD quedan ilegibles y deberás volver a configurarlas.

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Dónde:** `backend/.env`  
**Variable:** `FERNET_KEY`

---

## 4. `TURNSTILE_SECRET_KEY` — Cloudflare Turnstile (captcha)

Obtenida desde el panel de Cloudflare → Turnstile → tu sitio → Secret key.

**URL:** https://dash.cloudflare.com/?to=/:account/turnstile  
**Dónde:** `backend/.env`  
**Variable:** `TURNSTILE_SECRET_KEY`

---

## 5. `GMAIL_APP_PASSWORD` — Contraseña de aplicación Gmail

Para enviar notificaciones por correo (formulario de contacto, alertas).

1. Activa la **verificación en dos pasos** en tu cuenta de Google.
2. Ve a https://myaccount.google.com/apppasswords
3. Crea una contraseña de aplicación → *Otro* → "Stay Sidekick".
4. Copia los 16 caracteres **sin espacios**.

**Dónde:** `backend/.env`  
**Variables:** `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `MAIL_RECIPIENT`

---

## 6. `DISCORD_WEBHOOK_URL` — Webhook de Discord

Para recibir notificaciones de contacto en un canal de Discord.

1. En Discord → canal deseado → Editar canal → Integraciones → Webhooks.
2. Crea un nuevo webhook y copia la URL completa.

**Dónde:** `backend/.env`  
**Variable:** `DISCORD_WEBHOOK_URL`

---

## Resumen rápido

| Variable | Cómo generarla |
|----------|---------------|
| `SECRET_KEY` | `secrets.token_urlsafe(32)` |
| `JWT_SECRET_KEY` | `secrets.token_urlsafe(48)` |
| `FERNET_KEY` | `Fernet.generate_key().decode()` |
| `TURNSTILE_SECRET_KEY` | Panel de Cloudflare |
| `GMAIL_APP_PASSWORD` | Panel de Google — App Passwords |
| `DISCORD_WEBHOOK_URL` | Panel de Discord — Webhooks |

---

> Consulta `backend/.env.example` para ver todas las variables disponibles con sus descripciones.
