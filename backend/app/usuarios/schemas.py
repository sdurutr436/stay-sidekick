"""Schemas Marshmallow del módulo de usuarios."""

from marshmallow import Schema, ValidationError, fields, pre_load, validates

from app.usuarios.model import ROLES_VALIDOS


class UsuarioCreateSchema(Schema):
    email = fields.String(required=True)
    rol = fields.String(required=True)

    @pre_load
    def sanitizar(self, data, **kwargs):
        if isinstance(data.get("email"), str):
            data["email"] = data["email"].strip().lower()
        if isinstance(data.get("rol"), str):
            data["rol"] = data["rol"].strip().lower()
        return data

    @validates("email")
    def validate_email(self, value):
        if not value or len(value) > 254:
            raise ValidationError("El correo electrónico no es válido.")

    @validates("rol")
    def validate_rol(self, value):
        if value not in ROLES_VALIDOS:
            raise ValidationError(f"Rol inválido. Opciones: {', '.join(ROLES_VALIDOS)}.")


class UsuarioPatchSchema(Schema):
    rol = fields.String(required=True)

    @pre_load
    def sanitizar(self, data, **kwargs):
        if isinstance(data.get("rol"), str):
            data["rol"] = data["rol"].strip().lower()
        return data

    @validates("rol")
    def validate_rol(self, value):
        if value not in ROLES_VALIDOS:
            raise ValidationError(f"Rol inválido. Opciones: {', '.join(ROLES_VALIDOS)}.")
