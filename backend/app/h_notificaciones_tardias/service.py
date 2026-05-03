"""Servicio de notificaciones para check-in tardíos.

Orquesta:
- Lectura del maestro de apartamentos (activos de la empresa).
- Obtención de reservas de hoy desde el PMS API configurado.
- Parseo de XLSX subido por el usuario (procesado en memoria, no persiste — RGPD).
- Generación del texto de notificación que el usuario copia manualmente.
  (El envío de email queda fuera de este scope.)
"""

import logging
from datetime import date

from flask import current_app

from app.h_maestro_apartamentos import repository as apt_repo
from app.perfil import repository as perfil_repo
from app.common.col_utils import col_letra_a_indice
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
    - hora_corte configurada para la empresa.
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

    # Mapa id_externo normalizado -> Apartamento para cruce de nombre y dirección
    apts_por_externo = {_norm_id(a.id_externo): a for a in apts if a.id_externo}

    config = perfil_repo.get_notif_tardio_config(empresa_id)
    hora_corte = config.get("hora_corte", "20:00")

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
                reservas_pms = [_reserva_a_dict(r, apts_por_externo) for r in reservas]
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
        "hora_corte": hora_corte,
    }


# ── XLSX ──────────────────────────────────────────────────────────────────


def parse_checkins_xlsx(
    file_bytes: bytes,
    empresa_id: str,
    hora_corte: str,
    col_config: dict,
) -> tuple[list[dict], list[str]]:
    """Parsea un XLSX y devuelve los check-ins tardíos (hora_llegada >= hora_corte).

    Solo incluye reservas con hora_llegada conocida. Las que no tienen hora se
    excluyen silenciosamente (criterio estricto).
    Los datos se procesan en memoria y no se persisten (cumplimiento RGPD).
    """
    # Construir col_overrides desde las letras configuradas
    _FIELD_MAP = {
        "col_nombre":       "nombre_raw",
        "col_checkin":      "checkin",
        "col_hora_llegada": "hora_llegada",
        "col_telefono":     "telefono",
        "col_apartamento":  "nombre_apartamento",
    }
    col_overrides: dict[int, str] = {}
    for config_key, field in _FIELD_MAP.items():
        letra = col_config.get(config_key, "")
        if letra:
            try:
                col_overrides[col_letra_a_indice(letra)] = field
            except ValueError:
                pass

    reservas, errores = parse_xlsx_reservas(
        file_bytes,
        col_overrides=col_overrides if col_overrides else None,
    )

    # Filtrar: solo con hora_llegada conocida y >= hora_corte
    tardias = [
        r for r in reservas
        if r.hora_llegada and r.hora_llegada >= hora_corte
    ]

    # Cruzar con maestro para nombre y dirección
    apts = apt_repo.list_by_empresa(empresa_id)
    apts_por_externo = {_norm_id(a.id_externo): a for a in apts if a.id_externo}

    return [_reserva_a_dict(r, apts_por_externo) for r in tardias], errores


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


def _norm_id(valor: str) -> str:
    """Normaliza un ID externo quitando llaves y espacios para comparación robusta.

    Ejemplos: '{4}' → '4', '  4  ' → '4', '{APT-12}' → 'APT-12'.
    """
    s = str(valor).strip().strip("{}").strip()
    try:
        return str(int(s))   # '04' → '4'
    except ValueError:
        return s


def _reserva_a_dict(r, apartamentos_por_externo: dict | None = None) -> dict:
    direccion = None
    nombre_apt = r.nombre_apartamento

    if apartamentos_por_externo:
        # Intentar cruce con id_apartamento_externo y con nombre_apartamento
        # (el XLSX puede tener el ID del maestro en la columna de apartamento)
        for candidato in filter(None, [r.id_apartamento_externo, r.nombre_apartamento]):
            apt = apartamentos_por_externo.get(_norm_id(candidato))
            if apt:
                direccion = apt.direccion
                nombre_apt = apt.nombre
                break
    return {
        "nombre": r.nombre_raw,
        "apartamento": nombre_apt,
        "email": r.email,
        "telefono": r.telefono,
        "checkin": r.checkin,
        "checkout": r.checkout,
        "hora_llegada": r.hora_llegada,
        "direccion": direccion,
    }
