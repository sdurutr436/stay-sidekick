"""Tipos y protocolo base para adaptadores de PMS.

Cada adaptador implementa PMSClient y devuelve listas de ReservaEstandar.
Esto desacopla el módulo de contactos (y futuros módulos) de la API
concreta de cada proveedor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ReservaEstandar:
    """Datos de reserva normalizados, independientes del PMS origen.

    nombre_raw sigue el formato habitual de los PMS: "Apellido Apellido, Nombre"
    o simplemente "Nombre Apellido" si el PMS no distingue campos. El
    servicio de contactos decide cómo estructurarlo según las preferencias
    de la empresa almacenadas en empresas.configuracion.
    """

    id_externo: str
    nombre_raw: str                    # "García López, Juan" o "Juan García"
    email: str | None
    telefono: str | None
    checkin: str | None                # ISO 8601: "YYYY-MM-DD"
    checkout: str | None               # ISO 8601: "YYYY-MM-DD"
    nombre_apartamento: str | None
    id_apartamento_externo: str | None


class PMSClient(Protocol):
    """Protocolo que deben cumplir todos los adaptadores de PMS."""

    def fetch_reservations(
        self,
        desde: str | None = None,
        hasta: str | None = None,
    ) -> list[ReservaEstandar]:
        """Obtiene reservas normalizadas del PMS."""
        ...
