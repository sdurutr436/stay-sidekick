"""Servicio del módulo de empresas."""

import logging

from app.empresas import repository

logger = logging.getLogger(__name__)


def borrar_empresa_completa(empresa_id: str) -> bool:
    """Elimina una empresa y todas sus dependencias en cascada.

    Las relaciones ``cascade="all, delete-orphan"`` del modelo ``Empresa``
    garantizan que usuarios, apartamentos, plantillas, mensajes, configuración
    PMS, integración Google, configuración IA y logs desaparecen con ella.
    """
    eliminada = repository.eliminar_empresa(empresa_id)
    if eliminada:
        logger.info("Empresa %s eliminada con todas sus dependencias.", empresa_id)
    else:
        logger.warning("Intento de borrado de empresa inexistente: %s", empresa_id)
    return eliminada
