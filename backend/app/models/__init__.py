"""Registro de todos los modelos SQLAlchemy.

Importar este paquete garantiza que todos los modelos queden registrados
en el metadata de SQLAlchemy antes de cualquier operación con la BD.
"""

from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.models.apartamento import Apartamento
from app.models.vault import PlantillaVault, MensajeGenerado
from app.models.integraciones import ConfiguracionPMS, IntegracionGoogle, ConfiguracionIA
from app.models.logs import LogSincronizacion

__all__ = [
    "Empresa",
    "Usuario",
    "Apartamento",
    "PlantillaVault",
    "MensajeGenerado",
    "ConfiguracionPMS",
    "IntegracionGoogle",
    "ConfiguracionIA",
    "LogSincronizacion",
]
