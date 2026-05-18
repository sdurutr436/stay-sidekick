"""Servicio de notificación por Discord Webhook.

Soporta tanto notificaciones funcionales de formularios como alertas
operativas y observabilidad de IA usando únicamente ``requests``.
"""

import logging
from datetime import datetime, timezone
from typing import Any

import requests
from flask import current_app

logger = logging.getLogger(__name__)

_TIMEOUT = 5
_SEVERITY_COLORS = {
    "info": 0x5865F2,
    "warning": 0xFEE75C,
    "error": 0xED4245,
}


def _build_embed(title: str, color: int, fields: list[dict[str, Any]], footer_text: str) -> dict:
    """Construye el payload de embed de Discord."""
    return {
        "embeds": [
            {
                "title": title,
                "color": color,
                "fields": fields,
                "footer": {"text": footer_text},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ]
    }


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def _stringify_detail(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        text = "Si" if value else "No"
    elif isinstance(value, (list, tuple, set)):
        text = ", ".join(str(item) for item in value if item not in (None, "")) or "N/A"
    else:
        text = str(value)
    return _truncate(text, 1024)


def _details_to_fields(details: dict[str, Any]) -> list[dict[str, Any]]:
    fields = []
    for name, value in details.items():
        rendered = _stringify_detail(value)
        fields.append(
            {
                "name": _truncate(str(name), 256),
                "value": rendered,
                "inline": len(rendered) <= 80,
            }
        )
    return fields


def _resolve_webhook_url(*config_keys: str) -> str:
    for config_key in config_keys:
        webhook_url = current_app.config.get(config_key, "")
        if webhook_url:
            return webhook_url
    return ""


def _post_webhook(
    webhook_url: str,
    payload: dict,
    *,
    missing_message: str,
    success_message: str,
    error_message: str,
) -> bool:
    if not webhook_url:
        logger.warning(missing_message)
        return False

    try:
        response = requests.post(webhook_url, json=payload, timeout=_TIMEOUT)
        response.raise_for_status()
        logger.info(success_message)
        return True
    except requests.RequestException:
        logger.exception(error_message)
        return False


def _build_request_embed(clean_data: dict) -> dict:
    """Construye el payload de embed de Discord."""
    is_member = "Si" if clean_data.get("is_member") else "No"

    fields = [
        {"name": "Empresa", "value": clean_data.get("company_name", "N/A"), "inline": True},
        {"name": "Email", "value": clean_data.get("company_email", "N/A"), "inline": True},
        {"name": "Teléfono", "value": clean_data.get("phone", "N/A"), "inline": True},
        {"name": "Miembro", "value": is_member, "inline": True},
        {"name": "Mensaje", "value": clean_data.get("message", "(sin mensaje)") or "(sin mensaje)", "inline": False},
    ]
    return _build_embed(
        "Nueva solicitud de contacto",
        0x5865F2,
        fields,
        "Stay Sidekick — Formulario de contacto",
    )


def send_discord_notification(clean_data: dict) -> bool:
    """Envía la notificación al webhook de Discord.

    Returns
    -------
    bool
        ``True`` si Discord respondió con 2xx.
    """
    payload = _build_request_embed(clean_data)
    return _post_webhook(
        current_app.config.get("DISCORD_WEBHOOK_URL", ""),
        payload,
        missing_message=(
            "Discord webhook no configurado (DISCORD_WEBHOOK_URL vacío). "
            "La notificación no se enviará."
        ),
        success_message=(
            "Notificación de Discord enviada para solicitud de "
            f"{clean_data.get('company_name')}"
        ),
        error_message="Error al enviar notificación a Discord",
    )


def _build_contact_embed(clean_data: dict) -> dict:
    """Construye el embed para el formulario de contacto personal."""
    empresa = clean_data.get("empresa", "")
    fields = [
        {"name": "Nombre", "value": clean_data.get("nombre", "N/A"), "inline": True},
        {"name": "Email", "value": clean_data.get("email", "N/A"), "inline": True},
    ]
    if empresa:
        fields.append({"name": "Empresa", "value": empresa, "inline": True})
    fields.append(
        {"name": "Mensaje", "value": clean_data.get("mensaje", "(sin mensaje)") or "(sin mensaje)", "inline": False}
    )

    return _build_embed(
        "Nuevo mensaje de contacto",
        0x57F287,
        fields,
        "Stay Sidekick — Formulario de contacto",
    )


def send_discord_contact_notification(clean_data: dict) -> bool:
    """Envía el mensaje del formulario de contacto al webhook de Discord.

    Usa DISCORD_WEBHOOK_CONTACT_URL (canal separado del de solicitudes).
    """
    payload = _build_contact_embed(clean_data)
    return _post_webhook(
        current_app.config.get("DISCORD_WEBHOOK_CONTACT_URL", ""),
        payload,
        missing_message=(
            "Discord contact webhook no configurado (DISCORD_WEBHOOK_CONTACT_URL vacío). "
            "La notificación no se enviará."
        ),
        success_message=f"Notificación de contacto enviada para: {clean_data.get('email')}",
        error_message="Error al enviar notificación de contacto a Discord",
    )


def send_operational_notification(title: str, details: dict[str, Any], severity: str = "error") -> bool:
    """Envía una alerta operativa al canal de observabilidad del backend."""
    payload = _build_embed(
        title,
        _SEVERITY_COLORS.get(severity, _SEVERITY_COLORS["error"]),
        _details_to_fields(details),
        "Stay Sidekick — Operación",
    )
    return _post_webhook(
        _resolve_webhook_url("DISCORD_WEBHOOK_OPERATIONS_URL"),
        payload,
        missing_message=(
            "Webhook operativo de Discord no configurado "
            "(DISCORD_WEBHOOK_OPERATIONS_URL vacío)."
        ),
        success_message=f"Alerta operativa enviada a Discord: {title}",
        error_message=f"Error al enviar alerta operativa a Discord: {title}",
    )


def send_ai_observability_notification(title: str, details: dict[str, Any], severity: str = "warning") -> bool:
    """Envía un evento de observabilidad de IA al webhook dedicado o al operativo."""
    payload = _build_embed(
        title,
        _SEVERITY_COLORS.get(severity, _SEVERITY_COLORS["warning"]),
        _details_to_fields(details),
        "Stay Sidekick — IA",
    )
    return _post_webhook(
        _resolve_webhook_url(
            "DISCORD_WEBHOOK_AI_OBSERVABILITY_URL",
            "DISCORD_WEBHOOK_OPERATIONS_URL",
        ),
        payload,
        missing_message=(
            "Webhook de observabilidad de IA no configurado "
            "(DISCORD_WEBHOOK_AI_OBSERVABILITY_URL y DISCORD_WEBHOOK_OPERATIONS_URL vacíos)."
        ),
        success_message=f"Evento de observabilidad IA enviado a Discord: {title}",
        error_message=f"Error al enviar evento de observabilidad IA a Discord: {title}",
    )
