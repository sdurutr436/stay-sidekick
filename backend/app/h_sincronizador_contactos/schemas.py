"""Schemas Marshmallow para validación de payloads de Google Contacts."""

from marshmallow import Schema, fields, validate


FORMATOS_FECHA_SALIDA = (
    "YYMMDD", "YYYYMMDD", "DD/MM/YYYY", "DD/MM/YY", "MM/DD/YYYY", "DD-MM-YYYY"
)


class _XlsxReservasColsSchema(Schema):
    col_checkin   = fields.Integer(load_default=0)
    col_nombre    = fields.Integer(load_default=0)
    col_tipologia = fields.Integer(load_default=0)
    col_telefono  = fields.Integer(load_default=0)


class PreferenciasContactosSchema(Schema):
    """Validación para guardar preferencias de sincronización de contactos.

    Todos los campos son opcionales en el PUT para permitir updates parciales.
    """

    plantilla = fields.String(load_default="{FECHA} - {APT} - {NOMBRE}")
    separador_apt = fields.String(load_default=", ")
    formato_fecha_salida = fields.String(
        validate=validate.OneOf(FORMATOS_FECHA_SALIDA),
        load_default="YYMMDD",
    )
    xlsx_reservas = fields.Nested(_XlsxReservasColsSchema, load_default=dict)


class SyncRangoSchema(Schema):
    """Parámetros opcionales para lanzar la sincronización de contactos."""

    desde = fields.Date(load_default=None)
    hasta = fields.Date(load_default=None)
