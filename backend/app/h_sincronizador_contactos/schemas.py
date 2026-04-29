"""Schemas Marshmallow para validación de payloads de Google Contacts."""

from marshmallow import Schema, fields, validate, pre_load


# Valores admitidos para las preferencias de formato
FORMATOS_NOMBRE = ("nombre_apellidos", "apellidos_nombre", "nombre_solo")
FORMATOS_APARTAMENTO = ("nota", "etiqueta", "ninguno")


class PreferenciasContactosSchema(Schema):
    """Validación para guardar preferencias de sincronización de contactos.

    Todos los campos son opcionales en el PUT para permitir updates parciales.
    """

    formato_nombre_contacto = fields.String(
        validate=validate.OneOf(FORMATOS_NOMBRE),
    )
    incluir_apartamento_contacto = fields.Boolean()
    formato_apartamento_contacto = fields.String(
        validate=validate.OneOf(FORMATOS_APARTAMENTO),
    )
    incluir_checkin_contacto = fields.Boolean()

    @pre_load
    def sanitize(self, data, **kwargs):
        if "formato_nombre_contacto" in data and isinstance(
            data["formato_nombre_contacto"], str
        ):
            data["formato_nombre_contacto"] = data["formato_nombre_contacto"].strip()
        if "formato_apartamento_contacto" in data and isinstance(
            data["formato_apartamento_contacto"], str
        ):
            data["formato_apartamento_contacto"] = data[
                "formato_apartamento_contacto"
            ].strip()
        return data


class SyncRangoSchema(Schema):
    """Parámetros opcionales para lanzar la sincronización de contactos."""

    desde = fields.Date(load_default=None)
    hasta = fields.Date(load_default=None)
