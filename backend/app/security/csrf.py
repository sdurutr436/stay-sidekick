"""Protección CSRF stateless mediante Double-Submit Cookie.

Patrón:
1. El backend genera un token aleatorio y lo envía como cookie
   (``SameSite=Strict``, ``HttpOnly=False`` para que JS pueda leerlo).
2. El frontend lo lee y lo reenvía en la cabecera ``X-CSRF-Token``.
3. El backend compara cookie vs cabecera — si coinciden, la petición
   es legítima (un atacante CSRF desde otro dominio no puede leer la
   cookie gracias a SameSite + CORS).

No requiere sesión ni estado en el servidor.
"""

import logging
import os
import secrets

from functools import wraps

from flask import request, jsonify

logger = logging.getLogger(__name__)

_COOKIE_NAME = "csrf_token"
_HEADER_NAME = "X-CSRF-Token"
_TOKEN_BYTES = 32  # 256 bits


def generate_csrf_token() -> str:
    """Genera un token CSRF criptográficamente seguro."""
    return secrets.token_urlsafe(_TOKEN_BYTES)


def set_csrf_cookie(response, token: str):
    """Añade la cookie CSRF a una respuesta Flask."""
    response.set_cookie(
        _COOKIE_NAME,
        value=token,
        httponly=False,       # JS necesita leerlo para la cabecera
        samesite="Strict",
        secure=os.environ.get("FLASK_ENV", "production") != "development",
        max_age=3600,         # 1 hora
        path="/",
    )
    return response


def csrf_protect(f):
    """Decorador que valida el token CSRF (Double-Submit Cookie).

    Compara el token de la cookie ``csrf_token`` con el valor
    de la cabecera ``X-CSRF-Token``. Si no coinciden o faltan,
    devuelve 403.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        cookie_token = request.cookies.get(_COOKIE_NAME)
        header_token = request.headers.get(_HEADER_NAME)

        if not cookie_token or not header_token:
            logger.warning("CSRF: token ausente (cookie=%s, header=%s)",
                           bool(cookie_token), bool(header_token))
            return jsonify({"ok": False, "errors": ["Token CSRF ausente."]}), 403

        if not secrets.compare_digest(cookie_token, header_token):
            logger.warning("CSRF: token no coincide")
            return jsonify({"ok": False, "errors": ["Token CSRF inválido."]}), 403

        return f(*args, **kwargs)
    return decorated
