"""Sanitización y limpieza de campos de texto libre y nombres."""

import re
import unicodedata

import nh3


# ── Configuración de nh3 ────────────────────────────────────────────────────
# No se permite ninguna etiqueta HTML en los campos del formulario.
_NH3_CLEAN_OPTS: dict = {
    "tags": set(),          # sin etiquetas permitidas → se elimina todo HTML
    "attributes": {},
    "strip_comments": True,
}

# Longitudes máximas por campo
MAX_LEN_NAME = 150
MAX_LEN_FREE_TEXT = 2000


def _normalize_unicode(value: str) -> str:
    """Normaliza a NFC y elimina caracteres de control invisibles."""
    value = unicodedata.normalize("NFC", value)
    # Elimina categorías Cc (control) y Cf (format) excepto \n y \t
    return "".join(
        ch for ch in value
        if ch in ("\n", "\t") or unicodedata.category(ch) not in ("Cc", "Cf")
    )


def _collapse_whitespace(value: str) -> str:
    """Colapsa espacios múltiples y elimina líneas vacías excesivas."""
    value = re.sub(r"[^\S\n]+", " ", value)   # espacios horizontales
    value = re.sub(r"\n{3,}", "\n\n", value)  # máx. 1 línea en blanco
    return value.strip()


def sanitize_text(value: str, *, max_length: int = MAX_LEN_FREE_TEXT) -> str:
    """Sanitiza un campo de texto libre.

    1. Normaliza Unicode (NFC) y elimina caracteres de control.
    2. Elimina todo HTML/XSS con nh3 (zero-tags).
    3. Colapsa espacios y trunca a *max_length*.
    """
    if not isinstance(value, str):
        return ""
    value = _normalize_unicode(value)
    value = nh3.clean(value, **_NH3_CLEAN_OPTS)
    value = _collapse_whitespace(value)
    return value[:max_length]


def sanitize_name(value: str, *, max_length: int = MAX_LEN_NAME) -> str:
    """Sanitiza un nombre (empresa, persona, etc.).

    Aplica las mismas reglas que ``sanitize_text`` pero además:
    - Elimina saltos de línea (un nombre no los necesita).
    - Rechaza valores que queden vacíos tras la limpieza.
    """
    value = sanitize_text(value, max_length=max_length)
    value = re.sub(r"\s+", " ", value)  # todo whitespace → espacio simple
    return value.strip()
