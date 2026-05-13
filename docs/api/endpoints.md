# API REST — Stay Sidekick

Base URL: `http://localhost/api` (local) · `https://<dominio>/api` (Railway)

## Autenticación

Los endpoints protegidos requieren el header:
```
Authorization: Bearer <JWT>
```

El JWT se obtiene en `POST /api/auth/login`. Duración configurable con `JWT_ACCESS_TOKEN_HOURS` (por defecto 1 hora).

Los endpoints que modifican estado también requieren el header CSRF:
```
X-CSRF-Token: <token>
```
El token CSRF se obtiene en `GET /api/csrf-token` y debe enviarse como cookie + header (Double-Submit Cookie pattern).

---

## Endpoints públicos

### `GET /api/health`
Health check del servicio.
```bash
curl -s http://localhost/api/health
# {"status": "ok"}
```
| Código | Significado |
|--------|-------------|
| 200 | Servicio operativo |

---

### `GET /api/csrf-token`
Emite un token CSRF como cookie httpOnly y en el cuerpo JSON.
```bash
curl -s -c cookies.txt http://localhost/api/csrf-token
# {"csrf_token": "a3f8c2d1e9b4f7a2c5d8e1b4f7a2c5d8"}
```
| Código | Significado |
|--------|-------------|
| 200 | Token emitido |

---

### `POST /api/auth/login`
Autentica un usuario y devuelve un JWT.

**Body (JSON):**
```json
{ "email": "admin@ejemplo.com", "password": "tu-password" }
```
```bash
CSRF=$(curl -s -c cookies.txt http://localhost/api/csrf-token | python3 -c "import sys,json; print(json.load(sys.stdin)['csrf_token'])")
curl -s -b cookies.txt -H "X-CSRF-Token: $CSRF" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ejemplo.com","password":"tu-password"}' \
  http://localhost/api/auth/login
# {"ok": true, "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
```
| Código | Significado |
|--------|-------------|
| 200 | Login correcto, devuelve `token` |
| 400 | Cuerpo inválido |
| 401 | Credenciales incorrectas |
| 403 | Token CSRF inválido o ausente |
| 429 | Rate limit superado |

---

### `GET /api/auth/validacion`
Valida el JWT (uso interno de nginx para `auth_request`). No llamar directamente desde cliente.

| Código | Significado |
|--------|-------------|
| 200 | JWT válido |
| 401 | JWT inválido o ausente |

---

### `POST /api/contacto`
Procesa el formulario de contacto general (con verificación Turnstile).

| Código | Significado |
|--------|-------------|
| 200 | Mensaje enviado |
| 400 | Datos inválidos o captcha fallido |
| 429 | Rate limit: 10/hour por IP |

---

## Endpoints autenticados

> Todos requieren `Authorization: Bearer <token>`. Los que modifican datos requieren además `X-CSRF-Token`.

### Perfil

| Método | Ruta | Descripción | Códigos |
|--------|------|-------------|---------|
| GET | `/api/perfil` | Datos del usuario autenticado | 200, 404 |
| PUT | `/api/perfil/password` | Cambia contraseña (body: `password_actual`, `password_nuevo`) | 200, 400, 422 |
| GET | `/api/perfil/integraciones` | Estado de las integraciones activas | 200 |
| PUT | `/api/perfil/integraciones/pms` | Actualiza integración PMS *(admin)* | 200, 400, 422 |
| DELETE | `/api/perfil/integraciones/pms` | Elimina integración PMS *(admin)* | 200 |
| PUT | `/api/perfil/integraciones/ia` | Actualiza integración IA *(admin)* | 200, 400, 422 |
| DELETE | `/api/perfil/integraciones/ia` | Elimina integración IA *(admin)* | 200 |
| GET | `/api/perfil/xlsx-apartamentos` | Lee configuración de columnas XLSX | 200 |
| PUT | `/api/perfil/xlsx-apartamentos` | Guarda configuración de columnas XLSX *(admin)* | 200, 400, 422 |
| GET | `/api/perfil/notificaciones-tardio-config` | Lee config de notificaciones tardías | 200 |
| PUT | `/api/perfil/notificaciones-tardio-config` | Guarda config de notificaciones tardías *(admin)* | 200, 400, 422 |

