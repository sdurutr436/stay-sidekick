"""Schemas Marshmallow para validación de payloads del mapa de calor."""

from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class UmbralesSchema(Schema):
    nivel1 = fields.Integer(required=True, strict=True, validate=validate.Range(min=1, max=9999))
    nivel2 = fields.Integer(required=True, strict=True, validate=validate.Range(min=1, max=9999))
    nivel3 = fields.Integer(required=True, strict=True, validate=validate.Range(min=1, max=9999))

    @validates_schema
    def validate_orden(self, data, **kwargs):
        n1, n2, n3 = data.get("nivel1"), data.get("nivel2"), data.get("nivel3")
        if n1 is not None and n2 is not None and n3 is not None:
            if not (n1 < n2 < n3):
                raise ValidationError(
                    "Los umbrales deben cumplir nivel1 < nivel2 < nivel3."
                )


def _validar_letra_columna(valor):
    if valor and not valor.strip().upper().isalpha():
        raise ValidationError("Debe ser una letra de columna Excel (ej. A, B, C, AA...).")


class ConfigXlsxSchema(Schema):
    col_fecha_checkin = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=3), _validar_letra_columna],
    )
    col_fecha_checkout = fields.String(
        required=False,
        allow_none=True,
        load_default=None,
        validate=[validate.Length(max=3), _validar_letra_columna],
    )
