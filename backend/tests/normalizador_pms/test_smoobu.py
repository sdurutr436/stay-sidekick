"""Tests unitarios del normalizador de reservas de Smoobu."""

from app.normalizador_pms.smoobu import SmoobuReservationClient


def _booking(**extra) -> dict:
    base = {
        "id": 1,
        "firstname": "Ana",
        "lastname": "García",
        "email": "ana@test.com",
        "phone": "+34123",
        "arrival": "2025-06-01",
        "departure": "2025-06-05",
        "apartment": {"id": 9, "name": "Apto Centro"},
        "type": "reservation",
    }
    base.update(extra)
    return base


def test_normalize_hora_llegada_check_in_time():
    r = SmoobuReservationClient._normalize(_booking(check_in_time="15:00"))
    assert r.hora_llegada == "15:00"


def test_normalize_hora_llegada_camel_case():
    r = SmoobuReservationClient._normalize(_booking(checkInTime="14:30"))
    assert r.hora_llegada == "14:30"


def test_normalize_hora_llegada_formato_largo():
    r = SmoobuReservationClient._normalize(_booking(check_in_time="9:05:00"))
    assert r.hora_llegada == "09:05"


def test_normalize_hora_llegada_desde_arrival_time():
    """Smoobu devuelve la hora de llegada en arrivalTime."""
    r = SmoobuReservationClient._normalize(_booking(arrivalTime="16:30"))
    assert r.hora_llegada == "16:30"


def test_normalize_arrival_time_tiene_prioridad():
    """arrivalTime prima sobre check_in_time/checkInTime."""
    r = SmoobuReservationClient._normalize(_booking(arrivalTime="16:30", check_in_time="15:00"))
    assert r.hora_llegada == "16:30"


def test_normalize_sin_hora_llegada():
    r = SmoobuReservationClient._normalize(_booking())
    assert r.hora_llegada is None
