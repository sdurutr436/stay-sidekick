"""Capa de estandarización de PMS (Property Management Systems).

Patrón de adaptadores: cada PMS tiene su propio módulo cliente que
devuelve datos normalizados a través de ReservaEstandar. El módulo de
contactos (y cualquier otro que necesite datos de reservas) trabaja
únicamente con estos tipos normalizados, sin conocer los detalles de
cada API externa.

Adaptadores disponibles:
- smoobu   → SmoobuReservationClient  (app.pms.smoobu)
- beds24   → Beds24ReservationClient  (app.pms.beds24)  [stub]

Para sincronización de propiedades (apartamentos), ver app/apartamentos/.
"""

from app.pms.base import PMSClient, ReservaEstandar

__all__ = ["PMSClient", "ReservaEstandar"]
