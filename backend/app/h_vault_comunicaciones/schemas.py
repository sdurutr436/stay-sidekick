"""Schemas Marshmallow del Vault de comunicaciones."""

from marshmallow import Schema, fields, validate

_IDIOMAS = ("es", "en", "fr", "de", "it", "pt")
_TONOS = ("clasico", "cercano", "entusiasta", "minimalista")
_IDIOMAS_TEXTO = ", ".join(_IDIOMAS)
_CATEGORIAS = (
    "BIENVENIDA",
    "INSTRUCCIONES",
    "RECORDATORIO",
    "CHECKIN_TARDIO",
    "CHECKOUT",
    "INCIDENCIA",
    "GENERAL",
)
_CATEGORIAS_TEXTO = ", ".join(_CATEGORIAS)
_TONOS_TEXTO = ", ".join(_TONOS)


class PlantillaResponseSchema(Schema):
    id = fields.Str(dump_only=True)
    nombre = fields.Str(dump_only=True)
    contenido = fields.Str(dump_only=True)
    idioma = fields.Str(dump_only=True)
    categoria = fields.Str(dump_only=True, allow_none=True)
    activa = fields.Bool(dump_only=True)


class CrearPlantillaSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=200, error="El nombre debe tener entre 1 y 200 caracteres."))
    contenido = fields.Str(required=True, validate=validate.Length(min=1, error="El contenido no puede estar vacío."))
    idioma = fields.Str(load_default="es", validate=validate.OneOf(_IDIOMAS, error=f"Idioma no válido. Opciones: {_IDIOMAS_TEXTO}."))
    categoria = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(_CATEGORIAS, error=f"Categoría no válida. Opciones: {_CATEGORIAS_TEXTO}."))


class ActualizarPlantillaSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=200, error="El nombre debe tener entre 1 y 200 caracteres."))
    contenido = fields.Str(required=True, validate=validate.Length(min=1, error="El contenido no puede estar vacío."))
    idioma = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(_IDIOMAS, error=f"Idioma no válido. Opciones: {_IDIOMAS_TEXTO}."))
    categoria = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(_CATEGORIAS, error=f"Categoría no válida. Opciones: {_CATEGORIAS_TEXTO}."))


class MejorarSchema(Schema):
    contenido = fields.Str(required=True, validate=validate.Length(min=1, error="El contenido no puede estar vacío."))
    idioma = fields.Str(required=True, validate=validate.OneOf(_IDIOMAS, error=f"Idioma no válido. Opciones: {_IDIOMAS_TEXTO}."))
    tono = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(_TONOS, error=f"Tono no válido. Opciones: {_TONOS_TEXTO}."))


class TraducirSchema(Schema):
    contenido = fields.Str(required=True, validate=validate.Length(min=1, error="El contenido no puede estar vacío."))
    idioma_destino = fields.Str(required=True, validate=validate.OneOf(_IDIOMAS, error=f"Idioma no válido. Opciones: {_IDIOMAS_TEXTO}."))
