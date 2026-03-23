"""Validación y normalización de números de teléfono con phonenumbers."""

import phonenumbers
from phonenumbers import NumberParseException


def sanitize_phone(number: str, country_code: str = "ES") -> str | None:
    """Parsea, valida y devuelve el teléfono en formato E.164.

    Parameters
    ----------
    number:
        Número tal como lo introduce el usuario (puede incluir prefijo).
    country_code:
        Código ISO 3166-1 alpha-2 del país seleccionado en el frontend.
        Se usa como hint si el número no incluye prefijo internacional.

    Returns
    -------
    str | None
        Número en formato E.164 (ej. ``+34612345678``) o ``None`` si es
        inválido.
    """
    if not isinstance(number, str) or not number.strip():
        return None

    try:
        parsed = phonenumbers.parse(number.strip(), country_code.upper())
    except NumberParseException:
        return None

    if not phonenumbers.is_valid_number(parsed):
        return None

    return phonenumbers.format_number(
        parsed, phonenumbers.PhoneNumberFormat.E164
    )
