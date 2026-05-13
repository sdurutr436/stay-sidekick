-- Sello Alembic para entorno Docker local.
--
-- El schema.sql crea las tablas sin pasar por Alembic, por lo que
-- el registro de versiones está vacío y flask db upgrade falla con
-- DuplicateTable al intentar crear las tablas de nuevo.
--
-- Este script se ejecuta en initdb.d DESPUÉS de schema.sql (orden alfabético
-- stamp_alembic > schema) y marca la migración inicial como ya aplicada,
-- de forma que flask db upgrade solo ejecute migraciones posteriores.

CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    PRIMARY KEY (version_num)
);

INSERT INTO alembic_version (version_num)
VALUES ('g7h8i9j0k1l2')
ON CONFLICT DO NOTHING;
