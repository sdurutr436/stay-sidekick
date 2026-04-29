"""Cliente HTTP para la API de Smoobu.

Documentación: https://docs.smoobu.com/

Endpoints utilizados:
- GET /api/apartments         → lista de propiedades (id + name)
- GET /api/apartments/{id}    → detalle con location (street, city, country)

Autenticación: cabecera ``Api-Key: <api_key>``.
"""

import logging
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)

_BASE_URL = "https://login.smoobu.com"
_TIMEOUT = 15  # segundos


@dataclass
class SmoobuApartment:
    """Datos normalizados de una propiedad de Smoobu."""
    id_externo: str
    nombre: str
    direccion: str | None
    ciudad: str | None


class SmoobuClient:
    """Cliente para la API REST de Smoobu."""

    def __init__(self, api_key: str) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "Api-Key": api_key,
            "Accept": "application/json",
        })

    def list_apartments(self) -> list[dict]:
        """GET /api/apartments → [{id, name}, ...]"""
        url = f"{_BASE_URL}/api/apartments"
        resp = self._session.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("apartments", [])

    def get_apartment_detail(self, apartment_id: int) -> dict:
        """GET /api/apartments/{id} → detalle completo con location."""
        url = f"{_BASE_URL}/api/apartments/{apartment_id}"
        resp = self._session.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def fetch_all_normalized(self) -> list[SmoobuApartment]:
        """Obtiene todas las propiedades con dirección (2 llamadas por apt).

        Flujo:
        1. Lista ligera → IDs + nombres.
        2. Para cada ID → detalle con location.
        3. Normaliza a SmoobuApartment.
        """
        apartments_raw = self.list_apartments()
        logger.info("Smoobu: %d propiedades encontradas", len(apartments_raw))

        result: list[SmoobuApartment] = []
        for apt in apartments_raw:
            apt_id = apt.get("id")
            apt_name = apt.get("name", "")
            if apt_id is None:
                continue

            try:
                detail = self.get_apartment_detail(apt_id)
            except requests.RequestException:
                logger.warning("Smoobu: error al obtener detalle de apt %s, se omite", apt_id)
                continue

            location = detail.get("location", {})
            street = location.get("street", "")
            city = location.get("city", "")

            direccion = street if street else None
            ciudad = city if city else None

            result.append(SmoobuApartment(
                id_externo=str(apt_id),
                nombre=apt_name,
                direccion=direccion,
                ciudad=ciudad,
            ))

        logger.info("Smoobu: %d propiedades normalizadas", len(result))
        return result
