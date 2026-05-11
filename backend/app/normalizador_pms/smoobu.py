"""Adaptador PMS: Smoobu — reservas de huéspedes.

Documentación: https://docs.smoobu.com/

Endpoints usados:
- GET /api/reservations  → listado de reservas con datos del huésped

Nota: Este módulo maneja *reservas* (guests). Para sincronización de
propiedades (apartamentos), ver app/h_maestro_apartamentos/.
"""

import logging
import re
from datetime import date, datetime, timedelta

import requests

from app.normalizador_pms.base import ReservaEstandar

logger = logging.getLogger(__name__)

_BASE_URL = "https://login.smoobu.com"


def _to_iso(valor: str | None) -> str | None:
    """Convierte cualquier formato de fecha de Smoobu a ISO 8601 (YYYY-MM-DD).

    Formatos soportados: YYYY-MM-DD, DD.MM.YYYY, DD.MM.YY, DD/MM/YYYY,
    DD/MM/YY, MM/DD/YY, DD-MM-YYYY, DD-MM-YY, YY-MM-DD.
    """
    if not valor:
        return None
    s = str(valor).strip()

    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s

    if re.match(r"^\d{1,2}\.\d{1,2}\.\d{4}$", s):
        try:
            return datetime.strptime(s, "%d.%m.%Y").date().isoformat()
        except ValueError:
            return None

    if re.match(r"^\d{1,2}\.\d{1,2}\.\d{2}$", s):
        try:
            return datetime.strptime(s, "%d.%m.%y").date().isoformat()
        except ValueError:
            return None

    if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", s):
        a, b = int(s.split("/")[0]), int(s.split("/")[1])
        fmt = "%m/%d/%Y" if a <= 12 and b > 12 else "%d/%m/%Y"
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            return None

    if re.match(r"^\d{1,2}/\d{1,2}/\d{2}$", s):
        a, b = int(s.split("/")[0]), int(s.split("/")[1])
        fmt = "%m/%d/%y" if a <= 12 and b > 12 else "%d/%m/%y"
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            return None

    if re.match(r"^\d{1,2}-\d{1,2}-\d{4}$", s):
        try:
            return datetime.strptime(s, "%d-%m-%Y").date().isoformat()
        except ValueError:
            return None

    if re.match(r"^\d{2}-\d{2}-\d{2}$", s):
        a = int(s.split("-")[0])
        fmt = "%y-%m-%d" if a > 31 else "%d-%m-%y"
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            return None

    logger.warning("smoobu._to_iso: formato de fecha no reconocido: %r", s)
    return None


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

    def fetch_by_departure(
        self,
        desde: str,
        hasta: str,
    ) -> list[ReservaEstandar]:
        """Obtiene reservas cuyo checkout cae en el rango [desde, hasta].

        # TODO: validar con documentación oficial de Smoobu en https://docs.smoobu.com
        # Endpoint: GET https://login.smoobu.com/api/reservations
        # Parámetros asumidos: departureFrom, departureTo (análogos a arrivalFrom/arrivalTo)
        """
        reservas: list[ReservaEstandar] = []
        page = 1

        while True:
            raw = self._fetch_page_by_departure(desde, hasta, page)
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
            "Smoobu checkouts: %d obtenidos (rango %s — %s)",
            len(reservas), desde, hasta,
        )
        return reservas

    def _fetch_page_by_departure(self, desde: str, hasta: str, page: int) -> dict:
        url = f"{_BASE_URL}/api/reservations"
        params = {
            "departureFrom": desde,
            "departureTo": hasta,
            "pageSize": _PAGE_SIZE,
            "page": page,
        }
        resp = self._session.get(url, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _normalize(booking: dict) -> ReservaEstandar | None:
        """Convierte un booking de Smoobu en ReservaEstandar."""
        nombre = booking.get("firstname", "").strip()
        apellido = booking.get("lastname", "").strip()

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

        apt = booking.get("apartment") or {}
        raw_phone = booking.get("phone") or None
        telefono = re.sub(r"\((\+\d+)\)", r"\1", raw_phone) if raw_phone else None

        # Smoobu no garantiza hora de llegada; algunos canales la incluyen
        hora_llegada: str | None = None
        raw_hora = booking.get("check_in_time") or booking.get("checkInTime")
        if raw_hora:
            s = str(raw_hora).strip()
            m = re.match(r"^(\d{1,2}):(\d{2})", s)
            if m:
                hora_llegada = f"{int(m.group(1)):02d}:{m.group(2)}"

        return ReservaEstandar(
            id_externo=str(booking.get("id", "")),
            nombre_raw=nombre_raw,
            email=booking.get("email") or None,
            telefono=telefono,
            checkin=_to_iso(booking.get("arrival")),
            checkout=_to_iso(booking.get("departure")),
            nombre_apartamento=apt.get("name") or None,
            id_apartamento_externo=str(apt.get("id")) if apt.get("id") else None,
            hora_llegada=hora_llegada,
        )
