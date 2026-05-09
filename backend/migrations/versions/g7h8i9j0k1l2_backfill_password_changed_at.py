"""Rellena password_changed_at nulo con fecha de hace 60 días para forzar cambio.

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e1
Create Date: 2026-05-10

"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta, timezone

revision = "g7h8i9j0k1l2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    forced_at = datetime.now(timezone.utc) - timedelta(days=60)
    op.execute(
        sa.text(
            "UPDATE usuarios SET password_changed_at = :ts WHERE password_changed_at IS NULL"
        ).bindparams(ts=forced_at)
    )


def downgrade() -> None:
    # No revertimos: poner NULL de vuelta rompería la lógica de caducidad
    pass
