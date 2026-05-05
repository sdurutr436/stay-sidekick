"""Añade tablas ai_usage_log y system_prompts.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ai_usage_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("accion", sa.String(20), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("tokens_usados", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_ai_usage_log_empresa_id_fecha",
        "ai_usage_log",
        ["empresa_id", "fecha"],
        unique=False,
    )

    op.create_table(
        "system_prompts",
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("nombre"),
    )


def downgrade():
    op.drop_table("system_prompts")
    op.drop_index("ix_ai_usage_log_empresa_id_fecha", table_name="ai_usage_log")
    op.drop_table("ai_usage_log")
