"""Modelos del Vault de comunicaciones: plantillas y mensajes generados."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db


class PlantillaVault(db.Model):
    """Plantilla de mensaje almacenada en el Vault de cada empresa.

    El campo `contenido` puede incluir placeholders como {NOMBRE},
    {APARTAMENTO}, {HORA_LLEGADA}, {IDIOMA}, {PROTOCOLO_CHECKIN}."""

    __tablename__ = "plantillas_vault"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nombre = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    idioma = db.Column(db.String(10), nullable=False, default="es")
    # Categoría semántica: 'checkin_tardio' | 'bienvenida' | 'instrucciones' | etc.
    categoria = db.Column(db.String(50), nullable=True)
    activa = db.Column(db.Boolean, nullable=False, default=True)
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
    empresa = db.relationship("Empresa", back_populates="plantillas_vault")
    mensajes_generados = db.relationship(
        "MensajeGenerado",
        back_populates="plantilla",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<PlantillaVault {self.nombre!r} idioma={self.idioma}>"


class MensajeGenerado(db.Model):
    """Registro de mensajes generados por IA a partir de una plantilla.

    No almacena datos personales de huéspedes. La reserva se referencia
    únicamente por su ID externo del PMS (sin nombre, email ni teléfono)."""

    __tablename__ = "mensajes_generados"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plantilla_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("plantillas_vault.id", ondelete="SET NULL"),
        nullable=True,
    )
    # ID de la reserva en el PMS. No se persiste ningún dato personal del huésped.
    reserva_id_externo = db.Column(db.String(100), nullable=True)
    contenido_final = db.Column(db.Text, nullable=False)
    # Modelo de IA utilizado: 'gemini-2.0-flash' | 'gpt-4o' | 'claude-3-5-sonnet' | etc.
    modelo_ia = db.Column(db.String(100), nullable=True)
    # Parámetros de contexto usados en la generación (tono, idioma destino, etc.)
    metadatos = db.Column(JSONB, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relaciones
    empresa = db.relationship("Empresa", back_populates="mensajes_generados")
    plantilla = db.relationship("PlantillaVault", back_populates="mensajes_generados")

    def __repr__(self) -> str:
        return f"<MensajeGenerado plantilla={self.plantilla_id} reserva={self.reserva_id_externo}>"
