"""Factory de clientes PMS.

Centraliza la instanciación del adaptador correcto según el proveedor
configurado. Importado por cualquier módulo que necesite obtener reservas
del PMS (google_contacts, notificaciones, etc.).
"""

from app.pms.beds24 import Beds24ReservationClient
from app.pms.smoobu import SmoobuReservationClient


def build_pms_client(proveedor: str, api_key: str, endpoint: str | None):
    """Instancia el adaptador PMS correcto según el proveedor configurado."""
    if proveedor == "smoobu":
        return SmoobuReservationClient(api_key)
    if proveedor == "beds24":
        return Beds24ReservationClient(api_key, endpoint)
    raise ValueError(f"Proveedor PMS no soportado para reservas: {proveedor!r}")
