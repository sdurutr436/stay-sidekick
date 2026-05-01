"""Schemas Marshmallow para validación de payloads del mapa de calor."""

from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class UmbralesSchema(Schema):
    nivel1 = fields.Integer(required=True, strict=True, validate=validate.Range(min=1))
    nivel2 = fields.Integer(required=True, strict=True, validate=validate.Range(min=1))
    nivel3 = fields.Integer(required=True, strict=True, validate=validate.Range(min=1))

    @validates_schema
    def validate_orden(self, data, **kwargs):
        n1, n2, n3 = data.get("nivel1"), data.get("nivel2"), data.get("nivel3")
        if n1 is not None and n2 is not None and n3 is not None:
            if not (n1 < n2 < n3):
                raise ValidationError(
                    "Los umbrales deben cumplir nivel1 < nivel2 < nivel3."
                )


class ConfigXlsxSchema(Schema):
    col_fecha_checkin = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
    )
    col_fecha_checkout = fields.String(
        required=False,
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=100),
    )
