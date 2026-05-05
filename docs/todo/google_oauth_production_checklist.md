# Plan de acción: Google OAuth en producción

> **Contexto**: La aplicación despliega en Railway con un único nginx que enruta
> `/api/` → backend y `/menu` → Angular SPA bajo el mismo dominio.
> El error 400 `invalid_request / flowName=GeneralOAuthFlow` persiste en producción
> incluso tras corregir el bug de codificación de URL (prompt 1).

---

## Causas verificadas del error 400 en producción

| Causa | Dónde se corrige |
|---|---|
| URL mal codificada (`redirect_uri` sin percent-encoding) | Código — prompt 1 |
| `GOOGLE_REDIRECT_URI` apunta a `localhost` en Railway | Variable de entorno Railway |
| `redirect_uri` no registrada en Google Cloud Console | Google Cloud Console |
| Google People API no habilitada en el proyecto | Google Cloud Console |
| Pantalla de consentimiento sin el scope necesario | Google Cloud Console |
| App en modo "Testing" y el usuario no es "test user" | Google Cloud Console |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` vacíos en Railway | Variable de entorno Railway |

---

## Paso 1 — Habilitar Google People API

1. Ir a [Google Cloud Console → APIs y servicios → Biblioteca](https://console.cloud.google.com/apis/library).
2. Buscar **"Google People API"**.
3. Hacer clic en **Habilitar**.

---

## Paso 2 — Crear / revisar las credenciales OAuth

1. Ir a [APIs y servicios → Credenciales](https://console.cloud.google.com/apis/credentials).
2. Si no existe un **"ID de cliente OAuth 2.0"** de tipo *Aplicación web*, crearlo:
   - Tipo: **Aplicación web**
   - Nombre: `Stay Sidekick`
3. En **"URI de redireccionamiento autorizados"**, añadir **las dos** entradas siguientes exactamente como aparecen (sin barra final):
   ```
   http://localhost:5000/api/contactos/google/callback
   https://<TU-DOMINIO-RAILWAY>.up.railway.app/api/contactos/google/callback
   ```
   > **Importante**: Reemplaza `<TU-DOMINIO-RAILWAY>` con el dominio real del servicio
   > nginx en Railway. El path `/api/contactos/google/callback` debe coincidir
   > **byte a byte** con el valor de la variable de entorno `GOOGLE_REDIRECT_URI`.
4. Guardar. Descargar (o copiar) el **Client ID** y el **Client Secret**.

---

## Paso 3 — Configurar la pantalla de consentimiento OAuth

1. Ir a [APIs y servicios → Pantalla de consentimiento de OAuth](https://console.cloud.google.com/apis/credentials/consent).
2. Rellenar los campos obligatorios:
   - **Tipo de usuario**: *Externo* (o *Interno* si solo usarán cuentas del mismo Workspace)
   - **Nombre de la app**: `Stay Sidekick`
   - **Email de asistencia al usuario**: tu correo
   - **Información de contacto del desarrollador**: tu correo
   - **Página principal de la app**: `https://<TU-DOMINIO-RAILWAY>.up.railway.app`
   - **Política de privacidad** (requerida para verificación, puede ser la tuya o un placeholder HTTPS)
3. En la sección **Permisos (scopes)**, añadir:
   ```
   https://www.googleapis.com/auth/contacts
   ```
4. Guardar.

---

## Paso 4 — Gestionar el estado de publicación ("Testing" vs "En producción")

### Opción A — Permanecer en "Testing" (recomendado para el TFG)

El modo *Testing* permite hasta **100 usuarios de prueba** sin pasar la verificación de scopes sensibles (contacts es sensible).

1. En la pantalla de consentimiento, estado: **Testing**.
2. En la sección **Usuarios de prueba**, añadir el email de Google de cada empresa
   que vaya a usar la sincronización.
3. Solo esos emails podrán completar el flujo OAuth. Cualquier otro verá
   "Error 403: access_denied".

> Si el error 400 sigue tras los pasos anteriores, **este es el paso más probable
> que falta**: el usuario que intenta conectar no está en la lista de test users.

### Opción B — Publicar en "En producción"

Requiere verificación de scopes por Google (proceso de días/semanas).
No recomendado para el TFG. Solo necesario si múltiples empresas ajenas
usan la app sin ser añadidas manualmente.

---

## Paso 5 — Variables de entorno en Railway (servicio backend)

En Railway → tu proyecto → servicio `backend` → pestaña **Variables**:

| Variable | Valor |
|---|---|
| `GOOGLE_CLIENT_ID` | El Client ID del paso 2 |
| `GOOGLE_CLIENT_SECRET` | El Client Secret del paso 2 |
| `GOOGLE_REDIRECT_URI` | `https://<TU-DOMINIO-RAILWAY>.up.railway.app/api/contactos/google/callback` |
| `FRONTEND_BASE_URL` | `https://<TU-DOMINIO-RAILWAY>.up.railway.app` |

> **Crítico**: `GOOGLE_REDIRECT_URI` debe usar **HTTPS** y coincidir exactamente
> con lo registrado en Google Cloud Console (sin barra final).

---

## Paso 6 — Variables de entorno en local (`.env`)

Para desarrollo local, el fichero `.env` del backend debe tener:

```env
GOOGLE_CLIENT_ID=<tu-client-id>
GOOGLE_CLIENT_SECRET=<tu-client-secret>
GOOGLE_REDIRECT_URI=http://localhost:5000/api/contactos/google/callback
FRONTEND_BASE_URL=http://localhost:4200
```

> En Docker Compose local, nginx redirige `/api/` → puerto 5000 del backend,
> por lo que el callback es `localhost:5000`. El frontend Angular en Docker
> usa nginx también, así que `FRONTEND_BASE_URL` puede ser `http://localhost`.

---

## Verificación final

Una vez completados todos los pasos:

1. [ ] `GET /api/contactos/google/auth` devuelve una URL de Google que empieza por
       `https://accounts.google.com/o/oauth2/v2/auth?...` con todos los parámetros
       percent-encoded.
2. [ ] La URL redirige a la pantalla de consentimiento de Google (sin error 400).
3. [ ] Al aceptar, Google redirige a `/api/contactos/google/callback?code=...`.
4. [ ] El backend intercambia el code por tokens y redirige al frontend con
       `?google_conectado=true`.
5. [ ] `GET /api/contactos/google/status` devuelve `{"conectado": true, ...}`.
6. [ ] El componente Angular muestra el botón correcto según la combinación
       PMS/Google.
