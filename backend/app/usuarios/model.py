"""Modelo de usuario perteneciente a una empresa."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db

# Roles disponibles dentro de una empresa
ROL_ADMIN = "admin"
ROL_OPERATIVO = "operativo"
ROLES_VALIDOS = (ROL_ADMIN, ROL_OPERATIVO)


class Usuario(db.Model):
    """Usuario de la plataforma vinculado a una empresa.

    Un usuario admin puede gestionar la configuración de la empresa;
    un usuario operativo solo accede a las herramientas."""

    __tablename__ = "usuarios"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email = db.Column(db.String(254), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)  # bcrypt
    rol = db.Column(db.String(20), nullable=False, default=ROL_OPERATIVO)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    password_changed_at = db.Column(db.DateTime(timezone=True), nullable=True)
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
    empresa = db.relationship("Empresa", back_populates="usuarios")

    def __repr__(self) -> str:
        return f"<Usuario {self.email!r} rol={self.rol}>"
