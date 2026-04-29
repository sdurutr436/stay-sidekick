"""Modelo del maestro de alojamientos gestionado por cada empresa."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db

# Posibles orígenes de alta del alojamiento
ORIGEN_SMOOBU = "smoobu"
ORIGEN_MANUAL = "manual"
ORIGEN_XLSX = "xlsx"


class Apartamento(db.Model):
    """Alojamiento gestionado por una empresa.

    Actúa como tabla de referencia para el cruce con reservas importadas
    (vía PMS o XLSX). Los datos aquí almacenados no incluyen información
    personal de huéspedes (cumplimiento RGPD)."""

    __tablename__ = "apartamentos"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # ID único del apartamento en el PMS externo (columna 1 del XLSX; nulo si manual)
    id_pms = db.Column(db.String(100), nullable=True)
    # Código de tipología: puede ser compartido por varios apartamentos del mismo tipo
    id_externo = db.Column(db.String(100), nullable=True)
    nombre = db.Column(db.String(200), nullable=False)
    direccion = db.Column(db.String(300), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    # Origen del alta: 'smoobu' | 'manual' | 'xlsx'
    pms_origen = db.Column(db.String(50), nullable=True)
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

    __table_args__ = (
        # Índice parcial único: un id_pms solo puede existir una vez por empresa
        # (solo aplica cuando id_pms no es NULL; los manuales sin id_pms no se limitan)
        db.Index(
            "uq_apartamento_empresa_id_pms",
            "empresa_id",
            "id_pms",
            unique=True,
            postgresql_where=db.text("id_pms IS NOT NULL"),
        ),
    )

    # Relaciones
    empresa = db.relationship("Empresa", back_populates="apartamentos")

    def __repr__(self) -> str:
        return f"<Apartamento {self.nombre!r} empresa={self.empresa_id}>"
