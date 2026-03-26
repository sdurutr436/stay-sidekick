-- =============================================================================
-- Stay Sidekick — Esquema de base de datos PostgreSQL
-- =============================================================================
-- Cómo ejecutarlo:
--   psql -d <nombre_bd> -f schema.sql
--   O pegar directamente en el editor SQL de Supabase / Railway.
--
-- Compatible con: PostgreSQL 15+, Supabase, Railway
-- =============================================================================

-- Extensión para generación de UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- TABLA: empresas
-- Cuenta principal de cada cliente de la plataforma.
-- Centraliza autenticación, herramientas activas y configuración operativa.
-- =============================================================================
CREATE TABLE IF NOT EXISTS empresas (
    id                   UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre               VARCHAR(200) NOT NULL,
    email                VARCHAR(254) NOT NULL UNIQUE,
    password_hash        VARCHAR(255) NOT NULL,   -- bcrypt

    ciudad               VARCHAR(100),

    -- Herramientas activas por empresa (se activan/desactivan desde el panel).
    -- Estructura esperada: {"heatmap": true, "late_checkin": true,
    --                       "google_contacts": false, "vault": true}
    herramientas_activas JSONB        NOT NULL DEFAULT '{}'::JSONB,

    -- Configuración operativa parametrizable por empresa.
    -- Estructura esperada: {"hora_limite_checkin": "20:00",
    --                       "idioma_defecto": "es",
    --                       "formato_nombre_contacto": "apellido_nombre"}
    configuracion        JSONB        NOT NULL DEFAULT '{}'::JSONB,

    activa               BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- TABLA: usuarios
-- Miembros adicionales del equipo de una empresa.
--
-- En el MVP solo existe la cuenta de empresa (relación 1:1 con empresas).
-- Esta tabla está preparada para gestión de equipos en versiones futuras,
-- cuando el admin quiera dar acceso a recepcionistas o coordinadores sin
-- compartir la contraseña maestra.
--
-- Roles:
--   admin     → acceso completo: configura herramientas, integraciones,
--               plantillas y apartamentos. En el MVP es la cuenta de empresa.
--   operativo → acceso a herramientas del panel únicamente (heatmap, vault,
--               notificaciones). No puede tocar configuración de la empresa.
-- =============================================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id            UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id    UUID         NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    email         VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,          -- bcrypt
    rol           VARCHAR(20)  NOT NULL DEFAULT 'operativo'
                      CHECK (rol IN ('admin', 'operativo')),
    activo        BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usuarios_empresa_id ON usuarios(empresa_id);

-- =============================================================================
-- TABLA: apartamentos
-- Maestro de alojamientos gestionado por cada empresa.
--
-- Los campos son fijos y normalizados. Independientemente del origen
-- (llamada a API del PMS, importación XLSX o alta manual), el backend
-- construye un payload normalizado antes de insertar: identifica las columnas
-- del XLSX por cabecera (no por posición), resuelve ambigüedades y mapea
-- los datos a esta estructura estándar.
--
-- No contiene datos personales de huéspedes (cumplimiento RGPD).
-- =============================================================================
CREATE TABLE IF NOT EXISTS apartamentos (
    id          UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id  UUID         NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,

    -- ID del alojamiento en el PMS externo. NULL si se creó manualmente.
    id_externo  VARCHAR(100),

    nombre      VARCHAR(200) NOT NULL,
    direccion   VARCHAR(300),
    ciudad      VARCHAR(100),

    -- Origen del alta: API del PMS, importación XLSX o alta manual.
    pms_origen  VARCHAR(50)  CHECK (pms_origen IN ('smoobu', 'beds24', 'manual', 'xlsx')),

    activo      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    -- Una empresa no puede tener dos alojamientos con el mismo ID externo.
    CONSTRAINT uq_apartamento_empresa_id_externo UNIQUE (empresa_id, id_externo)
);

CREATE INDEX IF NOT EXISTS idx_apartamentos_empresa_id ON apartamentos(empresa_id);

-- =============================================================================
-- TABLA: plantillas_vault
-- Biblioteca centralizada de plantillas de mensajes por empresa.
--
-- Sustituye las respuestas rápidas dispersas en dispositivos personales.
-- El campo `contenido` puede incluir placeholders que el usuario rellena
-- manualmente antes de enviar: {NOMBRE}, {APARTAMENTO}, {HORA_LLEGADA},
-- {IDIOMA}, {PROTOCOLO_CHECKIN}, etc.
--
-- La IA (herramienta Vault) trabaja sobre estas plantillas para ajustar tono,
-- traducir o generar variaciones, pero no inventa contenido desde cero.
-- =============================================================================
CREATE TABLE IF NOT EXISTS plantillas_vault (
    id         UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID         NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    nombre     VARCHAR(200) NOT NULL,
    contenido  TEXT         NOT NULL,    -- Cuerpo con placeholders: {NOMBRE}, {HORA_LLEGADA}...
    idioma     VARCHAR(10)  NOT NULL DEFAULT 'es',

    -- Categoría semántica para filtrar en el panel.
    -- Ejemplos: 'checkin_tardio', 'bienvenida', 'instrucciones', 'protocolo'
    categoria  VARCHAR(50),

    activa     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_plantillas_vault_empresa_id ON plantillas_vault(empresa_id);

-- =============================================================================
-- TABLA: mensajes_generados
-- Registro de mensajes generados por IA a partir de una plantilla.
--
-- NO almacena ningún dato de huéspedes ni referencia a reservas.
-- Los datos de contexto opcionales (reserva, destinatario) que el frontend
-- puede enviar se usan en memoria durante la generación y se descartan
-- sin persistirse. El resultado final lo copia y envía el usuario por el
-- canal que utilice (WhatsApp, email, SMS).
-- =============================================================================
CREATE TABLE IF NOT EXISTS mensajes_generados (
    id              UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id      UUID         NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    plantilla_id    UUID         REFERENCES plantillas_vault(id) ON DELETE SET NULL,
    contenido_final TEXT         NOT NULL,

    -- Modelo de IA que generó el mensaje.
    -- Ejemplos: 'gemini-2.0-flash', 'gpt-4o', 'claude-3-5-sonnet'
    modelo_ia       VARCHAR(100),

    -- Parámetros de generación usados (tono, idioma destino, variación, etc.).
    -- No incluye datos de huéspedes.
    metadatos       JSONB,

    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mensajes_generados_empresa_id  ON mensajes_generados(empresa_id);
CREATE INDEX IF NOT EXISTS idx_mensajes_generados_plantilla_id ON mensajes_generados(plantilla_id);

-- =============================================================================
-- TABLA: configuracion_pms
-- Credenciales cifradas de la integración con el PMS de cada empresa.
--
-- Una empresa tiene como máximo un PMS activo a la vez.
-- La api_key se cifra con Fernet (cryptography) antes de persistirse.
-- El campo `proveedor` determina qué adaptador de normalización usa el backend.
-- =============================================================================
CREATE TABLE IF NOT EXISTS configuracion_pms (
    id              UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id      UUID         NOT NULL UNIQUE REFERENCES empresas(id) ON DELETE CASCADE,
    proveedor       VARCHAR(50)  NOT NULL
                        CHECK (proveedor IN ('smoobu', 'beds24', 'hostaway', 'cloudbeds')),

    -- API key cifrada con Fernet. NULL hasta que la empresa configure la integración.
    api_key_cifrada TEXT,

    -- Endpoint base del PMS si es configurable (algunos lo tienen fijo en el adaptador).
    endpoint        VARCHAR(500),

    activo          BOOLEAN      NOT NULL DEFAULT TRUE,
    ultimo_sync     TIMESTAMPTZ,                 -- Fecha de la última sincronización exitosa
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- TABLA: integraciones_google
-- Tokens OAuth 2.0 de Google People API por empresa.
--
-- El flujo: la empresa conecta su cuenta Google desde el panel (OAuth 2.0),
-- el backend recibe el código de autorización, lo intercambia por tokens y
-- los guarda cifrados con Fernet. El refresh_token permite renovar el
-- access_token sin nueva autenticación manual.
-- =============================================================================
CREATE TABLE IF NOT EXISTS integraciones_google (
    id                    UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id            UUID         NOT NULL UNIQUE REFERENCES empresas(id) ON DELETE CASCADE,

    -- Tokens cifrados con Fernet.
    access_token_cifrado  TEXT,                  -- NULL hasta el primer refresh
    refresh_token_cifrado TEXT         NOT NULL,

    token_expiry          TIMESTAMPTZ,           -- Expiración del access_token
    alcance               TEXT         NOT NULL, -- Scopes OAuth concedidos (separados por espacio)
    activo                BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- TABLA: configuracion_ia
-- Proveedor y modelo de IA por empresa (BYOK — Bring Your Own Key).
--
-- Si api_key_cifrada es NULL, el sistema usa la clave Gemini 2.0 Flash
-- del proyecto (free tier, cuota compartida). Si la empresa configura BYOK,
-- la clave se cifra con Fernet antes de persistirse.
--
-- Proveedores soportados: Gemini, OpenAI, Claude, o 'default' (sistema).
-- =============================================================================
CREATE TABLE IF NOT EXISTS configuracion_ia (
    id              UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id      UUID         NOT NULL UNIQUE REFERENCES empresas(id) ON DELETE CASCADE,
    proveedor       VARCHAR(50)  NOT NULL DEFAULT 'default'
                        CHECK (proveedor IN ('default', 'gemini', 'openai', 'claude')),

    -- BYOK: API key propia cifrada con Fernet.
    -- NULL = el sistema usa la clave Gemini compartida del proyecto.
    api_key_cifrada TEXT,

    -- Modelo concreto a usar con el proveedor seleccionado.
    -- Ejemplos: 'gemini-2.0-flash', 'gpt-4o', 'claude-3-5-sonnet-20241022'
    modelo          VARCHAR(100),

    activo          BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- TABLA: logs_sincronizacion
-- Auditoría de operaciones de sincronización con servicios externos.
--
-- Registra cada operación: cuándo ocurrió, qué empresa la ejecutó, qué
-- servicio estaba involucrado, si fue bien o mal y cuántos registros procesó.
--
-- Útil para:
--   - Mostrar al usuario "última sync hace 2 horas, 47 reservas importadas"
--   - Depurar errores de integración con PMS o Google
--   - Auditoría RGPD: trazabilidad de cuándo se accedió a servicios externos
-- =============================================================================
CREATE TABLE IF NOT EXISTS logs_sincronizacion (
    id            UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id    UUID         NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,

    -- Servicio con el que se sincronizó.
    origen        VARCHAR(50)  NOT NULL CHECK (origen IN ('pms', 'google_contacts', 'xlsx')),

    -- Resultado de la operación.
    estado        VARCHAR(20)  NOT NULL CHECK (estado IN ('exito', 'error', 'parcial')),

    -- Número de registros procesados (reservas obtenidas, contactos subidos, etc.).
    num_registros INTEGER,

    -- Detalle adicional: mensaje de error o resumen de la operación.
    detalle       TEXT,

    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_logs_sincronizacion_empresa_id ON logs_sincronizacion(empresa_id);
CREATE INDEX IF NOT EXISTS idx_logs_sincronizacion_created_at ON logs_sincronizacion(created_at DESC);
