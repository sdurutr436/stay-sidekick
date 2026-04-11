-- =============================================================================
-- Seed de datos iniciales — Stay Sidekick
--
-- Crea una empresa demo y dos usuarios administradores:
--   · duran.utrerasergio2612@gmail.com  → autor del TFG (Sergio)
--   · admin@staysidekick.es             → acceso para el tribunal
--
-- Uso:
--   En Railway (Data → Query):
--     Pegar este contenido y ejecutar.
--   En local con Docker:
--     docker compose exec postgres psql -U postgres -d stay_sidekick -f /seed.sql
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

-- ── Usuario: Sergio (autor del TFG) ──────────────────────────────────────────
INSERT INTO usuarios (
    id,
    empresa_id,
    email,
    password_hash,
    rol,
    activo,
    created_at,
    updated_at
) VALUES (
    'b2c3d4e5-f6a7-8901-bcde-f12345678901',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'duran.utrerasergio2612@gmail.com',
    -- hash bcrypt 12 rounds
    '$2b$12$G.zZBIf63HD/CbMKwkpMheaf0wrd3uJ4AjRF0uFqhg2yQ3pAUUGCy',
    'admin',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- ── Usuario: admin (acceso tribunal / profesores) ─────────────────────────────
INSERT INTO usuarios (
    id,
    empresa_id,
    email,
    password_hash,
    rol,
    activo,
    created_at,
    updated_at
) VALUES (
    'c3d4e5f6-a7b8-9012-cdef-123456789012',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'admin@staysidekick.es',
    -- hash bcrypt 12 rounds
    '$2b$12$zIGSXQ6ppzYAPz2T7Gbm9e.kaxF4yKKHWdLNUwAaamY1jlM3XJRzy',
    'admin',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

COMMIT;
