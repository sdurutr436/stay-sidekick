"""Servicio de procesamiento del formulario de contacto general."""

import logging

from flask import request
from marshmallow import ValidationError

from app.common.notifications.discord import (
    send_discord_contact_notification,
    send_operational_notification,
)
from app.common.notifications.mail_service import send_contact
from app.contact.schemas import ContactoMessageSchema
from app.solicitud.turnstile import verify_turnstile

logger = logging.getLogger(__name__)

_schema = ContactoMessageSchema()


def process_contacto(json_data: dict) -> tuple[dict, list[str]]:
    """Valida, sanitiza y procesa los datos del formulario de contacto.

    Returns (datos_limpios, errores).
    """
    try:
        clean_data: dict = _schema.load(json_data)
    except ValidationError as exc:
        flat = [
            msg
            for msgs in exc.messages.values()
            for msg in (msgs if isinstance(msgs, list) else [msgs])
        ]
        return {}, flat

    turnstile_token = clean_data.pop("turnstile_token")
    clean_data.pop("website", None)

    client_ip = request.remote_addr
    if not verify_turnstile(turnstile_token, client_ip):
        return {}, ["La verificación del captcha ha fallado."]

    _dispatch_notifications(clean_data)

    logger.info(
        "Mensaje de contacto recibido de: %s",
        clean_data.get("email"),
    )

    return clean_data, []


def _dispatch_notifications(clean_data: dict) -> None:
    failed_channels: list[str] = []

    try:
        email_ok = send_contact(clean_data)
    except Exception:
        logger.exception("Excepción inesperada al enviar contacto por email.")
        email_ok = False
    if not email_ok:
        failed_channels.append("email")

    try:
        discord_ok = send_discord_contact_notification(clean_data)
    except Exception:
        logger.exception("Excepción inesperada al notificar contacto a Discord.")
        discord_ok = False
    if not discord_ok:
        failed_channels.append("discord-funcional")

    if not email_ok:
        logger.warning("No se pudo enviar el email de contacto.")
    if not discord_ok:
        logger.warning("No se pudo enviar la notificación de contacto a Discord.")
    if failed_channels:
        send_operational_notification(
            "Fallo en notificaciones del formulario de contacto",
            {
                "Formulario": "contacto",
                "Canales fallidos": failed_channels,
            },
            severity="error" if "email" in failed_channels else "warning",
        )
