"""Modelos de integraciones externas: Google OAuth."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db


class IntegracionGoogle(db.Model):
    """Tokens OAuth 2.0 de Google People API por empresa.

    Los tokens se almacenan cifrados con Fernet. El refresh_token
    permite renovar el access_token sin requerir autenticación manual."""

    __tablename__ = "integraciones_google"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,   # 1 cuenta Google por empresa
    )
    # Tokens cifrados con Fernet
    access_token_cifrado = db.Column(db.Text, nullable=True)
    refresh_token_cifrado = db.Column(db.Text, nullable=False)
    token_expiry = db.Column(db.DateTime(timezone=True), nullable=True)
    # Scopes OAuth concedidos (separados por espacio)
    alcance = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relaciones
    empresa = db.relationship("Empresa", back_populates="integracion_google")

    def __repr__(self) -> str:
        return f"<IntegracionGoogle empresa={self.empresa_id} activo={self.activo}>"
