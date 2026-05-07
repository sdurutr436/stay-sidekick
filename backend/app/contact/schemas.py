"""Esquema Marshmallow para el formulario de contacto de /empresa/contacto."""

from marshmallow import EXCLUDE, Schema, ValidationError, fields, pre_load, validate, validates

from app.common.sanitizers.email import sanitize_email
from app.common.sanitizers.text import sanitize_name, sanitize_text


class ContactoMessageSchema(Schema):
    """Valida y sanitiza los datos del formulario de contacto general."""

    class Meta:
        unknown = EXCLUDE

    nombre = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "El nombre es obligatorio."},
    )

    email = fields.String(
        required=True,
        validate=validate.Length(max=254),
        error_messages={"required": "El correo electrónico es obligatorio."},
    )

    empresa = fields.String(
        load_default="",
        validate=validate.Length(max=150),
    )

    mensaje = fields.String(
        required=True,
        validate=validate.Length(min=10, max=2000),
        error_messages={
            "required": "El mensaje es obligatorio.",
            "validator_failed": "El mensaje debe tener al menos 10 caracteres.",
        },
    )

    turnstile_token = fields.String(
        required=True,
        validate=validate.Length(min=1, max=2048),
        error_messages={"required": "El token de verificación es obligatorio."},
    )

    # Campo honeypot: los bots lo rellenan, los usuarios no (está oculto en el frontend)
    website = fields.String(
        load_default="",
        validate=validate.Length(max=0),
        error_messages={"validator_failed": "Campo inesperado."},
    )

    @pre_load
    def sanitize_inputs(self, data, **kwargs):
        if "nombre" in data:
            data["nombre"] = sanitize_name(str(data["nombre"]))
        if "email" in data:
            data["email"] = str(data["email"]).strip()
        if "empresa" in data:
            data["empresa"] = sanitize_name(str(data["empresa"]))
        if "mensaje" in data:
            data["mensaje"] = sanitize_text(str(data["mensaje"]))
        if "turnstile_token" in data:
            data["turnstile_token"] = str(data["turnstile_token"]).strip()
        return data

    @validates("email")
    def validate_email(self, value: str, **_kwargs) -> None:
        normalized = sanitize_email(value)
        if normalized is None:
            raise ValidationError("El correo electrónico no es válido.")
