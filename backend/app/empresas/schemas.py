"""Schemas Marshmallow del módulo de empresas."""

from marshmallow import Schema, fields, validate


class CrearEmpresaSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    email = fields.Email(required=True)
