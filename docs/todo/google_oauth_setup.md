# Configuracion manual: Google OAuth para Sincronizador de Contactos

## Que hay que hacer

La herramienta de sincronizacion de contactos usa Google OAuth 2.0.
Antes de que funcione, tienes que configurar un proyecto en Google Cloud Console
y anadir las variables de entorno al backend.

---

## Pasos en Google Cloud Console

1. Ve a https://console.cloud.google.com
2. Crea un proyecto nuevo (o usa uno existente)
3. En el menu lateral: **APIs y servicios > Biblioteca**
   - Busca "Google People API" y activala
4. En el menu lateral: **APIs y servicios > Credenciales**
   - Haz clic en "Crear credenciales" > "ID de cliente de OAuth"
   - Tipo de aplicacion: **Aplicacion web**
   - Nombre: "Stay Sidekick" (o el que quieras)
   - En "URI de redireccionamiento autorizados", anade:
     - Desarrollo: `http://localhost:5000/api/contactos/google/callback`
     - Produccion: `https://tu-dominio.com/api/contactos/google/callback`
5. Copia el **Client ID** y el **Client Secret** generados

---

## Variables de entorno a anadir en backend/.env

```
GOOGLE_CLIENT_ID=<tu-client-id-aqui>
GOOGLE_CLIENT_SECRET=<tu-client-secret-aqui>
GOOGLE_REDIRECT_URI=http://localhost:5000/api/contactos/google/callback
FRONTEND_BASE_URL=http://localhost:4200
```

En produccion, cambia las URLs al dominio real.

---

## Pantalla de consentimiento OAuth

En Google Cloud Console > **APIs y servicios > Pantalla de consentimiento de OAuth**:
- Tipo de usuario: Externo
- Nombre de la aplicacion: Stay Sidekick
- Correo de soporte: tu correo
- Scopes: anade `https://www.googleapis.com/auth/contacts`
- Si la app esta en modo "Testing", anade los correos de las empresas como usuarios de prueba

---

## Como funciona el flujo

1. Empresa hace clic en "Conectar con Google" en el panel
2. El frontend llama a `GET /api/contactos/google/auth` (con JWT)
3. El backend devuelve la URL de Google OAuth
4. El frontend redirige al usuario a esa URL
5. Google autentica (incluido 2FA si esta activado) y redirige a `/api/contactos/google/callback`
6. El backend intercambia el codigo por tokens, los cifra con Fernet y los guarda en `integraciones_google`
7. El backend redirige al frontend con `?google_conectado=true`
