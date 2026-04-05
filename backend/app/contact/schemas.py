"""Esquema Marshmallow para el formulario de contacto / solicitud de herramienta."""

from marshmallow import (
    EXCLUDE,
    Schema,
    fields,
    validate,
    validates,
    validates_schema,
    ValidationError,
    pre_load,
)

from app.common.sanitizers.text import sanitize_name, sanitize_text
from app.common.sanitizers.phone import sanitize_phone
from app.common.sanitizers.email import sanitize_email


# Códigos ISO 3166-1 alpha-2 más habituales; ampliar según necesidades.
_VALID_COUNTRY_CODES = {
    "ES", "MX", "AR", "CO", "CL", "PE", "EC", "VE", "UY", "BO",
    "PY", "PA", "CR", "GT", "HN", "SV", "NI", "DO", "CU", "PR",
    "US", "GB", "FR", "DE", "IT", "PT", "BR", "CN", "JP", "IN",
    "AU", "CA", "NL", "BE", "CH", "AT", "SE", "NO", "DK", "FI",
    "PL", "CZ", "RO", "IE", "GR", "HU", "BG", "HR", "SK", "SI",
}


class ContactFormSchema(Schema):
    """Valida y sanitiza los datos del formulario de contacto.

    Campos esperados del frontend:
    - company_name: nombre de la empresa
    - company_email: correo corporativo
    - country_code: ISO alpha-2 del país (selector de prefijo)
    - phone: número de teléfono (sin o con prefijo)
    - is_member: si ya es miembro (boolean)
    - message: texto libre del usuario
    - turnstile_token: token del captcha Turnstile
    - privacy_accepted: aceptación de política de privacidad
    - website: campo honeypot (debe llegar vacío o ausente)
    """

    company_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=150),
        error_messages={"required": "El nombre de la empresa es obligatorio."},
    )

    company_email = fields.String(
        required=True,
        error_messages={"required": "El correo de la empresa es obligatorio."},
    )

    country_code = fields.String(
        required=True,
        validate=validate.Length(equal=2),
        error_messages={"required": "El código de país es obligatorio."},
    )

    phone = fields.String(
        required=True,
        validate=validate.Length(min=4, max=20),
        error_messages={"required": "El teléfono es obligatorio."},
    )

    is_member = fields.Boolean(
        required=True,
        error_messages={"required": "Indica si ya eres miembro."},
    )

    message = fields.String(
        load_default="",
        validate=validate.Length(max=2000),
    )

    turnstile_token = fields.String(
        required=True,
        validate=validate.Length(min=1, max=2048),
        error_messages={"required": "El token de verificación es obligatorio."},
    )

    privacy_accepted = fields.Boolean(
        required=True,
        error_messages={"required": "Debes aceptar la política de privacidad."},
    )

    # Campo honeypot: los bots lo rellenan, los usuarios no (está oculto en el frontend)
    website = fields.String(
        load_default="",
        validate=validate.Length(max=0),
        error_messages={"validator_failed": "Campo inesperado."},
    )

    class Meta:
        # Ignorar campos extra que no estén en el esquema
        unknown = EXCLUDE

    # ── Pre-load: sanitización antes de la validación ───────────────────────

    @pre_load
    def sanitize_fields(self, data: dict, **_kwargs) -> dict:
        """Sanitiza los campos de texto antes de que Marshmallow valide."""
        if "company_name" in data:
            data["company_name"] = sanitize_name(str(data["company_name"]))

        if "company_email" in data:
            data["company_email"] = str(data["company_email"]).strip()

        if "country_code" in data:
            data["country_code"] = str(data["country_code"]).strip().upper()

        if "phone" in data:
            data["phone"] = str(data["phone"]).strip()

        if "message" in data:
            data["message"] = sanitize_text(str(data["message"]))

        if "turnstile_token" in data:
            data["turnstile_token"] = str(data["turnstile_token"]).strip()

        return data

    # ── Validaciones individuales ───────────────────────────────────────────

    @validates("company_email")
    def validate_email(self, value: str, **_kwargs) -> None:
        normalized = sanitize_email(value)
        if normalized is None:
            raise ValidationError("El correo electrónico no es válido.")

    @validates("country_code")
    def validate_country_code(self, value: str, **_kwargs) -> None:
        if value not in _VALID_COUNTRY_CODES:
            raise ValidationError("El código de país no es válido.")

    @validates("privacy_accepted")
    def validate_privacy(self, value: bool, **_kwargs) -> None:
        if value is not True:
            raise ValidationError("Debes aceptar la política de privacidad.")

    # ── Validación cruzada ──────────────────────────────────────────────────

    @validates_schema
    def validate_phone_with_country(self, data: dict, **_kwargs) -> None:
        """Valida el teléfono usando el country_code como contexto."""
        phone = data.get("phone")
        country = data.get("country_code", "ES")
        if phone:
            normalized = sanitize_phone(phone, country)
            if normalized is None:
                raise ValidationError(
                    "El número de teléfono no es válido para el país seleccionado.",
                    field_name="phone",
                )
            # Reemplaza por el formato normalizado E.164
            data["phone"] = normalized

    @validates_schema
    def normalize_email_output(self, data: dict, **_kwargs) -> None:
        """Sustituye el email por su versión normalizada."""
        email = data.get("company_email")
        if email:
            data["company_email"] = sanitize_email(email)
