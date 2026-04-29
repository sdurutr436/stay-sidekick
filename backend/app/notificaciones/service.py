"""Servicio de notificaciones para check-in tardíos.

Orquesta:
- Lectura del maestro de apartamentos (activos de la empresa).
- Obtención de reservas de hoy desde el PMS API configurado.
- Parseo de XLSX subido por el usuario (procesado en memoria, no persiste — RGPD).
- Envío de email de notificación vía Gmail SMTP con destino y mensaje personalizables.
"""

import logging
from datetime import date

from flask import current_app

from app.apartamentos import repository as apt_repo
from app.common.crypto import decrypt
from app.common.notifications.gmail import send_via_smtp
from app.common.xlsx_reservas import parse_xlsx_reservas
from app.normalizador_pms.factory import build_pms_client

logger = logging.getLogger(__name__)


# ── Status ────────────────────────────────────────────────────────────────


def get_status(empresa_id: str) -> dict:
    """Devuelve el estado de la herramienta para la empresa.

    Incluye:
    - Si Gmail SMTP está configurado (GMAIL_USER + GMAIL_APP_PASSWORD).
    - Si hay PMS configurado y las reservas de check-in de hoy.
    - Lista de apartamentos activos del maestro.
    """
    gmail_ok = bool(
        current_app.config.get("GMAIL_USER")
        and current_app.config.get("GMAIL_APP_PASSWORD")
    )

    apts = apt_repo.list_by_empresa(empresa_id)
    apartamentos = [
        {"id": str(a.id), "nombre": a.nombre, "ciudad": a.ciudad}
        for a in apts
    ]

    reservas_pms: list[dict] = []
    pms_configurado = False
    pms_error: str | None = None

    pms_config = apt_repo.get_pms_config(empresa_id)
    if pms_config and pms_config.api_key_cifrada:
        api_key = decrypt(pms_config.api_key_cifrada)
        if api_key:
            pms_configurado = True
            try:
                client = build_pms_client(
                    pms_config.proveedor, api_key, pms_config.endpoint
                )
                hoy = date.today().isoformat()
                reservas = client.fetch_reservations(desde=hoy, hasta=hoy)
                reservas_pms = [_reserva_a_dict(r) for r in reservas]
            except Exception as exc:
                logger.warning(
                    "Error al obtener reservas PMS para notificaciones: %s", exc
                )
                pms_error = "No se pudieron cargar las reservas del PMS."

    return {
        "gmail_configurado": gmail_ok,
        "pms_configurado": pms_configurado,
        "pms_error": pms_error,
        "apartamentos": apartamentos,
        "reservas_pms": reservas_pms,
    }


# ── XLSX ──────────────────────────────────────────────────────────────────


def parse_checkins_xlsx(file_bytes: bytes) -> tuple[list[dict], list[str]]:
    """Parsea un XLSX y devuelve los check-ins de hoy.

    Si el archivo contiene columna de fecha de check-in, filtra por hoy.
    Si no tiene columna de fecha, devuelve todas las filas (con aviso).
    Los datos se procesan en memoria y no se persisten (cumplimiento RGPD).
    """
    reservas, errores = parse_xlsx_reservas(file_bytes)
    hoy = date.today().isoformat()

    tiene_fechas = any(r.checkin for r in reservas)
    if tiene_fechas:
        reservas_hoy = [r for r in reservas if r.checkin == hoy]
        if not reservas_hoy:
            errores = [f"No hay check-ins para hoy ({hoy}) en el archivo."] + errores
    else:
        reservas_hoy = reservas
        errores = ["El archivo no contiene columna de fecha — se muestran todas las filas."] + errores

    return [_reserva_a_dict(r) for r in reservas_hoy], errores


# ── Envío de email ────────────────────────────────────────────────────────


def enviar_notificacion(
    destinatario: str, asunto: str, mensaje: str
) -> tuple[bool, str | None]:
    """Envía un email de notificación vía Gmail SMTP."""
    ok, error = send_via_smtp(destinatario, asunto, mensaje)
    if ok:
        logger.info(
            "Notificación check-in tardío enviada a '%s' (asunto: '%s')",
            destinatario,
            asunto,
        )
    return ok, error


# ── Helpers privados ──────────────────────────────────────────────────────


def _reserva_a_dict(r) -> dict:
    return {
        "nombre": r.nombre_raw,
        "apartamento": r.nombre_apartamento,
        "email": r.email,
        "telefono": r.telefono,
        "checkin": r.checkin,
        "checkout": r.checkout,
    }
