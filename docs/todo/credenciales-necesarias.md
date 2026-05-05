# Credenciales necesarias para poner en marcha el proyecto

Todas van en `backend/.env` (copia de `.env.example`). Nunca commitear este fichero.

---

## 1. SECRET_KEY (Flask)

Clave aleatoria para firmar sesiones Flask.

```
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Pegar el resultado en `SECRET_KEY=`.

---

## 2. JWT_SECRET_KEY

Clave aleatoria para firmar los tokens JWT del panel.

```
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Pegar en `JWT_SECRET_KEY=`.

---

## 3. FERNET_KEY

Clave para cifrar las API keys almacenadas en la base de datos (PMS, IA, Google).

```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Pegar en `FERNET_KEY=`. **Guardar en un lugar seguro — si se pierde, todas las credenciales cifradas en BD quedan irrecuperables.**

---

## 4. DATABASE_URL (PostgreSQL)

URI de conexión a la base de datos.

- Con Docker Compose ya viene inyectada automáticamente; no hace falta cambiarla.
- Sin Docker (dev local): cambiar `postgres` por `localhost`.

Formato: `postgresql://usuario:contraseña@host:5432/stay_sidekick`

---

## 5. TURNSTILE_SECRET_KEY (Cloudflare Turnstile)

Protege el formulario de contacto público contra bots.

1. Ir a https://dash.cloudflare.com → Turnstile.
2. Crear un nuevo sitio (tipo "Managed").
3. Anotar la **Secret Key** (va aquí) y la **Site Key** (va en el frontend).
4. Pegar en `TURNSTILE_SECRET_KEY=`.

---

## 6. GMAIL_USER + GMAIL_APP_PASSWORD

Para enviar emails de notificación desde la app.

1. Usar una cuenta de Gmail dedicada (p. ej. `staysidekick.notif@gmail.com`).
2. Activar la verificación en dos pasos en esa cuenta.
3. Ir a https://myaccount.google.com/apppasswords.
4. Crear contraseña de aplicación → "Correo" → "Otro (Stay Sidekick)".
5. Copiar los 16 caracteres **sin espacios** en `GMAIL_APP_PASSWORD=`.
6. Poner la dirección de Gmail en `GMAIL_USER=`.
7. Poner el email destinatario de los formularios de contacto en `MAIL_RECIPIENT=`.

---

## 7. DISCORD_WEBHOOK_URL

Para recibir avisos en un canal de Discord.

1. En Discord, ir al canal deseado → Editar canal → Integraciones → Webhooks.
2. Crear nuevo webhook, copiar la URL.
3. Pegar en `DISCORD_WEBHOOK_URL=`.

---

## 8. GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET (OAuth 2.0)

Para la sincronización de contactos con Google Contacts.

1. Ir a https://console.cloud.google.com.
2. Crear un proyecto (o usar uno existente).
3. Habilitar la API **Google People API**.
4. Ir a "Credenciales" → Crear credencial → ID de cliente OAuth 2.0.
5. Tipo de aplicación: **Aplicación web**.
6. URI de redireccionamiento autorizado: `http://localhost:5000/api/contactos/google/callback` (dev) y la URL de producción cuando la haya.
7. Copiar Client ID → `GOOGLE_CLIENT_ID=` y Client Secret → `GOOGLE_CLIENT_SECRET=`.
8. En `GOOGLE_REDIRECT_URI=` poner la URI de callback del backend.
9. En `FRONTEND_BASE_URL=` poner la URL base del frontend (dev: `http://localhost:4200`).

---

## 9. AI_DEFAULT_API_KEY (Gemini — free tier del sistema)

Clave de Gemini que usarán las empresas sin BYOK configurado.

1. Ir a https://aistudio.google.com/app/apikey.
2. Crear una clave de API.
3. Pegar en `AI_DEFAULT_API_KEY=`.

Límites controlados por `AI_FREE_LIMIT_DAILY` (100) y `AI_FREE_LIMIT_WEEKLY` (500).

---

## 10. BYOK por empresa (Perfil > IA — se configura desde la UI)

Cada empresa puede traer su propia clave. Se gestiona desde el panel en Perfil > IA, no desde `.env`. Proveedores soportados:

- **Gemini**: clave desde https://aistudio.google.com/app/apikey
- **OpenAI**: clave desde https://platform.openai.com/api-keys
- **Anthropic (Claude)**: clave desde https://console.anthropic.com/settings/api-keys

---

## 11. AI_PROMPT_ADMIN_IPS

IPs autorizadas para editar los system prompts vía `PUT /api/admin/system-prompts/<nombre>`.

Por defecto `127.0.0.1` (solo localhost). En producción, añadir la IP del servidor o la de la VPN.

```
AI_PROMPT_ADMIN_IPS=127.0.0.1,203.0.113.5
```
