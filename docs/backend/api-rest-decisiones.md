# Decisiones de diseño REST — Stay Sidekick API

## Convención general

La API sigue REST con prefijo `/api/`. Recursos en plural (colecciones) o singular (recurso único bien definido). **Sin verbos en rutas.**

---

## Por qué se usa POST en endpoints de acción

REST puro modela **recursos**, no acciones. Sin embargo, ciertas operaciones de Stay Sidekick son acciones puras (trigger de un proceso, descarga de un fichero generado) que no crean un recurso persistente. En esos casos:

- Se usa **POST** (o PUT cuando el resultado es idempotente).
- La ruta es un **sustantivo** que describe el resultado o el proceso, no el verbo.
- El endpoint queda **documentado aquí** como excepción justificada.

| Endpoint | Método | Justificación |
|----------|--------|---------------|
| `POST /api/contactos/sincronizacion` | POST | Trigger de sincronización PMS→Google. No crea recurso persistente; el log se registra internamente. |
| `POST /api/contactos/exportacion/csv` | POST | Genera y descarga un CSV. Necesita fechas en el body (no en query string) porque el payload puede ser complejo. No crea recurso. |
| `POST /api/contactos/xlsx/sincronizacion` | POST | Misma lógica que arriba pero la fuente de datos es un XLSX subido (multipart). |
| `POST /api/contactos/xlsx/exportacion/csv` | POST | Igual pero en lugar de sincronizar genera el CSV localmente. |
| `POST /api/apartamentos/sincronizacion/smoobu` | POST | Trigger de pull de propiedades desde la API de Smoobu. Hace upsert interno. |
| `POST /api/apartamentos/importacion` | POST | Importación de apartamentos desde XLSX subido (multipart). Hace upsert interno. |
| `POST /api/notificaciones/checkin-tardio/checkins` | POST | Parsea un XLSX subido y devuelve los check-ins de hoy. Procesamiento en memoria, no persiste (RGPD). |
| `POST /api/notificaciones/checkin-tardio/email` | POST | Dispara el envío de un email de notificación de check-in tardío vía Gmail SMTP. |

---

## Flujo de los 4 casos del sincronizador de contactos

La herramienta combina dos variables independientes:

- **Fuente de reservas**: API del PMS (Smoobu/Beds24/…) o XLSX descargado del PMS manualmente.
- **Destino de contactos**: Google Contacts API (conectado) o CSV para importación manual.

```
                     Google conectado          Google desconectado
                 ┌─────────────────────┬──────────────────────────┐
Fuente: PMS API  │ POST /contactos/     │ POST /contactos/          │
                 │   sincronizacion     │   exportacion/csv         │
                 │ (fechas en body)     │ (fechas en body)          │
                 ├─────────────────────┼──────────────────────────┤
Fuente: XLSX     │ POST /contactos/     │ POST /contactos/          │
  (multipart)    │   xlsx/sincronizacion│   xlsx/exportacion/csv    │
                 │ (file en form-data)  │ (file en form-data)       │
                 └─────────────────────┴──────────────────────────┘
```

Los cuatro endpoints comparten la misma transformación interna (reservas → contactos Google) y las mismas preferencias de la empresa (formato de nombre, etiqueta de apartamento, etc.).

---

## Recursos PMS (`/api/apartamentos/pms`)

La configuración del PMS (proveedor + API key cifrada) vive bajo `/api/apartamentos/pms` porque `h_maestro_apartamentos` es el módulo propietario de la sincronización de propiedades.

| Método | Ruta | Acción |
|--------|------|--------|
| `GET` | `/api/apartamentos/pms` | Lee la config del PMS (sin exponer la API key). |
| `PUT` | `/api/apartamentos/pms` | Crea o actualiza la config del PMS (upsert idempotente → PUT). |
| `DELETE` | `/api/apartamentos/pms` | Elimina la config del PMS. |

> **Nota**: el endpoint `GET /api/perfil/integraciones` también expone el estado del PMS (si está configurado y qué proveedor) de forma resumida, ya que el panel de perfil muestra un resumen de todas las integraciones. `GET /api/apartamentos/pms` devuelve el detalle completo para la gestión específica del módulo de apartamentos.

---

## Conexión Google OAuth (`/api/contactos/google/conexion`)

El recurso `conexion` representa la vinculación OAuth entre la empresa y su cuenta Google. `DELETE /api/contactos/google/conexion` revoca y elimina los tokens almacenados (cierre de sesión en Google, equivalente a desconectar la cuenta).

---

## Módulo `normalizador_pms` (sin Blueprint)

`normalizador_pms/` es un módulo interno sin endpoints propios. Define:
- `ReservaEstandar` — dataclass que normaliza datos de reserva (nombre, email, teléfono, fechas, apartamento) independientemente del PMS origen.
- `PMSClient` — Protocol (interfaz) que deben implementar los adaptadores.
- `SmoobuReservationClient`, `Beds24ReservationClient` — adaptadores concretos.
- `build_pms_client(proveedor, api_key, endpoint)` — factory que devuelve el adaptador correcto.

Para añadir un nuevo PMS (ej. Hostaway), crear `normalizador_pms/hostaway.py` con la clase `HostawayReservationClient` y añadirla al `factory.py`.
