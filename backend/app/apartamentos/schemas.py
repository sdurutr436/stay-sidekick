"""Schemas Marshmallow para validación de payloads de apartamentos."""

from marshmallow import Schema, fields, validate, pre_load

import nh3


def _strip_html(value: str) -> str:
    """Elimina HTML y recorta espacios."""
    if not isinstance(value, str):
        return value
    return nh3.clean(value, tags=set()).strip()


class ApartamentoCreateSchema(Schema):
    """Validación para alta manual de un apartamento."""
    id_externo = fields.String(
        load_default=None,
        validate=validate.Length(max=100),
    )
    nombre = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
    )
    direccion = fields.String(
        load_default=None,
        validate=validate.Length(max=300),
    )
    ciudad = fields.String(
        load_default=None,
        validate=validate.Length(max=100),
    )

    @pre_load
    def sanitize(self, data, **kwargs):
        for field in ("nombre", "direccion", "ciudad", "id_externo"):
            if field in data and isinstance(data[field], str):
                data[field] = _strip_html(data[field])
        return data


class ApartamentoUpdateSchema(Schema):
    """Validación para actualización parcial de un apartamento.

    Ningún campo tiene load_default para evitar que Marshmallow inyecte None
    en updates parciales y sobreescriba datos existentes en BD.
    """
    nombre = fields.String(
        validate=validate.Length(min=1, max=200),
    )
    direccion = fields.String(
        validate=validate.Length(max=300),
        allow_none=True,
    )
    ciudad = fields.String(
        validate=validate.Length(max=100),
        allow_none=True,
    )

    @pre_load
    def sanitize(self, data, **kwargs):
        for field in ("nombre", "direccion", "ciudad"):
            if field in data and isinstance(data[field], str):
                data[field] = _strip_html(data[field])
        return data


class PMSConfigSchema(Schema):
    """Validación para guardar configuración del PMS."""
    proveedor = fields.String(
        required=True,
        validate=validate.OneOf(["smoobu", "beds24", "hostaway", "cloudbeds"]),
    )
    api_key = fields.String(
        required=True,
        validate=validate.Length(min=1, max=500),
    )
    endpoint = fields.String(
        load_default=None,
        validate=validate.Length(max=500),
    )
