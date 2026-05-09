"""Modelos del sincronizador de contactos: tokens OAuth Google y logs de auditoría."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db

# Orígenes de sincronización registrables
ORIGEN_PMS = "pms"
ORIGEN_GOOGLE_CONTACTS = "google_contacts"
ORIGEN_XLSX = "xlsx"

# Estados posibles de una sincronización
ESTADO_EXITO = "exito"
ESTADO_ERROR = "error"
ESTADO_PARCIAL = "parcial"


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


class LogSincronizacion(db.Model):
    """Registro de auditoría de accesos a APIs externas y procesos de sincronización.

    Permite trazar cuándo, quién y con qué resultado se realizaron
    sincronizaciones con el PMS, Google Contacts o importaciones XLSX."""

    __tablename__ = "logs_sincronizacion"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Origen del proceso: 'pms' | 'google_contacts' | 'xlsx' | 'heatmap_pms'
    origen = db.Column(db.String(50), nullable=False)
    # Resultado: 'exito' | 'error' | 'parcial'
    estado = db.Column(db.String(20), nullable=False)
    # Número de registros procesados (reservas, contactos, etc.)
    num_registros = db.Column(db.Integer, nullable=True)
    # Detalle adicional: mensaje de error o resumen de la operación
    detalle = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relaciones
    empresa = db.relationship("Empresa", back_populates="logs_sincronizacion")

    def __repr__(self) -> str:
        return (
            f"<LogSincronizacion origen={self.origen!r} "
            f"estado={self.estado!r} registros={self.num_registros}>"
        )
