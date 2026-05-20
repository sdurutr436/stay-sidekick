"""Servicio reutilizable de envío de correo transaccional vía Mailgun HTTP API.

Usa la API HTTP de Mailgun (``requests``) — sin SMTP. Toda la configuración
se lee desde ``current_app.config`` (poblada desde variables de entorno en
:mod:`app.config`):

    MAIL_GUN_API_KEY   → clave privada de la cuenta Mailgun
    MAIL_GUN_DOMAIN    → dominio verificado en Mailgun (p.ej. ``stay-sidekick.com``)
    MAIL_GUN_API_URL   → base de la API (``https://api.eu.mailgun.net`` ó
                         ``https://api.mailgun.net``)
    MAIL_FROM          → dirección visible en "From:" y destinatario de los
                         formularios públicos (solicitud y contacto)

Funciones públicas:
    :func:`send_mail`             — primitiva reutilizable
    :func:`send_form_request`     — formulario de solicitud (alta)
    :func:`send_contact`          — formulario de contacto general
    :func:`send_welcome_company`  — bienvenida tras alta de empresa
    :func:`send_temp_password`    — contraseña temporal a usuario nuevo
"""

from __future__ import annotations

import logging
from html import escape

import requests
from flask import current_app

logger = logging.getLogger(__name__)

_TIMEOUT = 10
_FROM_DISPLAY_NAME = "Stay Sidekick"
_DEFAULT_API_URL = "https://api.eu.mailgun.net"


# ── Primitiva Mailgun ─────────────────────────────────────────────────────


def send_mail(
    to: str,
    subject: str,
    body_text: str,
    body_html: str | None = None,
) -> tuple[bool, str | None]:
    """Envía un email transaccional vía Mailgun HTTP API.

    Devuelve ``(True, None)`` si el envío fue exitoso o
    ``(False, mensaje_error)`` si falló. Nunca lanza excepción al caller.
    """
    cfg = current_app.config
    api_key = cfg.get("MAIL_GUN_API_KEY", "")
    domain = cfg.get("MAIL_GUN_DOMAIN", "")
    api_url = (cfg.get("MAIL_GUN_API_URL") or _DEFAULT_API_URL).rstrip("/")
    mail_from = cfg.get("MAIL_FROM") or (f"noreply@{domain}" if domain else "")

    if not api_key or not domain:
        return False, "Mailgun no configurado (MAIL_GUN_API_KEY / MAIL_GUN_DOMAIN)."

    if not to:
        return False, "Destinatario vacío."

    data = {
        "from": f"{_FROM_DISPLAY_NAME} <{mail_from}>",
        "to": to,
        "subject": subject,
        "text": body_text,
    }
    if body_html:
        data["html"] = body_html

    url = f"{api_url}/v3/{domain}/messages"

    try:
        response = requests.post(
            url,
            auth=("api", api_key),
            data=data,
            timeout=_TIMEOUT,
        )
    except requests.RequestException as exc:
        logger.exception("Error al enviar email vía Mailgun")
        return False, f"Error al enviar el email: {exc}"

    if not response.ok:
        logger.error(
            "Mailgun respondió %s al enviar a %s: %s",
            response.status_code,
            to,
            response.text,
        )
        return False, f"Error al enviar el email: HTTP {response.status_code}"

    return True, None


def _mail_configured() -> bool:
    cfg = current_app.config
    return bool(cfg.get("MAIL_GUN_API_KEY") and cfg.get("MAIL_GUN_DOMAIN"))


def _admin_recipient() -> str:
    """Buzón al que llegan los formularios públicos (``MAIL_FROM``)."""
    return current_app.config.get("MAIL_FROM", "") or ""


# ── Plantillas HTML ───────────────────────────────────────────────────────


_HTML_BASE = """\
<!DOCTYPE html>
<html lang="es">
  <head><meta charset="utf-8"><title>{title}</title></head>
  <body style="font-family:Arial,Helvetica,sans-serif;color:#1f2937;background:#f9fafb;margin:0;padding:24px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background:#ffffff;border-radius:8px;padding:24px;">
      <tr><td>
        <h1 style="font-size:18px;margin:0 0 16px 0;color:#0f172a;">{title}</h1>
        {content}
        <p style="font-size:12px;color:#6b7280;margin-top:32px;border-top:1px solid #e5e7eb;padding-top:12px;">
          Stay Sidekick — correo transaccional automatizado.
        </p>
      </td></tr>
    </table>
  </body>
</html>
"""


def _render_html(title: str, content_html: str) -> str:
    return _HTML_BASE.format(title=escape(title), content=content_html)


def _rows_html(rows: list[tuple[str, str]]) -> str:
    items = "".join(
        f'<tr><td style="padding:4px 12px 4px 0;color:#6b7280;">{escape(label)}</td>'
        f'<td style="padding:4px 0;">{escape(value or "—")}</td></tr>'
        for label, value in rows
    )
    return f'<table cellpadding="0" cellspacing="0" style="font-size:14px;">{items}</table>'


# ── Caso 1 — Formulario de solicitud (alta) ───────────────────────────────


