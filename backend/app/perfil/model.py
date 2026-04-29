"""Modelos de configuración de integraciones gestionadas desde el perfil de empresa."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db

# Proveedores de PMS soportados
PMS_SMOOBU = "smoobu"
PMS_BEDS24 = "beds24"
PMS_HOSTAWAY = "hostaway"

# Proveedores de IA soportados
IA_DEFAULT = "default"   # Gemini 2.0 Flash del sistema (cuota compartida)
IA_GEMINI = "gemini"
IA_OPENAI = "openai"
IA_CLAUDE = "claude"


class ConfiguracionPMS(db.Model):
    """Configuración de la integración con el PMS de cada empresa.

    La api_key se almacena cifrada con Fernet (cryptography).
    Una empresa solo puede tener un PMS activo a la vez."""

    __tablename__ = "configuracion_pms"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,   # 1 PMS por empresa
    )
    # 'smoobu' | 'beds24' | 'hostaway' | ...
    proveedor = db.Column(db.String(50), nullable=False)
    # API key cifrada con Fernet. NULL mientras no se haya configurado.
    api_key_cifrada = db.Column(db.Text, nullable=True)
    # Endpoint base del PMS (opcional si el adaptador lo tiene hardcodeado)
    endpoint = db.Column(db.String(500), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    ultimo_sync = db.Column(db.DateTime(timezone=True), nullable=True)
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
    empresa = db.relationship("Empresa", back_populates="configuracion_pms")

    def __repr__(self) -> str:
        return f"<ConfiguracionPMS proveedor={self.proveedor!r} activo={self.activo}>"


class ConfiguracionIA(db.Model):
    """Configuración del proveedor de IA por empresa (BYOK).

    Si api_key_cifrada es NULL, el sistema usa la clave Gemini compartida
    del proyecto (free tier). Si se configura BYOK, la clave se cifra con
    Fernet antes de persistirse."""

    __tablename__ = "configuracion_ia"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,   # 1 configuración de IA por empresa
    )
    # 'default' | 'gemini' | 'openai' | 'claude'
    proveedor = db.Column(db.String(50), nullable=False, default=IA_DEFAULT)
    # BYOK: API key cifrada con Fernet. NULL = usa clave del sistema.
    api_key_cifrada = db.Column(db.Text, nullable=True)
    # Modelo concreto a usar: 'gemini-2.0-flash' | 'gpt-4o' | 'claude-3-5-sonnet' | etc.
    modelo = db.Column(db.String(100), nullable=True)
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
    empresa = db.relationship("Empresa", back_populates="configuracion_ia")

    def __repr__(self) -> str:
        return f"<ConfiguracionIA proveedor={self.proveedor!r} modelo={self.modelo!r}>"
