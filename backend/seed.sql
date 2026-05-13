-- =============================================================================
-- Seed de datos iniciales — Stay Sidekick
--
-- Crea una empresa demo y un usuario superadmin para desarrollo local:
--   · dev@staysidekick.es / admin123   → acceso local y tribunal
--
-- Uso:
--   En local con Docker:
--     docker compose exec postgres psql -U postgres -d stay_sidekick -f /seed.sql
--   Para aplicar en Railway (Data → Query): pegar y ejecutar.
--
-- Los hashes han sido generados con bcrypt (12 rounds) desde Python.
-- ON CONFLICT DO NOTHING hace el script idempotente (seguro de re-ejecutar).
-- =============================================================================

BEGIN;

-- ── Empresa demo ─────────────────────────────────────────────────────────────
INSERT INTO empresas (
    id,
    nombre,
    email,
    password_hash,
    ciudad,
    herramientas_activas,
    configuracion,
    activa,
    created_at,
    updated_at
) VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'StaySidekick Demo',
    'demo@staysidekick.es',
    -- hash bcrypt 12 rounds
    '$2b$12$G.zZBIf63HD/CbMKwkpMheaf0wrd3uJ4AjRF0uFqhg2yQ3pAUUGCy',
    'Sevilla',
    '{"heatmap": true, "late_checkin": true, "google_contacts": true, "vault": true}',
    '{}',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- ── Usuario: dev / admin (acceso local y tribunal) ───────────────────────────
INSERT INTO usuarios (
    id,
    empresa_id,
    email,
    password_hash,
    rol,
    es_superadmin,
    activo,
    created_at,
    updated_at
) VALUES (
    'c3d4e5f6-a7b8-9012-cdef-123456789012',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'dev@staysidekick.es',
    -- hash bcrypt 12 rounds de 'admin123'
    '$2b$12$9yMylH3GVqBLl6dKYumcx.JvFYCCTbwtgeruUo4aASCZRIZ/Vzu5G',
    'admin',
    true,
    true,
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

COMMIT;
