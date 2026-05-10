"""Schemas Marshmallow del módulo de empresas."""

from marshmallow import Schema, fields, validate


class EmpresaResponseSchema(Schema):
    id = fields.Str(dump_only=True)
    nombre = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    # password_hash excluido: no se declara → nunca aparece en el dump


class CrearEmpresaSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    email = fields.Email(required=True)
