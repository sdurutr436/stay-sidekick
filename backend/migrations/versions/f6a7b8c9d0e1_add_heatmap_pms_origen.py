"""Añade heatmap_pms al check constraint de origen en logs_sincronizacion.

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-05-09

"""
from alembic import op

revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("logs_sincronizacion_origen_check", "logs_sincronizacion")
    op.create_check_constraint(
        "logs_sincronizacion_origen_check",
        "logs_sincronizacion",
        "origen IN ('pms', 'google_contacts', 'xlsx', 'heatmap_pms')",
    )


def downgrade():
    op.drop_constraint("logs_sincronizacion_origen_check", "logs_sincronizacion")
    op.create_check_constraint(
        "logs_sincronizacion_origen_check",
        "logs_sincronizacion",
        "origen IN ('pms', 'google_contacts', 'xlsx')",
    )