```bash
curl -s -H "Authorization: Bearer $TOKEN" http://localhost/api/perfil
# {"id": "uuid", "email": "admin@ejemplo.com", "rol": "admin", "empresa_id": "uuid"}
```

---

### Apartamentos

| Método | Ruta | Descripción | Códigos |
|--------|------|-------------|---------|
| GET | `/api/apartamentos` | Lista apartamentos activos | 200 |
| GET | `/api/apartamentos/<id>` | Detalle de un apartamento | 200, 404 |
| POST | `/api/apartamentos` | Crea apartamento (body: datos) | 201, 400, 422 |
| PUT | `/api/apartamentos/<id>` | Actualiza apartamento | 200, 400, 404, 422 |
| DELETE | `/api/apartamentos/<id>` | Soft-delete (marca inactivo) | 200, 404 |
| POST | `/api/apartamentos/sincronizacion/smoobu` | Importa propiedades desde Smoobu | 200, 400 *(10/hour)* |
| POST | `/api/apartamentos/importacion` | Importa desde XLSX (multipart: `file`) | 200, 400, 413, 422 *(20/hour)* |
| POST | `/api/apartamentos/importacion/preview` | Preview XLSX sin guardar (multipart: `file`) | 200, 400, 422 *(30/hour)* |
| GET | `/api/apartamentos/pms` | Lee config PMS activo | 200 |
| PUT | `/api/apartamentos/pms` | Crea/actualiza config PMS | 200, 400, 422 |
| DELETE | `/api/apartamentos/pms` | Elimina config PMS | 200, 404 |

```bash
curl -s -H "Authorization: Bearer $TOKEN" http://localhost/api/apartamentos
# [{"id": "uuid", "nombre": "Apartamento 1", "activo": true, ...}]
```

---

### Usuarios *(admin/superadmin)*

| Método | Ruta | Descripción | Códigos |
|--------|------|-------------|---------|
| GET | `/api/usuarios` | Lista usuarios de la empresa | 200 |
| POST | `/api/usuarios` | Crea usuario (body: `email`, `rol`) | 201, 400, 422 |
| PATCH | `/api/usuarios/<id>` | Edita rol del usuario | 200, 400, 404, 422 |
| PATCH | `/api/usuarios/<id>/contrasena` | Resetea contraseña temporal | 200, 404, 422 |
| DELETE | `/api/usuarios/<id>` | Elimina usuario | 200, 404 |

---

### Empresas *(superadmin)*

| Método | Ruta | Descripción | Códigos |
|--------|------|-------------|---------|
| GET | `/api/empresas` | Lista empresas activas | 200 |
| POST | `/api/empresas` | Crea empresa (body: `nombre`, `email`) | 201, 409, 422 |

---

### Contactos Google

| Método | Ruta | Descripción | Códigos |
|--------|------|-------------|---------|
| GET | `/api/contactos/google/auth` | URL OAuth para conectar cuenta Google *(admin)* | 200 |
| GET | `/api/contactos/google/status` | Estado de la conexión Google | 200 |
| DELETE | `/api/contactos/google/conexion` | Desconecta cuenta Google *(admin)* | 200, 404 |
| GET | `/api/contactos/preferencias` | Lee preferencias de sincronización | 200 |
| PUT | `/api/contactos/preferencias` | Guarda preferencias | 200, 400, 422 |
| POST | `/api/contactos/sincronizacion` | Sincroniza PMS → Google Contacts (body: `desde`, `hasta`) | 200, 400 *(10/hour)* |
| POST | `/api/contactos/exportacion/csv` | Genera CSV desde PMS (body: `desde`, `hasta`) | 200, 400 *(20/hour)* |
| POST | `/api/contactos/xlsx/sincronizacion` | Sincroniza XLSX → Google Contacts (multipart: `file`) | 200, 400 *(10/hour)* |
| POST | `/api/contactos/xlsx/exportacion/csv` | Genera CSV desde XLSX (multipart: `file`) | 200, 400 *(20/hour)* |

---

### Notificaciones de check-in tardío

