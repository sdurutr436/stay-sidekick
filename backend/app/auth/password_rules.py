"""Reglas de fortaleza para contraseñas nuevas.

Fuente de verdad única para la validación de contraseñas en el backend.
Reflejada en:
- web/src/assets/js/password-rules.js (formulario estático en 11ty)
- frontend/src/app/validators/password-strength.validator.ts (SPA Angular)

Reglas:
- Entre 8 y 20 caracteres (el máximo es secreto para el usuario).
- Al menos una letra mayúscula, una minúscula, un número
  y un carácter especial de la lista permitida.
"""

import re

MIN_LENGTH = 8
MAX_LENGTH = 20

# Lista de especiales sincronizada con password-rules.js y el validador Angular.
SPECIAL_CHARS = "!@#$%^&*-_=+.,;:?"

# Regex equivalente para uso externo (auditoría, tests cruzados).
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*\-_=+.,;:?]).{8,20}$"
)

_RE_UPPER   = re.compile(r"[A-Z]")
_RE_LOWER   = re.compile(r"[a-z]")
_RE_DIGIT   = re.compile(r"\d")
_RE_SPECIAL = re.compile(r"[!@#$%^&*\-_=+.,;:?]")


def validate_password(pwd: str) -> str | None:
    """Valida una contraseña nueva contra las reglas de fortaleza.

    Parameters
    ----------
    pwd:
        Contraseña en claro propuesta por el usuario.

    Returns
    -------
    str | None
        ``None`` si la contraseña es válida, o un mensaje descriptivo
        del primer criterio incumplido.
    """
    if not isinstance(pwd, str) or not pwd:
        return "La contraseña es obligatoria."
    if len(pwd) < MIN_LENGTH:
        return f"La contraseña debe tener al menos {MIN_LENGTH} caracteres."
    if len(pwd) > MAX_LENGTH:
        return f"La contraseña no puede superar los {MAX_LENGTH} caracteres."
    if not _RE_UPPER.search(pwd):
        return "La contraseña debe contener al menos una letra mayúscula."
    if not _RE_LOWER.search(pwd):
        return "La contraseña debe contener al menos una letra minúscula."
    if not _RE_DIGIT.search(pwd):
        return "La contraseña debe contener al menos un número."
    if not _RE_SPECIAL.search(pwd):
        return "La contraseña debe contener al menos un carácter especial."
    return None
