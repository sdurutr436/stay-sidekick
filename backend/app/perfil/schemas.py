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


class XlsxApartamentosConfigSchema(Schema):
    col_id_externo = fields.Int(required=True, validate=validate.Range(min=0, max=200))
    col_nombre     = fields.Int(required=True, validate=validate.Range(min=0, max=200))
    col_direccion  = fields.Int(load_default=0, validate=validate.Range(min=0, max=200))
    col_ciudad     = fields.Int(load_default=0, validate=validate.Range(min=0, max=200))


_COL_LETRA_RE = r"^[A-Za-z]{0,2}$"
_HORA_CORTE_RE = r"^([01]\d|2[0-3]):[0-5]\d$"


class NotifTardioConfigSchema(Schema):
    hora_corte        = fields.Str(required=True, validate=validate.Regexp(_HORA_CORTE_RE))
    col_nombre        = fields.Str(load_default="", validate=validate.Regexp(_COL_LETRA_RE))
    col_checkin       = fields.Str(load_default="", validate=validate.Regexp(_COL_LETRA_RE))
    col_hora_llegada  = fields.Str(load_default="", validate=validate.Regexp(_COL_LETRA_RE))
    col_telefono      = fields.Str(load_default="", validate=validate.Regexp(_COL_LETRA_RE))
    col_apartamento   = fields.Str(load_default="", validate=validate.Regexp(_COL_LETRA_RE))
