# coding=utf-8

from marshmallow import Schema, fields, validate, validates, ValidationError
from sii import __SII_VERSION__


class Titular(Schema):
    NombreRazon = fields.String(
        required=True,
        validate=validate.Length(max=40, error='Nombre demasiado largo')
    )
    NIF = fields.String(
        required=True,
        validate=validate.Length(max=9, error='NIF demasiado largo')  # TODO validate if it belongs to a NIF ??
    )


class Cabecera(Schema):
    IDVersionSii = fields.String(required=True, default=__SII_VERSION__)
    Titular = fields.Nested(Titular, required=True)
    TipoComunicacion = fields.String(required=True)


class PeriodoImpositivo(Schema):
    Ejercicio = fields.String(required=True)  # TODO validate Año en formato 'YYYY'
    Periodo = fields.String(required=True)  # TODO validate Enumeration '01' para enero, '02' para febrero, ..., '0A' Periodicidad anual


class EmisorFactura(Schema):
    NIF = fields.String(required=True)


class DetalleFactura(Schema):
    IDEmisorFactura = fields.Nested(EmisorFactura, required=True)
    NumSerieFacturaEmisor = fields.String(required=True)
    FechaExpedicionFacturaEmisor = fields.String(required=True)


class Factura(Schema):
    # Campos comunes de una factura
    PeriodoImpositivo = fields.Nested(PeriodoImpositivo)
    IDFactura = fields.Nested(DetalleFactura)


class TipoDesglose(Schema):
    DesgloseFactura = fields.String()  # TODO to change
    DesgloseTipoOperacion = fields.String()  # TODO to change


class Contraparte(Schema):
    NombreRazon = fields.String(
        required=True,
        validate=validate.Length(max=40, error='Nombre demasiado largo')
    )
    NIF = fields.String(
        required=True,
        validate=validate.Length(max=9, error='NIF demasiado largo')  # TODO validate if it belongs to a NIF ??
    )


class DetalleFacturaEmitida(Schema):
    TipoFactura = fields.String(required=True)
    ClaveRegimenEspecialOTrascendencia = fields.String(required=True)
    DescripcionOperacion = fields.String(required=True)
    TipoDesglose = fields.Nested(TipoDesglose, required=True)
    ImporteTotal = fields.Float()
    Contraparte = fields.Nested(Contraparte)  # TODO obligatorio si TipoFactura no es F2 ni F4


class DetalleFacturaRecibida(Schema):
    pass  # TODO add missing fields


class FacturaEmitida(Factura):
    # Campos específicos para facturas emitidas
    FacturaExpedida = fields.Nested(DetalleFacturaEmitida)


class FacturaRecibida(Factura):
    # Campos específicos para facturas recibidas
    FacturaRecibida = fields.String(DetalleFacturaRecibida)


class RegistroFacturasEmitidas(Schema):
    Cabecera = fields.Nested(Cabecera)
    RegistroLRFacturasEmitidas = fields.Nested(FacturaEmitida)
    # TODO lista_facturas = fields.List(fields.Nested(Factura, dump_to='Factura'), validate=validate.Length(max=10000, error='No puede haber más de 10000 facturas'))


class SuministroFacturasEmitidas(Schema):
    SuministroLRFacturasEmitidas = fields.Nested(RegistroFacturasEmitidas)


class SuministroFacturasRecibidas(Schema):
    pass  # TODO add missing fields
