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


def send_via_smtp(to: str, subject: str, body: str) -> tuple[bool, str | None]:
    """Envía un email de texto plano vía Gmail SMTP.

    Función de bajo nivel reutilizable por cualquier módulo que necesite
    enviar emails. Devuelve ``(True, None)`` si el envío fue exitoso o
    ``(False, mensaje_error)`` si falló.
    """
    user = current_app.config.get("GMAIL_USER", "")
    password = current_app.config.get("GMAIL_APP_PASSWORD", "")

    if not user or not password:
        return False, "Gmail SMTP no configurado (GMAIL_USER / GMAIL_APP_PASSWORD)."

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg.set_content(body)

    try:
        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=_TIMEOUT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, password)
            server.send_message(msg)
        return True, None

    except smtplib.SMTPException as exc:
        logger.exception("Error al enviar email vía Gmail SMTP")
        return False, f"Error al enviar el email: {exc}"


def send_contact_email(clean_data: dict) -> bool:
    """Envía el email de notificación de solicitud de contacto por Gmail SMTP.

    Returns
    -------
    bool
        ``True`` si el email se envió correctamente.
    """
    if not current_app.config.get("GMAIL_USER") or not current_app.config.get("GMAIL_APP_PASSWORD"):
        logger.warning(
            "Gmail SMTP no configurado (GMAIL_USER / GMAIL_APP_PASSWORD vacíos). "
            "El email de notificación no se enviará."
        )
        return False

    subject = f"[Stay Sidekick] Nueva solicitud de {clean_data.get('company_name', 'N/A')}"
    is_member = "Sí" if clean_data.get("is_member") else "No"
    body = (
        "Se ha recibido una nueva solicitud desde el formulario de contacto.\n"
        "\n"
        "─────────────────────────────────────\n"
        f"  Empresa:   {clean_data.get('company_name', 'N/A')}\n"
        f"  Email:     {clean_data.get('company_email', 'N/A')}\n"
        f"  Teléfono:  {clean_data.get('phone', 'N/A')}\n"
        f"  Miembro:   {is_member}\n"
        "─────────────────────────────────────\n"
        "\n"
        "Mensaje:\n"
        f"{clean_data.get('message', '') or '(sin mensaje)'}\n"
    )

    ok, _ = send_via_smtp(
        to=current_app.config["MAIL_RECIPIENT"],
        subject=subject,
        body=body,
    )
    if ok:
        logger.info(
            "Email enviado a %s para solicitud de %s",
            current_app.config["MAIL_RECIPIENT"],
            clean_data.get("company_name"),
        )
    return ok
