"""Autenticación JWT para rutas protegidas (panel de usuario).

Usa ``PyJWT`` para firmar y verificar tokens HS256. Pensado para las
rutas autenticadas del panel (heatmaps, notificaciones, vault, etc.).

Configuración necesaria en .env:
    JWT_SECRET_KEY         → clave secreta para firmar tokens
    JWT_ACCESS_TOKEN_HOURS → duración del token en horas (default: 1)
"""

import logging
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

logger = logging.getLogger(__name__)

_ALGORITHM = "HS256"


def create_access_token(identity: str, extra_claims: dict | None = None) -> str:
    """Genera un JWT firmado con HS256.

    Parameters
    ----------
    identity:
        Identificador del usuario (email, user_id, etc.).
    extra_claims:
        Claims adicionales a incluir en el payload.

    Returns
    -------
    str
        Token JWT codificado.
    """
    secret = current_app.config["JWT_SECRET_KEY"]
    hours = current_app.config.get("JWT_ACCESS_TOKEN_HOURS", 1)

    now = datetime.now(timezone.utc)
    payload = {
        "sub": identity,
        "iat": now,
        "exp": now + timedelta(hours=hours),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, secret, algorithm=_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Decodifica y verifica un JWT.

    Returns
    -------
    dict | None
        Claims del token o ``None`` si es inválido/expirado.
    """
    secret = current_app.config["JWT_SECRET_KEY"]
    try:
        return jwt.decode(token, secret, algorithms=[_ALGORITHM])
    except jwt.ExpiredSignatureError:
        logger.warning("JWT expirado")
        return None
    except jwt.InvalidTokenError:
        logger.warning("JWT inválido")
        return None


def jwt_required(f):
    """Decorador que exige un JWT válido en ``Authorization: Bearer <token>``.

    Si el token es válido, almacena los claims en ``g.jwt_claims``
    y la identidad en ``g.jwt_identity``.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"ok": False, "errors": ["Token de acceso requerido."]}), 401

        token = auth_header[7:]  # quita "Bearer "
        claims = decode_token(token)

        if claims is None:
            return jsonify({"ok": False, "errors": ["Token inválido o expirado."]}), 401

        g.jwt_claims = claims
        g.jwt_identity = claims.get("sub")

        return f(*args, **kwargs)
    return decorated