def send_form_request(clean_data: dict) -> bool:
    """Envía al admin la notificación de una nueva solicitud de empresa."""
    if not _mail_configured():
        logger.warning("Mailgun no configurado; no se enviará form_request.")
        return False

    company = clean_data.get("company_name", "N/A")
    is_member = "Sí" if clean_data.get("is_member") else "No"
    mensaje = clean_data.get("message") or "(sin mensaje)"

    subject = f"[Stay Sidekick] Nueva solicitud de {company}"
    rows = [
        ("Empresa", company),
        ("Email", clean_data.get("company_email", "N/A")),
        ("Teléfono", clean_data.get("phone", "N/A")),
        ("Miembro", is_member),
    ]
    text_lines = [
        "Se ha recibido una nueva solicitud desde el formulario público.",
        "",
        *(f"{lbl}: {val}" for lbl, val in rows),
        "",
        "Mensaje:",
        mensaje,
    ]
    html = _render_html(
        "Nueva solicitud de empresa",
        _rows_html(rows)
        + f'<p style="font-size:14px;margin-top:16px;"><strong>Mensaje:</strong><br>{escape(mensaje)}</p>',
    )

    ok, _ = send_mail(_admin_recipient(), subject, "\n".join(text_lines), html)
    if ok:
        logger.info("form_request enviado para %s", company)
    return ok


# ── Caso 2 — Formulario de contacto general ───────────────────────────────


def send_contact(clean_data: dict) -> bool:
    """Envía al admin el mensaje del formulario de contacto general."""
    if not _mail_configured():
        logger.warning("Mailgun no configurado; no se enviará contacto.")
        return False

    nombre = clean_data.get("nombre", "N/A")
    email = clean_data.get("email", "N/A")
    empresa = clean_data.get("empresa") or "(sin empresa)"
    mensaje = clean_data.get("mensaje") or "(sin mensaje)"

    subject = f"[Stay Sidekick] Mensaje de contacto de {nombre}"
    rows = [("Nombre", nombre), ("Email", email), ("Empresa", empresa)]
    text_lines = [
        "Nuevo mensaje recibido desde el formulario de contacto.",
        "",
        *(f"{lbl}: {val}" for lbl, val in rows),
        "",
        "Mensaje:",
        mensaje,
    ]
    html = _render_html(
        "Nuevo mensaje de contacto",
        _rows_html(rows)
        + f'<p style="font-size:14px;margin-top:16px;"><strong>Mensaje:</strong><br>{escape(mensaje)}</p>',
    )

    ok, _ = send_mail(_admin_recipient(), subject, "\n".join(text_lines), html)
    if ok:
        logger.info("contacto enviado de %s", email)
    return ok


# ── Caso 3 — Bienvenida a nueva empresa ───────────────────────────────────


def send_welcome_company(empresa_email: str, empresa_nombre: str) -> bool:
    """Envía un correo de bienvenida al admin de la empresa recién creada."""
    if not _mail_configured():
        logger.warning("Mailgun no configurado; no se enviará bienvenida.")
        return False

    subject = f"Bienvenida a Stay Sidekick, {empresa_nombre}"
    text = (
        f"Hola {empresa_nombre},\n\n"
        "Tu cuenta de empresa en Stay Sidekick ha sido creada correctamente.\n"
        "En breve recibirás un correo separado con las credenciales del primer\n"
        "usuario administrador, incluida una contraseña temporal que deberás\n"
        "cambiar en el primer inicio de sesión.\n\n"
        "Si no esperabas este correo, ignóralo o contáctanos respondiendo a\n"
        "este mensaje.\n\n"
        "— El equipo de Stay Sidekick"
    )
    html = _render_html(
        f"Bienvenida, {empresa_nombre}",
        '<p style="font-size:14px;line-height:1.6;">'
        "Tu cuenta de empresa en <strong>Stay Sidekick</strong> ha sido "
        "creada correctamente. En breve recibirás un correo separado con las "
        "credenciales del primer usuario administrador, incluida una "
        "contraseña temporal que deberás cambiar en el primer inicio de sesión."
        "</p>"
        '<p style="font-size:14px;color:#6b7280;">'
        "Si no esperabas este correo, ignóralo o contáctanos respondiendo a "
        "este mensaje."
        "</p>",
    )

    ok, _ = send_mail(empresa_email, subject, text, html)
    if ok:
        logger.info("welcome_company enviado a %s", empresa_email)
    return ok


# ── Caso 4 — Contraseña temporal a usuario nuevo ──────────────────────────


def send_temp_password(usuario_email: str, password_temporal: str) -> bool:
    """Envía al usuario su contraseña temporal recién generada.

    La contraseña ya viene en claro desde el servicio (se generó con
    ``secrets.token_urlsafe`` y se ha hasheado inmediatamente en BD).
    """
    if not _mail_configured():
        logger.warning("Mailgun no configurado; no se enviará contraseña temporal.")
        return False

    subject = "Tu contraseña temporal de Stay Sidekick"
    text = (
        "Hola,\n\n"
        "Se ha creado tu cuenta en Stay Sidekick. Tu contraseña temporal es:\n\n"
        f"    {password_temporal}\n\n"
        "Por seguridad, te pediremos cambiarla la primera vez que inicies sesión.\n"
        "Si no esperabas este correo, ignóralo.\n\n"
        "— El equipo de Stay Sidekick"
    )
    pwd_html = escape(password_temporal)
    html = _render_html(
        "Tu contraseña temporal",
        '<p style="font-size:14px;line-height:1.6;">'
        "Se ha creado tu cuenta en <strong>Stay Sidekick</strong>. "
        "Esta es tu contraseña temporal:"
        "</p>"
        f'<p style="font-family:Consolas,Menlo,monospace;font-size:18px;'
        f"background:#f3f4f6;border:1px solid #e5e7eb;border-radius:6px;"
        f'padding:12px 16px;margin:16px 0;letter-spacing:1px;">{pwd_html}</p>'
        '<p style="font-size:14px;color:#6b7280;">'
        "Por seguridad, te pediremos cambiarla la primera vez que inicies sesión."
        "</p>",
    )

    ok, _ = send_mail(usuario_email, subject, text, html)
    if ok:
        logger.info("temp_password enviado a %s", usuario_email)
    return ok
