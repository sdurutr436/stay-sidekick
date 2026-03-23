"""Protección honeypot contra bots simples.

Añade un campo oculto al formulario (``website`` o similar). Los usuarios
legítimos no lo rellenarán (está oculto con CSS), pero los bots que
parsean el HTML y rellenan todos los campos enviarán un valor.

Si el campo llega con contenido → bot → se rechaza silenciosamente.
"""

import logging

from flask import request

logger = logging.getLogger(__name__)

_HONEYPOT_FIELD = "website"


def check_honeypot(json_data: dict | None = None) -> bool:
    """Comprueba si el campo honeypot fue rellenado.

    Parameters
    ----------
    json_data:
        Datos JSON de la petición. Si no se pasa, se obtiene de
        ``request.get_json()``.

    Returns
    -------
    bool
        ``True`` si el honeypot está limpio (campo vacío o ausente).
        ``False`` si un bot rellenó el campo.
    """
    if json_data is None:
        json_data = request.get_json(silent=True) or {}

    value = json_data.get(_HONEYPOT_FIELD, "")

    if isinstance(value, str) and value.strip():
        logger.warning(
            "Honeypot activado: campo '%s' contenía '%s' — posible bot",
            _HONEYPOT_FIELD,
            value[:50],
        )
        return False

    return True
