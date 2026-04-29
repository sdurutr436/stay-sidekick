"""Añadir id_pms a apartamentos y cambiar constraint de unicidad.

id_pms es el ID del apartamento en el PMS externo (columna 1 del XLSX).
id_externo pasa a ser el código de tipología (puede compartirse entre varios
apartamentos del mismo tipo); se elimina el UNIQUE sobre él.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-30

"""
from alembic import op
import sqlalchemy as sa

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade():
    # Añadir columna id_pms (nullable)
    op.add_column("apartamentos", sa.Column("id_pms", sa.String(100), nullable=True))

    # Poblar id_pms con el valor actual de id_externo para filas existentes
    op.execute("UPDATE apartamentos SET id_pms = id_externo WHERE id_pms IS NULL")

    # Eliminar el UNIQUE anterior (empresa_id, id_externo)
    op.drop_constraint("uq_apartamento_empresa_id_externo", "apartamentos", type_="unique")

    # Nuevo índice parcial único sobre (empresa_id, id_pms) para filas no nulas
    op.create_index(
        "uq_apartamento_empresa_id_pms",
        "apartamentos",
        ["empresa_id", "id_pms"],
        unique=True,
        postgresql_where=sa.text("id_pms IS NOT NULL"),
    )


def downgrade():
    op.drop_index("uq_apartamento_empresa_id_pms", table_name="apartamentos")
    op.drop_column("apartamentos", "id_pms")
    op.create_unique_constraint(
        "uq_apartamento_empresa_id_externo", "apartamentos", ["empresa_id", "id_externo"]
    )
