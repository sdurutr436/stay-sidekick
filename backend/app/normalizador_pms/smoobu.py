"""Adaptador PMS: Smoobu — reservas de huéspedes.

Documentación: https://docs.smoobu.com/

Endpoints usados:
- GET /api/reservations  → listado de reservas con datos del huésped

Nota: Este módulo maneja *reservas* (guests). Para sincronización de
propiedades (apartamentos), ver app/h_maestro_apartamentos/.
"""

import logging
from datetime import date, timedelta

import requests

from app.normalizador_pms.base import ReservaEstandar

logger = logging.getLogger(__name__)

_BASE_URL = "https://login.smoobu.com"
_TIMEOUT = 15
_PAGE_SIZE = 100


class SmoobuReservationClient:
    """Obtiene reservas de Smoobu y las normaliza a ReservaEstandar."""

    def __init__(self, api_key: str) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "Api-Key": api_key,
            "Accept": "application/json",
        })

    def fetch_reservations(
        self,
        desde: str | None = None,
        hasta: str | None = None,
    ) -> list[ReservaEstandar]:
        """Obtiene reservas del rango [desde, hasta] paginando hasta el final."""
        if desde is None:
            desde = date.today().isoformat()
        if hasta is None:
            hasta = (date.today() + timedelta(days=365)).isoformat()

        reservas: list[ReservaEstandar] = []
        page = 1

        while True:
            raw = self._fetch_page(desde, hasta, page)
            bookings = raw.get("bookings", [])
            if not bookings:
                break
            for booking in bookings:
                reserva = self._normalize(booking)
                if reserva is not None:
                    reservas.append(reserva)
            total_pages = raw.get("page_count", 1)
            if page >= total_pages:
                break
            page += 1

        logger.info(
            "Smoobu reservas: %d obtenidas (rango %s — %s)",
            len(reservas), desde, hasta,
        )
        return reservas

    def _fetch_page(self, desde: str, hasta: str, page: int) -> dict:
        url = f"{_BASE_URL}/api/reservations"
        params = {
            "arrivalFrom": desde,
            "arrivalTo": hasta,
            "pageSize": _PAGE_SIZE,
            "page": page,
        }
        resp = self._session.get(url, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _normalize(booking: dict) -> ReservaEstandar | None:
        """Convierte un booking de Smoobu en ReservaEstandar."""
        nombre = booking.get("firstName", "").strip()
        apellido = booking.get("lastName", "").strip()

        if apellido and nombre:
            nombre_raw = f"{apellido}, {nombre}"
        elif apellido:
            nombre_raw = apellido
        elif nombre:
            nombre_raw = nombre
        else:
            nombre_raw = (booking.get("guest-name") or "").strip()

        if not nombre_raw:
            return None

        prop = booking.get("property") or {}

        return ReservaEstandar(
            id_externo=str(booking.get("id", "")),
            nombre_raw=nombre_raw,
            email=booking.get("email") or None,
            telefono=booking.get("phone") or None,
            checkin=booking.get("arrivalDate") or None,
            checkout=booking.get("departureDate") or None,
            nombre_apartamento=prop.get("name") or None,
            id_apartamento_externo=str(prop.get("id")) if prop.get("id") else None,
        )
