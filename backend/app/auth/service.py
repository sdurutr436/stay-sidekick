"""Servicio de autenticación — sanitización, validación y verificación de credenciales."""

import logging

from marshmallow import ValidationError

from app.auth.schemas import LoginSchema
from app.auth.passwords import verify_password
from app.auth.user_repository import find_user_by_email
from app.common.sanitizers.email import sanitize_email
from app.security.jwt import create_access_token

logger = logging.getLogger(__name__)

_schema = LoginSchema()

# Mensaje genérico para no revelar si el email existe en la BD
_INVALID_CREDENTIALS_MSG = "Credenciales incorrectas."


def sanitize_login_payload(json_data: dict) -> tuple[dict, list[str]]:
    """Sanitiza y valida el payload de login.

    1. Pre-load: sanitización de campos (schemas.py @pre_load).
    2. Validación Marshmallow (longitudes, formato email, password imprimible).
    3. Normalización final del email con email-validator.

    Returns
    -------
    tuple[dict, list[str]]
        (datos_limpios, errores).
    """
    try:
        clean_data: dict = _schema.load(json_data)
    except ValidationError as exc:
        return {}, _flatten_errors(exc.messages)

    normalized_email = sanitize_email(clean_data["email"])
    if normalized_email is None:
        return {}, ["El correo electrónico no es válido."]
    clean_data["email"] = normalized_email

    logger.debug("Payload de login sanitizado para origen='%s'", clean_data.get("origen"))

    return clean_data, []


def authenticate_user(clean_data: dict) -> tuple[str | None, list[str]]:
    """Verifica las credenciales y emite un JWT si son válidas.

    Parameters
    ----------
    clean_data:
        Datos ya sanitizados por ``sanitize_login_payload``.

    Returns
    -------
    tuple[str | None, list[str]]
        (token_jwt, errores). Si ``errores`` está vacío, el token es válido.
    """
    email    = clean_data["email"]
    password = clean_data["password"]

    user = find_user_by_email(email)

    # Misma respuesta tanto si el email no existe como si la contraseña falla
    # → no revelar información sobre qué campo es incorrecto
    if user is None or not user.get("is_active", False):
        logger.warning("Login fallido — usuario no encontrado o inactivo: %s", email)
        return None, [_INVALID_CREDENTIALS_MSG]

    if not verify_password(password, user["password_hash"]):
        logger.warning("Login fallido — contraseña incorrecta para: %s", email)
        return None, [_INVALID_CREDENTIALS_MSG]

    token = create_access_token(
        identity=email,
        extra_claims={"user_id": user["id"]},
    )

    logger.info("Login correcto para: %s", email)
    return token, []


def _flatten_errors(messages: dict) -> list[str]:
    """Convierte los errores anidados de Marshmallow en lista plana."""
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
