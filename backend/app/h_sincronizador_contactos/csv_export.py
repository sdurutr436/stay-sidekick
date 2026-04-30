"""Exportación CSV de contactos con cabeceras exactas de Google Contacts.

Permite la importación manual desde contacts.google.com cuando el flujo
OAuth no está disponible o cuando la empresa prefiere el control manual.

Solo tres campos tienen valor en el CSV:
- Name         → cadena compuesta con la plantilla configurada
- Group Membership → siempre "* myContacts"
- Phone 1 - Value  → teléfono del huésped

El resto de columnas se incluyen con valor vacío para mantener compatibilidad
con el formato CSV de importación de Google Contacts.
"""

import csv
import io
import logging

from app.h_sincronizador_contactos.contacto_formatter import (
    ContactoAgrupado,
    aplicar_plantilla,
)

logger = logging.getLogger(__name__)

_GOOGLE_CSV_HEADERS = [
    "Name",
    "Given Name",
    "Family Name",
    "Group Membership",
    "E-mail 1 - Type",
    "E-mail 1 - Value",
    "Phone 1 - Type",
    "Phone 1 - Value",
    "Notes",
]


def build_csv(contactos: list[ContactoAgrupado], preferencias: dict) -> bytes:
    """Genera el CSV de Google Contacts a partir de contactos agrupados.

    Parameters
    ----------
    contactos:
        Lista de ContactoAgrupado (ya filtrados por teléfono y agrupados).
    preferencias:
        Dict con plantilla, formato_fecha_salida y separador_apt.

    Returns
    -------
    bytes
        Contenido CSV en UTF-8 con BOM para compatibilidad con Excel.
    """
    plantilla = preferencias.get("plantilla", "{FECHA} - {APT} - {NOMBRE}")
    formato_fecha = preferencias.get("formato_fecha_salida", "YYMMDD")
    separador_apt = preferencias.get("separador_apt", ", ")

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=_GOOGLE_CSV_HEADERS,
        extrasaction="ignore",
        lineterminator="\r\n",
    )
    writer.writeheader()

    for contacto in contactos:
        nombre_compuesto = aplicar_plantilla(
            plantilla,
            contacto.checkin_date,
            contacto.apartamentos,
            contacto.nombre,
            formato_fecha,
            separador_apt,
        )
        writer.writerow({
            "Name": nombre_compuesto,
            "Given Name": "",
            "Family Name": "",
            "Group Membership": "* myContacts",
            "E-mail 1 - Type": "",
            "E-mail 1 - Value": "",
            "Phone 1 - Type": "",
            "Phone 1 - Value": contacto.telefono,
            "Notes": "",
        })

    logger.info("CSV contactos: %d filas generadas", len(contactos))
    return ("﻿" + output.getvalue()).encode("utf-8")
