"""Verificación del captcha Cloudflare Turnstile."""

import logging

import requests
from flask import current_app

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 5


def verify_turnstile(token: str, remote_ip: str | None = None) -> bool:
    """Envía el token al endpoint de verificación de Turnstile.

    Returns True si Cloudflare confirma que el captcha es válido.
    """
    secret = current_app.config["TURNSTILE_SECRET_KEY"]
    url = current_app.config["TURNSTILE_VERIFY_URL"]

    payload = {
        "secret": secret,
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        resp = requests.post(url, data=payload, timeout=_TIMEOUT_SECONDS)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        logger.exception("Error al verificar Turnstile")
        return False

    success = data.get("success", False)
    if not success:
        error_codes = data.get("error-codes", [])
        logger.warning("Turnstile rechazado: %s", error_codes)

    return success
