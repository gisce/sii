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
    PeriodoImpositivo = fields.Nested(PeriodoImpositivo, required=True)
    IDFactura = fields.Nested(DetalleFactura, required=True)


class Exenta(Schema):
    BaseImponible = fields.Float(required=True)


class DetalleIVAEmitida(Schema):
    TipoImpositivo = fields.String(required=True)
    BaseImponible = fields.Float(required=True)
    CuotaRepercutida = fields.Float(required=True)


class DesgloseIVA(Schema):
    DetalleIVA = fields.Nested(DetalleIVAEmitida, required=True)


class NoExenta(Schema):
    TipoNoExenta = fields.String(required=True)
    DesgloseIVA = fields.Nested(DesgloseIVA, required=True)

    @validates('TipoNoExenta')
    def validate_tipo_no_exenta(self, value):
        if value not in ['S1', 'S2']:
            raise ValidationError(
                'El TipoNoExenta es incorrecto: {}'.format(value)
            )


class ExentaAIVA(Schema):  # TODO obligatorio uno de los dos
    Exenta = fields.Nested(Exenta)
    NoExenta = fields.Nested(NoExenta)


class DesgloseFacturaEmitida(Schema):  # TODO obligatorio uno de los dos
    Sujeta = fields.Nested(ExentaAIVA)
    NoSujeta = fields.String()  # TODO


class TipoDesglose(Schema):
    DesgloseFactura = fields.Nested(DesgloseFacturaEmitida)
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


class ImporteRectificacion(Schema):
    BaseRectificada = fields.Float(required=True)
    CuotaRectificada = fields.Float(required=True)


class DetalleFacturaEmitida(Schema):
    TipoFactura = fields.String(required=True)
    ClaveRegimenEspecialOTrascendencia = fields.String(required=True)
    DescripcionOperacion = fields.String(required=True)
    TipoDesglose = fields.Nested(TipoDesglose, required=True)
    ImporteTotal = fields.Float()
    Contraparte = fields.Nested(Contraparte)  # TODO obligatorio si TipoFactura no es F2 ni F4
    TipoRectificativa = fields.String()  # TODO obligatorio si es una rectificativa
    ImporteRectificacion = fields.Nested(ImporteRectificacion) # TODO obligatorio si es una rectificativa


class FacturaEmitida(Factura):
    # Campos específicos para facturas emitidas
    FacturaExpedida = fields.Nested(DetalleFacturaEmitida, required=True)


class RegistroFacturasEmitidas(Schema):
    Cabecera = fields.Nested(Cabecera, required=True)
    RegistroLRFacturasEmitidas = fields.Nested(FacturaEmitida, required=True)
    # TODO lista_facturas = fields.List(fields.Nested(Factura, dump_to='Factura'), validate=validate.Length(max=10000, error='No puede haber más de 10000 facturas'))


class SuministroFacturasEmitidas(Schema):
    SuministroLRFacturasEmitidas = fields.Nested(
        RegistroFacturasEmitidas, required=True
    )


class DetalleIVARecibida(DetalleIVAEmitida):
    pass


class DetalleIVARecibida2(Schema):
    BaseImponible = fields.Float(required=True)


class DesgloseFactura(Schema):
    InversionSujetoPasivo = fields.Nested(DetalleIVARecibida)
    DesgloseIVA = fields.Nested(DetalleIVARecibida2)


class DetalleFacturaRecibida(Schema):
    TipoFactura = fields.String(required=True)
    ClaveRegimenEspecialOTrascendencia = fields.String(required=True)
    DescripcionOperacion = fields.String(required=True)
    DesgloseFactura = fields.Nested(DesgloseFactura, required=True)
    Contraparte = fields.Nested(Contraparte, required=True)
    FechaRegContable = fields.String(required=True)  # TODO change to Date, max length 10 chars,
    CuotaDeducible = fields.Float(required=True)


class FacturaRecibida(Factura):
    # Campos específicos para facturas recibidas
    FacturaRecibida = fields.String(DetalleFacturaRecibida, required=True)


class RegistroFacturasRecibidas(Schema):
    Cabecera = fields.Nested(Cabecera, required=True)
    RegistroLRFacturasRecibidas = fields.Nested(FacturaRecibida, required=True)


class SuministroFacturasRecibidas(Schema):
    SuministroLRFacturasRecibidas = fields.Nested(
        RegistroFacturasRecibidas, required=True
    )
