"""Registro de todos los modelos SQLAlchemy.

Importar este paquete garantiza que todos los modelos queden registrados
en el metadata de SQLAlchemy antes de cualquier operación con la BD.
"""

from app.empresas.model import Empresa
from app.usuarios.model import Usuario
from app.h_maestro_apartamentos.model import Apartamento
from app.h_vault_comunicaciones.model import PlantillaVault, MensajeGenerado
from app.perfil.model import ConfiguracionPMS, ConfiguracionIA
from app.h_sincronizador_contactos.model import IntegracionGoogle
from app.h_sincronizador_contactos.model import LogSincronizacion

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
