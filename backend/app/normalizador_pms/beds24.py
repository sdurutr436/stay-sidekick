"""Adaptador PMS: Beds24 — reservas de huéspedes (stub).

Se completará cuando la empresa disponga de acceso a la API de Beds24.
El protocolo PMSClient garantiza que el servicio de contactos no necesita
saber nada de esta implementación.
"""

from app.normalizador_pms.base import ReservaEstandar


class Beds24ReservationClient:
    """Cliente Beds24 — pendiente de implementar."""

    def __init__(self, api_key: str, endpoint: str | None = None) -> None:
        self._api_key = api_key
        self._endpoint = endpoint

    def fetch_reservations(
        self,
        desde: str | None = None,
        hasta: str | None = None,
    ) -> list[ReservaEstandar]:
        raise NotImplementedError(
            "Adaptador Beds24 pendiente de implementar. "
            "Consulta la documentación de la API de Beds24."
        )
