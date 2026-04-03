"""Servicio de autenticación — validación y sanitización del payload de login.

La verificación real de credenciales (consulta a BD) se añadirá en el
siguiente commit cuando se integre el modelo de usuario.
"""

import logging

from marshmallow import ValidationError

from app.auth.schemas import LoginSchema
from app.common.sanitizers.email import sanitize_email

logger = logging.getLogger(__name__)

_schema = LoginSchema()


def sanitize_login_payload(json_data: dict) -> tuple[dict, list[str]]:
    """Sanitiza y valida el payload de login.

    Aplica el mismo patrón que ``process_contact_form``:
    1. Pre-load: sanitización de campos (schemas.py @pre_load).
    2. Validación Marshmallow (longitudes, formato email, password imprimible).
    3. Normalización final del email con email-validator.

    Returns
    -------
    tuple[dict, list[str]]
        (datos_limpios, errores). Si ``errores`` está vacío los datos
        son seguros para continuar con la verificación de credenciales.
    """
    try:
        clean_data: dict = _schema.load(json_data)
    except ValidationError as exc:
        return {}, _flatten_errors(exc.messages)

    # Normalización final del email (E.164 equivalente para emails)
    normalized_email = sanitize_email(clean_data["email"])
    if normalized_email is None:
        return {}, ["El correo electrónico no es válido."]
    clean_data["email"] = normalized_email

    # El campo 'origen' es informativo — se registra en log pero no se usa
    logger.debug("Login intentado desde origen='%s' para email='%s'",
                 clean_data.get("origen"), clean_data["email"])

    return clean_data, []


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
