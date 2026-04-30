"""Helpers de formato para el sincronizador de contactos."""

import re
from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class ContactoAgrupado:
    nombre: str
    telefono: str
    checkin_date: date | None
    apartamentos: list[str] = field(default_factory=list)


def parsear_fecha(valor) -> date | None:
    """Parsea fecha desde múltiples formatos de entrada.

    Soporta: objeto date, YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY,
    YYYY/MM/DD, DD/MM/YY, MM/DD/YYYY, DD.MM.YYYY.
    """
    if valor is None:
        return None
    if isinstance(valor, date):
        return valor

    s = str(valor).strip()
    if not s:
        return None

    # YYYY-MM-DD (ISO / Smoobu)
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        try:
            return datetime.strptime(s[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    # YYYY/MM/DD
    if re.match(r"^\d{4}/\d{2}/\d{2}$", s):
        try:
            return datetime.strptime(s, "%Y/%m/%d").date()
        except ValueError:
            return None

    # DD.MM.YYYY
    if re.match(r"^\d{1,2}\.\d{1,2}\.\d{4}$", s):
        try:
            return datetime.strptime(s, "%d.%m.%Y").date()
        except ValueError:
            return None

    # DD-MM-YYYY
    if re.match(r"^\d{1,2}-\d{1,2}-\d{4}$", s):
        try:
            return datetime.strptime(s, "%d-%m-%Y").date()
        except ValueError:
            return None

    # Barra con año de 4 dígitos: DD/MM/YYYY o MM/DD/YYYY
    # Si el primer número > 12 → debe ser día (DD/MM/YYYY)
    # Si el segundo número > 12 → debe ser día (MM/DD/YYYY)
    # Ambiguo → contexto europeo: DD/MM/YYYY
    if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", s):
        partes = s.split("/")
        a, b = int(partes[0]), int(partes[1])
        if a > 12:
            fmt = "%d/%m/%Y"
        elif b > 12:
            fmt = "%m/%d/%Y"
        else:
            fmt = "%d/%m/%Y"
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            return None

    # DD/MM/YY (año de 2 dígitos)
    if re.match(r"^\d{1,2}/\d{1,2}/\d{2}$", s):
        try:
            return datetime.strptime(s, "%d/%m/%y").date()
        except ValueError:
            return None

    return None


def parsear_telefono(valor) -> str | None:
    """Parsea teléfono manejando notación científica de Excel (int/float → str)."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        s = str(int(valor))
    else:
        s = str(valor).strip()
    if not s or s in ("+", "0") or s.startswith("+0") or len(s) <= 5:
        return None
    return s


def formatear_fecha_salida(d: date, formato: str) -> str:
    """Formatea una fecha según el formato de salida configurado."""
    opciones = {
        "YYMMDD":     lambda x: x.strftime("%y%m%d"),
        "YYYYMMDD":   lambda x: x.strftime("%Y%m%d"),
        "DD/MM/YYYY": lambda x: x.strftime("%d/%m/%Y"),
        "DD/MM/YY":   lambda x: x.strftime("%d/%m/%y"),
        "MM/DD/YYYY": lambda x: x.strftime("%m/%d/%Y"),
        "DD-MM-YYYY": lambda x: x.strftime("%d-%m-%Y"),
    }
    return opciones.get(formato, opciones["YYMMDD"])(d)


def aplicar_plantilla(
    plantilla: str,
    fecha: date | None,
    apartamentos: list[str],
    nombre: str,
    formato_fecha: str,
    separador_apt: str,
) -> str:
    """Aplica la plantilla de nombre de contacto con los tokens dados.

    Tokens: {FECHA}, {APT}, {NOMBRE}.
    """
    fecha_str = formatear_fecha_salida(fecha, formato_fecha) if fecha else ""
    apt_str = separador_apt.join(apartamentos) if apartamentos else ""
    result = plantilla.replace("{FECHA}", fecha_str)
    result = result.replace("{APT}", apt_str)
    result = result.replace("{NOMBRE}", nombre)
    return result.strip()


def agrupar_contactos(registros: list[dict]) -> list[ContactoAgrupado]:
    """Agrupa registros por clave nombre+teléfono, combinando apartamentos.

    Cada registro debe tener: nombre (str), telefono (str, ya parseado),
    checkin_date (date|None), apartamentos (list[str]).
    """
    grupos: dict[tuple, ContactoAgrupado] = {}
    for rec in registros:
        tel = rec["telefono"]
        nombre = rec["nombre"]
        clave = (nombre.lower().strip(), tel)
        if clave not in grupos:
            grupos[clave] = ContactoAgrupado(
                nombre=nombre,
                telefono=tel,
                checkin_date=rec.get("checkin_date"),
                apartamentos=[],
            )
        grupo = grupos[clave]
        for apt in rec.get("apartamentos", []):
            if apt and apt not in grupo.apartamentos:
                grupo.apartamentos.append(apt)
        ci = rec.get("checkin_date")
        if ci and (grupo.checkin_date is None or ci < grupo.checkin_date):
            grupo.checkin_date = ci
    return list(grupos.values())
