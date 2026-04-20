"""Schemas Marshmallow para el módulo de perfil de usuario."""

from marshmallow import Schema, fields, validate

_PMS_PROVEEDORES = ("smoobu", "beds24", "hostaway", "cloudbeds")
_IA_PROVEEDORES  = ("default", "gemini", "openai", "claude")


class CambiarPasswordSchema(Schema):
    password_actual = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    password_nueva  = fields.Str(required=True, validate=validate.Length(min=8, max=128))


class ActualizarPMSSchema(Schema):
    proveedor = fields.Str(required=True, validate=validate.OneOf(_PMS_PROVEEDORES))
    api_key   = fields.Str(required=True, validate=validate.Length(min=1, max=500))


class ActualizarIASchema(Schema):
    proveedor = fields.Str(required=True, validate=validate.OneOf(_IA_PROVEEDORES))
    modelo    = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=100))
    api_key   = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=500))
