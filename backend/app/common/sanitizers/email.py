"""Validación y normalización de direcciones de correo electrónico."""

from email_validator import EmailNotValidError, validate_email

MAX_LEN_EMAIL = 254  # RFC 5321


def sanitize_email(value: str) -> str | None:
    """Valida y normaliza un email.

    Usa ``email-validator`` que comprueba:
    - Sintaxis RFC 5322
    - Dominio con registro DNS (MX o A) cuando está disponible
    - Normalización de la parte local y del dominio (IDNA/punycode)

    Returns
    -------
    str | None
        Email normalizado o ``None`` si es inválido.
    """
    if not isinstance(value, str) or not value.strip():
        return None

    if len(value) > MAX_LEN_EMAIL:
        return None

    try:
        result = validate_email(value.strip(), check_deliverability=False)
        return result.normalized
    except EmailNotValidError:
        return None