| Método | Ruta | Descripción | Códigos |
|--------|------|-------------|---------|
| GET | `/api/notificaciones/checkin-tardio/status` | Estado del PMS y check-ins del día | 200 |
| POST | `/api/notificaciones/checkin-tardio/checkins` | Parsea XLSX de check-ins (multipart: `file`) | 200, 400 *(20/hour)* |
| GET | `/api/notificaciones/checkin-tardio/plantillas` | Lista plantillas | 200 |
| POST | `/api/notificaciones/checkin-tardio/plantillas` | Crea plantilla (body: `nombre`, `contenido`) | 201, 400 |
| PUT | `/api/notificaciones/checkin-tardio/plantillas/<id>` | Actualiza plantilla | 200, 400, 404 |
| DELETE | `/api/notificaciones/checkin-tardio/plantillas/<id>` | Elimina plantilla | 200, 404 |

---

### Vault de comunicaciones

| Método | Ruta | Descripción | Códigos |
|--------|------|-------------|---------|
| GET | `/api/vault/plantillas` | Lista plantillas (query: `categoria`, `idioma`) | 200 |
| POST | `/api/vault/plantillas` | Crea plantilla | 201, 422 |
| PUT | `/api/vault/plantillas/<id>` | Actualiza plantilla | 200, 404, 422 |
| DELETE | `/api/vault/plantillas/<id>` | Soft-delete | 200, 404 |
| POST | `/api/vault/plantillas/<id>/mejoras` | Mejora con IA (body: `contenido`, `idioma`) | 200, 422, 429, 502, 504 |
| POST | `/api/vault/plantillas/<id>/traducciones` | Traduce con IA (body: `contenido`, `idioma_destino`) | 200, 422, 429, 502, 504 |
| GET | `/api/ai/uso` | Contadores de uso de IA | 200 |
| GET | `/api/ai/config` | Config IA enmascarada *(admin)* | 200 |

---

### Mapa de calor

| Método | Ruta | Descripción | Códigos |
|--------|------|-------------|---------|
| GET | `/api/heatmap` | Genera mapa de calor desde PMS (query: `desde`, `hasta`) | 200, 400, 422 |
| POST | `/api/heatmap/xlsx` | Genera mapa de calor desde XLSX (multipart: `checkins`, `checkouts`; form: `desde`, `hasta`) | 200, 400, 422 *(30/hour)* |
| GET | `/api/heatmap/umbrales` | Lee umbrales de intensidad | 200 |
| PUT | `/api/heatmap/umbrales` | Guarda umbrales *(admin)* | 200, 400, 422 |
| GET | `/api/heatmap/config-xlsx` | Lee config de columnas XLSX | 200 |
| PUT | `/api/heatmap/config-xlsx` | Guarda config de columnas XLSX *(admin)* | 200, 400, 422 |

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost/api/heatmap?desde=2026-05-01&hasta=2026-05-31"
# {"dias": [{"fecha": "2026-05-01", "checkins": 2, "checkouts": 1, "mesAdyacente": false}, ...]}
```

---

## Resumen de seguridad

| Mecanismo | Descripción |
|-----------|-------------|
| JWT (HS256) | Header `Authorization: Bearer <token>`. Claims: `user_id`, `empresa_id`, `rol`, `es_superadmin` |
| CSRF | Double-Submit Cookie. Header `X-CSRF-Token` + cookie `csrf_token` en endpoints de escritura |
| Rate limiting | Por IP, límites por endpoint (ver columna Códigos — *(N/hour)*) |
| CORS | Solo orígenes configurados en `ALLOWED_ORIGINS` |
| Turnstile | Captcha Cloudflare en formularios públicos |

## Códigos de error comunes

| Código | Causa habitual |
|--------|----------------|
| 400 | Body malformado o datos de negocio inválidos |
| 401 | JWT ausente, expirado o inválido |
| 403 | Token CSRF inválido, o rol insuficiente |
| 404 | Recurso no encontrado (o no pertenece a la empresa) |
| 413 | Archivo XLSX demasiado grande (límite 10 MB) |
| 422 | Validación de esquema fallida (Marshmallow) |
| 429 | Rate limit superado |
| 502/504 | Timeout o error del proveedor de IA externo |
