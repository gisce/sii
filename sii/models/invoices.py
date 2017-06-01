# coding=utf-8

from marshmallow import Schema, fields, post_dump
from marshmallow import validate, validates, validates_schema, ValidationError
from sii import __SII_VERSION__
from datetime import datetime

PERIODO_VALUES = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '0A'
]


class DateString(fields.String):
    def _validate(self, value):
        if value is None:
            return None
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except (ValueError, AttributeError):
            raise ValidationError('Invalid date string', value)

    @post_dump
    def _serialize(self, value, attr, obj):
        return datetime.strptime(value, '%Y-%m-%d').strftime('%d-%m-%Y')


class MySchema(Schema):
    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        unknown = list(set(original_data) - set(self.fields))
        if unknown:
            raise ValidationError('Unknown field', unknown)


class NIF(MySchema):
    NIF = fields.String(required=True, validate=validate.Length(max=9))


class Titular(NIF):
    NombreRazon = fields.String(
        required=True, validate=validate.Length(max=120)
    )


class Contraparte(Titular):
    pass


class Cabecera(MySchema):
    IDVersionSii = fields.String(required=True, default=__SII_VERSION__)
    Titular = fields.Nested(Titular, required=True)


class PeriodoImpositivo(MySchema):
    Ejercicio = fields.String(
        required=True,
        validate=validate.OneOf([str(x) for x in range(0, 10000)])
    )
    Periodo = fields.String(
        required=True, validate=validate.OneOf(PERIODO_VALUES)
    )
