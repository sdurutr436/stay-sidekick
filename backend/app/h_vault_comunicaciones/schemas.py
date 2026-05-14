"""Schemas Marshmallow del Vault de comunicaciones."""

from marshmallow import Schema, fields, validate

_IDIOMAS = ("es", "en", "fr", "de", "it", "pt")
_TONOS = ("clasico", "cercano", "entusiasta", "minimalista")


class PlantillaResponseSchema(Schema):
    id = fields.Str(dump_only=True)
    nombre = fields.Str(dump_only=True)
    contenido = fields.Str(dump_only=True)
    idioma = fields.Str(dump_only=True)
    categoria = fields.Str(dump_only=True, allow_none=True)
    activa = fields.Bool(dump_only=True)
_CATEGORIAS = (
    "BIENVENIDA",
    "INSTRUCCIONES",
    "RECORDATORIO",
    "CHECKIN_TARDIO",
    "CHECKOUT",
    "INCIDENCIA",
    "GENERAL",
)


class CrearPlantillaSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    contenido = fields.Str(required=True, validate=validate.Length(min=1))
    idioma = fields.Str(load_default="es", validate=validate.OneOf(_IDIOMAS))
    categoria = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(_CATEGORIAS))


class ActualizarPlantillaSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    contenido = fields.Str(required=True, validate=validate.Length(min=1))
    idioma = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(_IDIOMAS))
    categoria = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(_CATEGORIAS))


class MejorarSchema(Schema):
    contenido = fields.Str(required=True, validate=validate.Length(min=1))
    idioma = fields.Str(required=True, validate=validate.OneOf(_IDIOMAS))
    tono = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(_TONOS))


class TraducirSchema(Schema):
    contenido = fields.Str(required=True, validate=validate.Length(min=1))
    idioma_destino = fields.Str(required=True, validate=validate.OneOf(_IDIOMAS))
