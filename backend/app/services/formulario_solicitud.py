"""Servicio de procesamiento del formulario público de solicitud de acceso."""

import logging

from flask import request
from marshmallow import ValidationError

from app.common.notifications.discord import send_discord_notification
from app.common.notifications.gmail import send_contact_email
from app.schemas.formulario_solicitud import FormularioSolicitudSchema
from app.services.turnstile import verify_turnstile

logger = logging.getLogger(__name__)

_schema = FormularioSolicitudSchema()


def process_solicitud(json_data: dict) -> tuple[dict, list[str]]:
    """Valida, sanitiza y procesa los datos del formulario de solicitud.

    Returns
    -------
    tuple[dict, list[str]]
        (datos_limpios, errores). Si ``errores`` está vacío, los datos
        son seguros para notificar.
    """
    # 1. Validación y sanitización con Marshmallow (incluye honeypot)
    try:
        clean_data: dict = _schema.load(json_data)
    except ValidationError as exc:
        return {}, _flatten_errors(exc.messages)

    # 2. Verificar Turnstile
    turnstile_token = clean_data.pop("turnstile_token")
    client_ip = request.remote_addr
    if not verify_turnstile(turnstile_token, client_ip):
        return {}, ["La verificación del captcha ha fallado."]

    # 3. Eliminar campos internos (ya validados, no se almacenan)
    clean_data.pop("privacy_accepted", None)
    clean_data.pop("website", None)  # honeypot

    # 4. Despachar notificaciones (no bloquean la respuesta al usuario)
    _dispatch_notifications(clean_data)

    logger.info(
        "Formulario de solicitud procesado para: %s",
        clean_data.get("company_email"),
    )

    return clean_data, []


def _dispatch_notifications(clean_data: dict) -> None:
    """Envía las notificaciones de email y Discord."""
    email_ok = send_contact_email(clean_data)
    discord_ok = send_discord_notification(clean_data)

    if not email_ok:
        logger.warning("No se pudo enviar el email de notificación.")
    if not discord_ok:
        logger.warning("No se pudo enviar la notificación de Discord.")


def _flatten_errors(messages: dict) -> list[str]:
    errors: list[str] = []
    for field, msgs in messages.items():
        if isinstance(msgs, list):
            for msg in msgs:
                errors.append(f"{field}: {msg}")
        elif isinstance(msgs, dict):
            for sub_msgs in msgs.values():
                if isinstance(sub_msgs, list):
                    errors.extend(f"{field}: {m}" for m in sub_msgs)
    return errors
