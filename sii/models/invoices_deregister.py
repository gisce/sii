# coding=utf-8
from __future__ import absolute_import

from marshmallow import fields, ValidationError
from sii import __SII_VERSION__
from .invoices_record import (
    MySchema, DateString, CustomStringField, Titular, Partner, NIF,
    PERIODO_VALUES
)


class Cabecera(MySchema):
    IDVersionSii = CustomStringField(required=True, default=__SII_VERSION__)
    Titular = fields.Nested(Titular, required=True)

    @staticmethod
    def validate_id_version_sii(value):
        if value != __SII_VERSION__:
            raise ValidationError(
                'La version del SII es incorrecta. '
                'Se esperaba "{}"'.format(__SII_VERSION__)
            )


class RegistroFacturas(MySchema):
    Cabecera = fields.Nested(Cabecera, required=True)


class IdentificacionFactura(MySchema):
    NumSerieFacturaEmisor = CustomStringField(required=True)
    FechaExpedicionFacturaEmisor = DateString(required=True)

    def validate_num_serie_factura_emisor(self, value):
        self.validate_field_max_length(
            value=value, field_name='Numero de Factura del Emisor',
            max_chars=60
        )

    def validate_fecha_expedicion_factura_emisor(self, value):
        self.validate_field_max_length(
            value=value, field_name='Fecha de Expedicion de la Factura',
            max_chars=10
        )


class IdentificacionFacturaEmitida(IdentificacionFactura):
    IDEmisorFactura = fields.Nested(NIF, required=True)


class EmisorBajaFacturaRecibida(Titular, Partner):

    @staticmethod
    def get_atleast_one_of():
        return ['NIF', 'IDOtro']


class IdentificacionFacturaRecibida(IdentificacionFactura):
    IDEmisorFactura = fields.Nested(EmisorBajaFacturaRecibida, required=True)


class PeriodoImpositivo(MySchema):
    Ejercicio = CustomStringField(required=True)
    Periodo = CustomStringField(required=True)

    def validate_ejercicio(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Ejercicio',
            choices=[str(x) for x in range(0, 10000)]
        )

    def validate_periodo(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Periodo',
            choices=PERIODO_VALUES
        )


class Factura(MySchema):
    PeriodoImpositivo = fields.Nested(PeriodoImpositivo, required=True)


class FacturaEmitida(Factura):
    IDFactura = fields.Nested(IdentificacionFacturaEmitida, required=True)


class FacturaRecibida(Factura):
    IDFactura = fields.Nested(IdentificacionFacturaRecibida, required=True)


class RegistroBajaExpedidas(RegistroFacturas):
    RegistroLRBajaExpedidas = fields.Nested(FacturaEmitida, required=True)


class BajaFacturasEmitidas(MySchema):
    BajaLRFacturasEmitidas = fields.Nested(RegistroBajaExpedidas, required=True)


class RegistroBajaRecibidas(RegistroFacturas):
    RegistroLRBajaRecibidas = fields.Nested(FacturaRecibida, required=True)


class BajaFacturasRecibidas(MySchema):
    BajaLRFacturasRecibidas = fields.Nested(
        RegistroBajaRecibidas, required=True
    )
