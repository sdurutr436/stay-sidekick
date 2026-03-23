"""Servicio de envío de correo electrónico vía Gmail SMTP.

Usa la librería estándar ``smtplib`` + ``email`` de Python — no requiere
dependencias externas. Se conecta al servidor SMTP de Gmail con TLS y
autenticación mediante *App Password* (contraseña de aplicación).

Configuración necesaria en .env:
    GMAIL_USER        → tu-correo@gmail.com
    GMAIL_APP_PASSWORD→ contraseña de aplicación de 16 caracteres
    MAIL_RECIPIENT    → correo destino que recibe las solicitudes
"""

import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

logger = logging.getLogger(__name__)

_SMTP_HOST = "smtp.gmail.com"
_SMTP_PORT = 587
_TIMEOUT = 10


def _build_message(clean_data: dict) -> EmailMessage:
    """Construye el EmailMessage con los datos sanitizados del formulario."""
    sender = current_app.config["GMAIL_USER"]
    recipient = current_app.config["MAIL_RECIPIENT"]

    msg = EmailMessage()
    msg["Subject"] = (
        f"[Stay Sidekick] Nueva solicitud de {clean_data.get('company_name', 'N/A')}"
    )
    msg["From"] = sender
    msg["To"] = recipient

    is_member = "Sí" if clean_data.get("is_member") else "No"

    body = (
        "Se ha recibido una nueva solicitud desde el formulario de contacto.\n"
        "\n"
        "─────────────────────────────────────\n"
        f"  Empresa:   {clean_data.get('company_name', 'N/A')}\n"
        f"  Email:     {clean_data.get('company_email', 'N/A')}\n"
        f"  Teléfono:  {clean_data.get('phone', 'N/A')}\n"
        f"  País:      {clean_data.get('country_code', 'N/A')}\n"
        f"  Miembro:   {is_member}\n"
        "─────────────────────────────────────\n"
        "\n"
        "Mensaje:\n"
        f"{clean_data.get('message', '(sin mensaje)')}\n"
    )
    msg.set_content(body)
    return msg


def send_contact_email(clean_data: dict) -> bool:
    """Envía el email de notificación por Gmail SMTP.

    Returns
    -------
    bool
        ``True`` si el email se envió correctamente.
    """
    user = current_app.config.get("GMAIL_USER", "")
    password = current_app.config.get("GMAIL_APP_PASSWORD", "")

    if not user or not password:
        logger.warning(
            "Gmail SMTP no configurado (GMAIL_USER / GMAIL_APP_PASSWORD vacíos). "
            "El email de notificación no se enviará."
        )
        return False

    msg = _build_message(clean_data)

    try:
        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=_TIMEOUT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, password)
            server.send_message(msg)

        logger.info(
            "Email enviado a %s para solicitud de %s",
            current_app.config["MAIL_RECIPIENT"],
            clean_data.get("company_name"),
        )
        return True

    except smtplib.SMTPException:
        logger.exception("Error al enviar email vía Gmail SMTP")
        return False
