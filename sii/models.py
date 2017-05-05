# coding=utf-8

from marshmallow import Schema, fields, validate, validates, ValidationError
from sii import __SII_VERSION__

PERIODO_VALUES = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '0A'
]

TIPO_NO_EXENTA_VALUES = ['S1', 'S2']

TIPO_RECTIFICATIVA_VALUES = ['S', 'I']


class NIF(Schema):
    NIF = fields.String(
        required=True, validate=validate.Length(max=9)
    )  # TODO validate if it belongs to a NIF ??


class Titular(NIF):
    NombreRazon = fields.String(required=True, validate=validate.Length(max=40))


class Cabecera(Schema):
    IDVersionSii = fields.String(required=True, default=__SII_VERSION__)
    Titular = fields.Nested(Titular, required=True)
    TipoComunicacion = fields.String(
        required=True, validate=validate.Length(max=2)
    )


class PeriodoImpositivo(Schema):
    Ejercicio = fields.String(required=True, validate=validate.Length(max=4))  # TODO validate Año en formato 'YYYY'
    Periodo = fields.String(
        required=True, validate=validate.OneOf(PERIODO_VALUES)
    )


class EmisorFactura(NIF):
    pass


class IdentificacionFactura(Schema):
    IDEmisorFactura = fields.Nested(EmisorFactura, required=True)
    NumSerieFacturaEmisor = fields.String(
        required=True, validate=validate.Length(max=60)
    )
    FechaExpedicionFacturaEmisor = fields.String(required=True)  # TODO fecha en formato DD-MM-AAAA


class Factura(Schema):
    # Campos comunes de una factura
    PeriodoImpositivo = fields.Nested(PeriodoImpositivo, required=True)
    IDFactura = fields.Nested(IdentificacionFactura, required=True)


class Exenta(Schema):
    BaseImponible = fields.Float(required=True)


class DetalleIVAEmitida(Schema):
    TipoImpositivo = fields.Float(required=True)
    BaseImponible = fields.Float(required=True)
    CuotaRepercutida = fields.Float(required=True)


class DesgloseIVA(Schema):
    DetalleIVA = fields.Nested(DetalleIVAEmitida, required=True)


class NoExenta(Schema):
    TipoNoExenta = fields.String(
        required=True, validate=[
            validate.OneOf(TIPO_NO_EXENTA_VALUES), validate.Length(max=2)
        ]
    )
    DesgloseIVA = fields.Nested(DesgloseIVA, required=True)


class ExentaAIVA(Schema):  # TODO obligatorio uno de los dos
    Exenta = fields.Nested(Exenta)
    NoExenta = fields.Nested(NoExenta)


class DesgloseFacturaEmitida(Schema):  # TODO obligatorio uno de los dos
    Sujeta = fields.Nested(ExentaAIVA)
    NoSujeta = fields.String()  # TODO


class DesgloseTipoOperacion(Schema):  # TODO obligatorio uno de los dos
    PrestacionServicios = fields.Nested(DesgloseFacturaEmitida)
    Entrega = fields.Nested(DesgloseFacturaEmitida)


class TipoDesglose(Schema):  # TODO obligatorio uno de los dos
    DesgloseFactura = fields.Nested(DesgloseFacturaEmitida)
    DesgloseTipoOperacion = fields.Nested(DesgloseTipoOperacion)


class Contraparte(Titular):
    pass


class ImporteRectificacion(Schema):
    BaseRectificada = fields.Float(required=True)
    CuotaRectificada = fields.Float(required=True)


class DetalleFactura(Schema):
    TipoFactura = fields.String(required=True, validate=validate.Length(max=2))
    ClaveRegimenEspecialOTrascendencia = fields.String(
        required=True, validate=validate.Length(max=2)
    )
    DescripcionOperacion = fields.String(
        required=True, validate=validate.Length(max=500)
    )
    ImporteTotal = fields.Float()


class DetalleFacturaEmitida(DetalleFactura):
    TipoDesglose = fields.Nested(TipoDesglose, required=True)
    Contraparte = fields.Nested(Contraparte)  # TODO obligatorio si TipoFactura no es F2 ni F4
    TipoRectificativa = fields.String(
        validate=validate.OneOf(TIPO_RECTIFICATIVA_VALUES)
    )  # TODO obligatorio si es una rectificativa
    ImporteRectificacion = fields.Nested(ImporteRectificacion)  # TODO obligatorio si es una rectificativa


class FacturaEmitida(Factura):
    # Campos específicos para facturas emitidas
    FacturaExpedida = fields.Nested(DetalleFacturaEmitida, required=True)


class RegistroFacturas(Schema):
    Cabecera = fields.Nested(Cabecera, required=True)


class RegistroFacturasEmitidas(RegistroFacturas):
    RegistroLRFacturasEmitidas = fields.Nested(FacturaEmitida, required=True)
    # TODO lista_facturas = fields.List(fields.Nested(Factura, dump_to='Factura'), validate=validate.Length(max=10000, error='No puede haber más de 10000 facturas'))


class SuministroFacturasEmitidas(Schema):
    SuministroLRFacturasEmitidas = fields.Nested(
        RegistroFacturasEmitidas, required=True
    )


class DetalleIVADesglose(Schema):
    BaseImponible = fields.Float(required=True)


class DesgloseIVARecibida(Schema):
    DetalleIVA = fields.Nested(DetalleIVADesglose, required=True)


class DetalleIVAInversionSujetoPasivo(DesgloseIVA):
    pass


class DesgloseFacturaRecibida(Schema):  # TODO obligatorio uno de los dos
    InversionSujetoPasivo = fields.Nested(DetalleIVAInversionSujetoPasivo)
    DesgloseIVA = fields.Nested(DesgloseIVARecibida)


class DetalleFacturaRecibida(DetalleFactura):
    DesgloseFactura = fields.Nested(DesgloseFacturaRecibida, required=True)
    Contraparte = fields.Nested(Contraparte, required=True)
    FechaRegContable = fields.String(required=True)  # TODO change to Date, max length 10 chars,
    CuotaDeducible = fields.Float(required=True)


class FacturaRecibida(Factura):
    # Campos específicos para facturas recibidas
    FacturaRecibida = fields.Nested(DetalleFacturaRecibida, required=True)


class RegistroFacturasRecibidas(RegistroFacturas):
    RegistroLRFacturasRecibidas = fields.Nested(FacturaRecibida, required=True)


class SuministroFacturasRecibidas(Schema):
    SuministroLRFacturasRecibidas = fields.Nested(
        RegistroFacturasRecibidas, required=True
    )
