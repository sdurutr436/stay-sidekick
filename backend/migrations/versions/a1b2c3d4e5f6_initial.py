"""Creación inicial del esquema completo de Stay Sidekick.

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-04-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ── empresas ──────────────────────────────────────────────────────────────
    op.create_table(
        "empresas",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("ciudad", sa.String(100), nullable=True),
        sa.Column(
            "herramientas_activas",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "configuracion",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # ── usuarios ──────────────────────────────────────────────────────────────
    op.create_table(
        "usuarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(
        op.f("ix_usuarios_empresa_id"), "usuarios", ["empresa_id"], unique=False
    )

    # ── apartamentos ──────────────────────────────────────────────────────────
    op.create_table(
        "apartamentos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("id_externo", sa.String(100), nullable=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("direccion", sa.String(300), nullable=True),
        sa.Column("ciudad", sa.String(100), nullable=True),
        sa.Column("pms_origen", sa.String(50), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "empresa_id", "id_externo", name="uq_apartamento_empresa_id_externo"
        ),
    )
    op.create_index(
        op.f("ix_apartamentos_empresa_id"), "apartamentos", ["empresa_id"], unique=False
    )

    # ── plantillas_vault ──────────────────────────────────────────────────────
    op.create_table(
        "plantillas_vault",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("idioma", sa.String(10), nullable=False),
        sa.Column("categoria", sa.String(50), nullable=True),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_plantillas_vault_empresa_id"),
        "plantillas_vault",
        ["empresa_id"],
        unique=False,
    )

    # ── mensajes_generados ────────────────────────────────────────────────────
    op.create_table(
        "mensajes_generados",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plantilla_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("contenido_final", sa.Text(), nullable=False),
        sa.Column("modelo_ia", sa.String(100), nullable=True),
        sa.Column(
            "metadatos", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["plantilla_id"], ["plantillas_vault.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mensajes_generados_empresa_id"),
        "mensajes_generados",
        ["empresa_id"],
        unique=False,
    )

    # ── configuracion_pms ─────────────────────────────────────────────────────
    op.create_table(
        "configuracion_pms",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("proveedor", sa.String(50), nullable=False),
        sa.Column("api_key_cifrada", sa.Text(), nullable=True),
        sa.Column("endpoint", sa.String(500), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("ultimo_sync", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id"),
    )

    # ── integraciones_google ──────────────────────────────────────────────────
    op.create_table(
        "integraciones_google",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("access_token_cifrado", sa.Text(), nullable=True),
        sa.Column("refresh_token_cifrado", sa.Text(), nullable=False),
        sa.Column("token_expiry", sa.DateTime(timezone=True), nullable=True),
        sa.Column("alcance", sa.Text(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id"),
    )

    # ── configuracion_ia ──────────────────────────────────────────────────────
    op.create_table(
        "configuracion_ia",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("proveedor", sa.String(50), nullable=False),
        sa.Column("api_key_cifrada", sa.Text(), nullable=True),
        sa.Column("modelo", sa.String(100), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id"),
    )

    # ── logs_sincronizacion ───────────────────────────────────────────────────
    op.create_table(
        "logs_sincronizacion",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("origen", sa.String(50), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False),
        sa.Column("num_registros", sa.Integer(), nullable=True),
        sa.Column("detalle", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_logs_sincronizacion_empresa_id"),
        "logs_sincronizacion",
        ["empresa_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_logs_sincronizacion_created_at"),
        "logs_sincronizacion",
        ["created_at"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_logs_sincronizacion_created_at"), table_name="logs_sincronizacion"
    )
    op.drop_index(
        op.f("ix_logs_sincronizacion_empresa_id"), table_name="logs_sincronizacion"
    )
    op.drop_table("logs_sincronizacion")
    op.drop_table("configuracion_ia")
    op.drop_table("integraciones_google")
    op.drop_table("configuracion_pms")
    op.drop_index(
        op.f("ix_mensajes_generados_empresa_id"), table_name="mensajes_generados"
    )
    op.drop_table("mensajes_generados")
    op.drop_index(
        op.f("ix_plantillas_vault_empresa_id"), table_name="plantillas_vault"
    )
    op.drop_table("plantillas_vault")
    op.drop_index(op.f("ix_apartamentos_empresa_id"), table_name="apartamentos")
    op.drop_table("apartamentos")
    op.drop_index(op.f("ix_usuarios_empresa_id"), table_name="usuarios")
    op.drop_table("usuarios")
    op.drop_table("empresas")
