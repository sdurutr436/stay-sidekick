"""Modelo de empresa (cliente de la plataforma)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db


class Empresa(db.Model):
    """Cuenta de empresa. Centraliza autenticación, configuración de herramientas
    activas y preferencias operativas propias de cada cliente."""

    __tablename__ = "empresas"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)  # bcrypt
    ciudad = db.Column(db.String(100), nullable=True)

    herramientas_activas = db.Column(JSONB, nullable=False, default=dict)  # {heatmap, late_checkin, google_contacts, vault} → bool
    configuracion = db.Column(JSONB, nullable=False, default=dict)  # hora_limite_checkin_tardio, idioma_defecto, max_usuarios, etc.

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
    usuarios = db.relationship("Usuario", back_populates="empresa", cascade="all, delete-orphan")
    apartamentos = db.relationship("Apartamento", back_populates="empresa", cascade="all, delete-orphan")
    plantillas_vault = db.relationship("PlantillaVault", back_populates="empresa", cascade="all, delete-orphan")
    mensajes_generados = db.relationship("MensajeGenerado", back_populates="empresa", cascade="all, delete-orphan")
    configuracion_pms = db.relationship("ConfiguracionPMS", back_populates="empresa", uselist=False, cascade="all, delete-orphan")
    integracion_google = db.relationship("IntegracionGoogle", back_populates="empresa", uselist=False, cascade="all, delete-orphan")
    configuracion_ia = db.relationship("ConfiguracionIA", back_populates="empresa", uselist=False, cascade="all, delete-orphan")
    logs_sincronizacion = db.relationship("LogSincronizacion", back_populates="empresa", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Empresa {self.nombre!r} ({self.email})>"
