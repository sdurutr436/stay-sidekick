"""Servicio de notificación por Discord Webhook.

Envía un embed enriquecido a un canal de Discord cada vez que se recibe
una solicitud de contacto válida. Usa únicamente ``requests`` (ya presente
en el proyecto) — no requiere dependencias adicionales.

Configuración necesaria en .env:
    DISCORD_WEBHOOK_URL → URL del webhook de Discord
"""

import logging
from datetime import datetime, timezone

import requests
from flask import current_app

logger = logging.getLogger(__name__)

_TIMEOUT = 5


def _build_embed(clean_data: dict) -> dict:
    """Construye el payload de embed de Discord."""
    is_member = "Si" if clean_data.get("is_member") else "No"

    fields = [
        {"name": "Empresa", "value": clean_data.get("company_name", "N/A"), "inline": True},
        {"name": "Email", "value": clean_data.get("company_email", "N/A"), "inline": True},
        {"name": "Telefono", "value": clean_data.get("phone", "N/A"), "inline": True},
        {"name": "Pais", "value": clean_data.get("country_code", "N/A"), "inline": True},
        {"name": "Miembro", "value": is_member, "inline": True},
        {"name": "Mensaje", "value": clean_data.get("message", "(sin mensaje)")[:1024], "inline": False},
    ]

    return {
        "embeds": [
            {
                "title": "Nueva solicitud de contacto",
                "color": 0x5865F2,  # Blurple de Discord
                "fields": fields,
                "footer": {"text": "Stay Sidekick — Formulario de contacto"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ]
    }


def send_discord_notification(clean_data: dict) -> bool:
    """Envía la notificación al webhook de Discord.

    Returns
    -------
    bool
        ``True`` si Discord respondió con 2xx.
    """
    webhook_url = current_app.config.get("DISCORD_WEBHOOK_URL", "")

    if not webhook_url:
        logger.warning(
            "Discord webhook no configurado (DISCORD_WEBHOOK_URL vacío). "
            "La notificación no se enviará."
        )
        return False

    payload = _build_embed(clean_data)

    try:
        resp = requests.post(
            webhook_url,
            json=payload,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()

        logger.info(
            "Notificación de Discord enviada para solicitud de %s",
            clean_data.get("company_name"),
        )
        return True

    except requests.RequestException:
        logger.exception("Error al enviar notificación a Discord")
        return False
