"""Servicio de procesamiento del formulario de contacto general."""

import logging

from flask import request
from marshmallow import ValidationError

from app.common.notifications.discord import send_discord_contact_notification
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

    send_discord_contact_notification(clean_data)

    logger.info(
        "Mensaje de contacto recibido de: %s",
        clean_data.get("email"),
    )

    return clean_data, []
