"""Exportación CSV de contactos con cabeceras exactas de Google Contacts.

Permite la importación manual desde contacts.google.com cuando el flujo
OAuth no está disponible o cuando la empresa prefiere el control manual.

El formato respeta exactamente las columnas que espera Google Contacts
en su importación CSV:
https://support.google.com/contacts/answer/1069522
"""

import csv
import io
import logging

from app.pms.base import ReservaEstandar

logger = logging.getLogger(__name__)

# Cabeceras exactas de Google Contacts CSV
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

# Separador de grupos en el CSV de Google
_GROUP_SEP = " ::: "


def build_csv(
    reservas: list[ReservaEstandar],
    preferencias: dict,
) -> bytes:
    """Genera el CSV de contactos en formato Google a partir de reservas.

    Parameters
    ----------
    reservas:
        Lista de reservas normalizadas del PMS.
    preferencias:
        Dict con las claves de configuración de la empresa:
        - formato_nombre_contacto
        - incluir_apartamento_contacto
        - formato_apartamento_contacto  ('nota' | 'etiqueta' | 'ninguno')
        - incluir_checkin_contacto

    Returns
    -------
    bytes
        Contenido del fichero CSV codificado en UTF-8 con BOM (para
        compatibilidad con Excel y Google Sheets en Windows).
    """
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=_GOOGLE_CSV_HEADERS,
        extrasaction="ignore",
        lineterminator="\r\n",
    )
    writer.writeheader()

    for reserva in reservas:
        row = _reserva_to_row(reserva, preferencias)
        if row:
            writer.writerow(row)

    logger.info("CSV contactos: %d filas generadas", len(reservas))
    # UTF-8 BOM para compatibilidad con Excel/Google Sheets
    return ("\ufeff" + output.getvalue()).encode("utf-8")


def _reserva_to_row(reserva: ReservaEstandar, preferencias: dict) -> dict | None:
    """Convierte una ReservaEstandar en una fila del CSV de Google."""
    given_name, family_name = _split_nombre(reserva.nombre_raw)
    if not given_name and not family_name:
        return None

    formato_nombre = preferencias.get("formato_nombre_contacto", "nombre_apellidos")
    display_name = _format_display_name(given_name, family_name, formato_nombre)

    notas = _build_notas(reserva, preferencias)
    grupo = _build_grupo(reserva, preferencias)

    return {
        "Name": display_name,
        "Given Name": given_name,
        "Family Name": family_name,
        "Group Membership": grupo,
        "E-mail 1 - Type": "* Work" if reserva.email else "",
        "E-mail 1 - Value": reserva.email or "",
        "Phone 1 - Type": "* Mobile" if reserva.telefono else "",
        "Phone 1 - Value": reserva.telefono or "",
        "Notes": notas,
    }


def _split_nombre(nombre_raw: str) -> tuple[str, str]:
    """Separa nombre y apellidos a partir del formato del PMS.

    Convenciones detectadas:
    - "Apellido Apellido, Nombre"  → ('Nombre', 'Apellido Apellido')
    - "Nombre Apellido"            → ('Nombre', 'Apellido')   [heurística]
    - "Nombre"                     → ('Nombre', '')
    """
    if "," in nombre_raw:
        apellidos, _, nombre = nombre_raw.partition(",")
        return nombre.strip(), apellidos.strip()

    parts = nombre_raw.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    if len(parts) == 2:
        return parts[0], parts[1]
    # Más de 2 palabras sin coma: primer token = nombre, resto = apellidos
    return parts[0], " ".join(parts[1:])


def _format_display_name(given: str, family: str, formato: str) -> str:
    if formato == "apellidos_nombre":
        return f"{family}, {given}".strip(", ") if family else given
    if formato == "nombre_solo":
        return given
    # nombre_apellidos (defecto)
    return f"{given} {family}".strip()


def _build_notas(reserva: ReservaEstandar, preferencias: dict) -> str:
    partes: list[str] = []

    if preferencias.get("incluir_checkin_contacto", True) and reserva.checkin:
        partes.append(f"Checkin: {reserva.checkin}")

    if (
        preferencias.get("incluir_apartamento_contacto", True)
        and preferencias.get("formato_apartamento_contacto") == "nota"
        and reserva.nombre_apartamento
    ):
        partes.append(f"Apartamento: {reserva.nombre_apartamento}")

    return "\n".join(partes)


def _build_grupo(reserva: ReservaEstandar, preferencias: dict) -> str:
    """Construye la columna Group Membership para etiquetas."""
    grupos: list[str] = ["* myContacts"]

    if (
        preferencias.get("incluir_apartamento_contacto", True)
        and preferencias.get("formato_apartamento_contacto") == "etiqueta"
        and reserva.nombre_apartamento
    ):
        grupos.append(reserva.nombre_apartamento)

    return _GROUP_SEP.join(grupos)
