# 5. Diseno

## Indice

- [5.1. Diagrama entidad-relacion](#51-diagrama-entidad-relacion)
  - [Entidades y atributos principales](#entidades-y-atributos-principales)
  - [Relaciones](#relaciones)
- [5.2. Diagrama de casos de uso](#52-diagrama-de-casos-de-uso)
- [5.3. Diagramas de flujo de los procesos principales](#53-diagramas-de-flujo-de-los-procesos-principales)
  - [Flujo 1 - Inicio de sesion](#flujo-1---inicio-de-sesion)
  - [Flujo 2 - Sincronizar apartamentos desde PMS](#flujo-2---sincronizar-apartamentos-desde-pms)
  - [Flujo 3 - Importar apartamentos desde XLSX](#flujo-3---importar-apartamentos-desde-xlsx)
  - [Flujo 4 - Generar mapa de calor](#flujo-4---generar-mapa-de-calor)
  - [Flujo 5 - Sincronizar contactos con Google](#flujo-5---sincronizar-contactos-con-google)
  - [Flujo 6 - Mejorar plantilla en Vault con IA](#flujo-6---mejorar-plantilla-en-vault-con-ia)
- [5.4. Arquitectura de la aplicacion](#54-arquitectura-de-la-aplicacion)
  - [Vision general](#vision-general)
  - [Capa frontend](#capa-frontend)
  - [Capa backend](#capa-backend)
  - [Capa de datos](#capa-de-datos)
  - [Integraciones externas](#integraciones-externas)
- [5.5. Diseno de la API](#55-diseno-de-la-api)
  - [Convenciones generales](#convenciones-generales)
  - [Modulos de endpoints](#modulos-de-endpoints)
  - [Ejemplos de respuestas](#ejemplos-de-respuestas)

---

## 5.1. Diagrama entidad-relacion

El modelo de datos esta orientado a multiempresa. Cada empresa dispone de su propio espacio de configuracion, usuarios, apartamentos, plantillas e integraciones, con aislamiento logico por `empresa_id`.

```mermaid
erDiagram
    EMPRESAS ||--o{ USUARIOS : tiene
    EMPRESAS ||--o{ APARTAMENTOS : gestiona
    EMPRESAS ||--o{ PLANTILLAS_VAULT : define
    EMPRESAS ||--o{ MENSAJES_GENERADOS : registra
    EMPRESAS ||--o{ AI_USAGE_LOG : acumula
    EMPRESAS ||--o{ LOGS_SINCRONIZACION : audita
    EMPRESAS ||--o{ CONFIGURACION_PMS : configura
    EMPRESAS ||--o{ CONFIGURACION_IA : configura
    EMPRESAS ||--o{ INTEGRACIONES_GOOGLE : conecta

    PLANTILLAS_VAULT ||--o{ MENSAJES_GENERADOS : origen

    EMPRESAS {
      string id
      string nombre
      string email
      string password_hash
      string herramientas_activas
      string configuracion
      string activa
      string created_at
      string updated_at
    }

    USUARIOS {
      string id
      string empresa_id
      string email
      string password_hash
      string rol
      string activo
      string es_superadmin
      string created_at
      string updated_at
    }

    APARTAMENTOS {
      string id
      string empresa_id
      string id_pms
      string id_externo
      string nombre
      string direccion
      string ciudad
      string pms_origen
      string activo
      string created_at
      string updated_at
    }

    CONFIGURACION_PMS {
      string id
      string empresa_id
      string proveedor
      text api_key_cifrada
      string endpoint
      string activo
      string ultimo_sync
    }

    INTEGRACIONES_GOOGLE {
      string id
      string empresa_id
      text access_token_cifrado
      text refresh_token_cifrado
      string token_expiry
      text alcance
      string activo
    }

    CONFIGURACION_IA {
      string id
      string empresa_id
      string proveedor
      text api_key_cifrada
      string modelo
      string activo
    }

    PLANTILLAS_VAULT {
      string id
      string empresa_id
      string nombre
      text contenido
      string idioma
      string categoria
      string activa
    }

    MENSAJES_GENERADOS {
      string id
      string empresa_id
      string plantilla_id
      text contenido_final
      string modelo_ia
      string metadatos
      string created_at
    }

    LOGS_SINCRONIZACION {
      string id
      string empresa_id
      string origen
      string estado
      int num_registros
      text detalle
      string created_at
    }

    AI_USAGE_LOG {
      string id
      string empresa_id
      string accion
      date fecha
      int tokens_usados
    }
```

### Entidades y atributos principales

- `empresas`: cuenta principal por cliente, activacion de herramientas y configuracion operativa.
- `usuarios`: miembros de equipo con roles `admin` u `operativo`; soporta `es_superadmin`.
- `apartamentos`: maestro de alojamientos con origen (`smoobu`, `beds24`, `manual`, `xlsx`).
- `configuracion_pms`: proveedor y credenciales cifradas del PMS por empresa.
- `integraciones_google`: tokens OAuth cifrados para sincronizacion de contactos.
- `configuracion_ia`: proveedor/modelo y API key BYOK cifrada.
- `plantillas_vault`: biblioteca de mensajes reutilizables por categoria e idioma.
- `mensajes_generados`: trazabilidad de resultados de IA sobre plantillas.
- `logs_sincronizacion`: auditoria de procesos de sincronizacion.
- `ai_usage_log`: consumo diario de IA para control de cuotas.

### Relaciones

- Una empresa tiene N usuarios, N apartamentos, N plantillas y N logs.
- Una empresa tiene 0..1 configuracion PMS, 0..1 configuracion IA y 0..1 integracion Google.
- Una plantilla puede originar N mensajes generados.
- Todas las tablas funcionales usan `empresa_id` para aislamiento multi-tenant.

---

## 5.2. Diagrama de casos de uso

```mermaid
flowchart LR
    OP[Usuario operativo]
    AD[Admin empresa]
    SA[Superadmin]
    EXT[Servicios externos\nSmoobu - Google - IA]

    subgraph SYS[Stay Sidekick]
      UC1[Iniciar sesion]
      UC2[Gestionar perfil y password]
      UC3[Gestionar usuarios]
      UC4[Alta/edicion de apartamentos]
      UC5[Sincronizar apartamentos PMS]
      UC6[Importar apartamentos XLSX]
      UC7[Generar mapa de calor]
      UC8[Configurar umbrales y columnas XLSX]
      UC9[Sincronizar contactos con Google]
      UC10[Exportar contactos a CSV]
      UC11[Gestionar plantillas check-in tardio]
      UC12[Gestionar vault de comunicaciones]
      UC13[Mejorar/traducir con IA]
      UC14[Gestionar empresas]
    end

    OP --> UC1
    OP --> UC2
    OP --> UC4
    OP --> UC6
    OP --> UC7
    OP --> UC9
    OP --> UC10
    OP --> UC11
    OP --> UC12
    OP --> UC13

    AD --> UC3
    AD --> UC5
    AD --> UC8
    AD --> UC9
    AD --> UC11
    AD --> UC12

    SA --> UC14
    SA --> UC3

    EXT -.-> UC5
    EXT -.-> UC9
    EXT -.-> UC13
```

Actores principales:

- Usuario operativo: usa herramientas diarias del panel.
- Admin de empresa: administra equipo, integraciones y configuraciones.
- Superadmin: administra empresas y operaciones globales.
- Servicios externos: PMS, Google Contacts y proveedor de IA.

---

## 5.3. Diagramas de flujo de los procesos principales

### Flujo 1 - Inicio de sesion

```mermaid
flowchart TD
    A[Usuario envia email/password] --> B[GET csrf-token]
    B --> C[POST /api/auth/login]
    C --> D{Credenciales validas}
    D -- No --> E[401 error]
    D -- Si --> F[Emitir JWT]
    F --> G[Guardar sesion en frontend]
    G --> H[Consumir API autenticada]
```

### Flujo 2 - Sincronizar apartamentos desde PMS

```mermaid
flowchart TD
    A[Admin pulsa sincronizar] --> B[POST /api/apartamentos/sincronizacion/smoobu]
    B --> C[Leer configuracion_pms]
    C --> D[Llamar API PMS]
    D --> E[Normalizar payload]
    E --> F[Upsert en apartamentos]
    F --> G[Registrar logs_sincronizacion]
    G --> H[Devolver resumen]
```

### Flujo 3 - Importar apartamentos desde XLSX

```mermaid
flowchart TD
    A[Usuario sube XLSX] --> B[POST /api/apartamentos/importacion/preview]
    B --> C[Validar extension y tamano]
    C --> D[Parsear columnas configuradas]
    D --> E[Mostrar preview]
    E --> F[POST /api/apartamentos/importacion]
    F --> G[Normalizar + upsert]
    G --> H[Resultado con warnings opcionales]
```

### Flujo 4 - Generar mapa de calor

```mermaid
flowchart TD
    A[Usuario define desde/hasta] --> B{Origen de datos}
    B -- PMS --> C[GET /api/heatmap]
    B -- XLSX --> D[POST /api/heatmap/xlsx]
    C --> E[Calcular checkins/checkouts por dia]
    D --> E
    E --> F[Aplicar umbrales de intensidad]
    F --> G[Render calendario de carga]
```

### Flujo 5 - Sincronizar contactos con Google

```mermaid
flowchart TD
    A[Admin conecta Google] --> B[GET /api/contactos/google/auth]
    B --> C[OAuth callback]
    C --> D[Guardar tokens cifrados]
    D --> E[POST /api/contactos/sincronizacion]
    E --> F[Leer reservas PMS o XLSX]
    F --> G[Generar contactos]
    G --> H[Upsert en Google People API]
    H --> I[Registrar logs_sincronizacion]
```

### Flujo 6 - Mejorar plantilla en Vault con IA

```mermaid
flowchart TD
    A[Usuario selecciona plantilla] --> B[POST /api/vault/plantillas/:id/mejoras]
    B --> C[Validar cuota AI]
    C --> D{BYOK configurado}
    D -- Si --> E[Usar api_key_cifrada empresa]
    D -- No --> F[Usar clave sistema]
    E --> G[Llamar proveedor IA]
    F --> G
    G --> H[Devolver contenido mejorado]
    H --> I[Registrar ai_usage_log]
```

---

## 5.4. Arquitectura de la aplicacion

### Vision general

La aplicacion sigue arquitectura cliente-servidor con proxy inverso y separacion por capas: sitio web publico, SPA autenticada, API backend y base de datos relacional.

```mermaid
graph TD
    U[Cliente navegador]
    N[Nginx reverse proxy]
    W[Web 11ty\nlanding y paginas publicas]
    F[Frontend Angular SPA\nmenu operativo]
    B[Backend Flask API]
    P[(PostgreSQL 16)]
    S[Smoobu API]
    G[Google People API]
    A[Proveedor IA]

    U -->|HTTP| N
    N -->|/| W
    N -->|/menu| F
    N -->|/api| B

    B --> P
    B --> S
    B --> G
    B --> A
```

### Capa frontend

- Angular SPA para zona autenticada (`/menu`).
- Sitio 11ty para contenido publico (`/`).
- Consumo API via JSON y multipart.
- Gestion de sesion con JWT y token CSRF en operaciones de escritura.

### Capa backend

- Flask con blueprints modulares (`auth`, `perfil`, `usuarios`, `empresas`, `apartamentos`, `contactos`, `notificaciones`, `vault`, `heatmap`, `contacto`).
- Seguridad: JWT, CSRF double-submit cookie, rate limiting, CORS.
- Logica de negocio por herramientas del MVP.

### Capa de datos

- PostgreSQL con UUID como claves primarias.
- Cifrado de secretos en BD mediante Fernet.
- Tablas de auditoria para sincronizaciones y uso de IA.
- Modelo preparado para multi-tenant por `empresa_id`.

### Integraciones externas

- PMS (Smoobu en MVP) para apartamentos y reservas.
- Google OAuth + People API para sincronizacion de contactos.
- Proveedor IA (Gemini/OpenAI/Claude) para mejoras y traducciones en Vault.

---

## 5.5. Diseno de la API

### Convenciones generales

- Base path: `/api`.
- Auth: `Authorization: Bearer <JWT>` en endpoints privados.
- CSRF: `X-CSRF-Token` + cookie en endpoints de escritura.
- Respuestas exitosas estandar: `{"ok": true, ...}`.
- Respuestas de error estandar: `{"ok": false, "errors": ["..."]}`.
- Codigos frecuentes: `200`, `201`, `400`, `401`, `403`, `404`, `409`, `413`, `422`, `429`, `502`, `504`.

### Modulos de endpoints

| Modulo | Endpoints principales |
|---|---|
| Salud y docs | `GET /api/health`, `GET /api/docs`, `GET /api/docs/openapi.yaml` |
| Autenticacion | `GET /api/csrf-token`, `POST /api/auth/login`, `GET /api/auth/validacion` |
| Perfil e integraciones | `GET /api/perfil`, `PUT /api/perfil/password`, `GET/PUT/DELETE /api/perfil/integraciones/*` |
| Empresas | `GET/POST /api/empresas` (superadmin) |
| Usuarios | `GET/POST /api/usuarios`, `PATCH/DELETE /api/usuarios/:id` |
| Maestro apartamentos | `GET/POST/PUT/DELETE /api/apartamentos`, `POST /api/apartamentos/sincronizacion/smoobu`, importacion XLSX |
| Contactos | OAuth Google, preferencias, sincronizacion y export CSV (`/api/contactos/*`) |
| Notificaciones tardias | `GET /status`, `POST /checkins`, CRUD de plantillas check-in tardio |
| Vault comunicaciones | CRUD plantillas, `mejoras`, `traducciones`, uso y config IA |
| Mapa de calor | `GET /api/heatmap`, `POST /api/heatmap/xlsx`, `GET/PUT /umbrales`, `GET/PUT /config-xlsx` |
| Contacto publico | `POST /api/contacto`, `POST /api/contact` |

### Ejemplos de respuestas

Login correcto:

```json
{
  "ok": true,
  "token": "<jwt>",
  "debe_cambiar_password": false
}
```

Validacion fallida:

```json
{
  "ok": false,
  "errors": [
    "El campo email es obligatorio."
  ]
}
```

Respuesta tipica de modulo:

```json
{
  "ok": true,
  "resultado": {
    "creados": 12,
    "actualizados": 7,
    "omitidos": 1
  }
}
```
