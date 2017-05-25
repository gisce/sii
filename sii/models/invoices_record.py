# coding=utf-8

from marshmallow import Schema, fields, post_dump
from marshmallow import validate, validates, validates_schema, ValidationError
from sii import __SII_VERSION__
from datetime import datetime

TIPO_COMUNICACION_VALUES = ['A0', 'A1', 'A4']

TIPO_FACTURA_VALUES = [
    'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'R1', 'R2', 'R3', 'R4', 'R5'
]

PERIODO_VALUES = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '0A'
]

TIPO_NO_EXENTA_VALUES = ['S1', 'S2', 'S3']

TIPO_RECTIFICATIVA_VALUES = ['S', 'I']

CLAVE_REGIMEN_ESPECIAL_FACTURAS_EMITIDAS = ['01', '02', '03', '04', '05', '06',
                                            '07', '08', '09', '10', '11', '12',
                                            '13', '14', '15', '16']

CLAVE_REGIMEN_ESPECIAL_FACTURAS_RECIBIDAS = ['01', '02', '03', '04', '05', '06',
                                             '07', '08', '09', '12', '13', '14']


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


class Cabecera(MySchema):
    IDVersionSii = fields.String(required=True, default=__SII_VERSION__)
    Titular = fields.Nested(Titular, required=True)
    TipoComunicacion = fields.String(
        required=True, validate=validate.OneOf(TIPO_COMUNICACION_VALUES)
    )


class PeriodoImpositivo(MySchema):
    Ejercicio = fields.String(required=True, validate=validate.OneOf(
        [str(x) for x in range(0, 10000)]
    ))
    Periodo = fields.String(
        required=True, validate=validate.OneOf(PERIODO_VALUES)
    )


class EmisorFactura(NIF):
    pass


class IdentificacionFactura(MySchema):
    IDEmisorFactura = fields.Nested(EmisorFactura, required=True)
    NumSerieFacturaEmisor = fields.String(
        required=True, validate=validate.Length(max=60)
    )
    FechaExpedicionFacturaEmisor = DateString(
        required=True, validate=validate.Length(max=10)
    )


class Factura(MySchema):
    # Campos comunes de una factura
    PeriodoImpositivo = fields.Nested(PeriodoImpositivo, required=True)
    IDFactura = fields.Nested(IdentificacionFactura, required=True)


class DetalleIVA(MySchema):
    BaseImponible = fields.Float(required=True)


class Exenta(DetalleIVA):
    pass


class DetalleIVAEmitida(DetalleIVA):
    TipoImpositivo = fields.Float()
    CuotaRepercutida = fields.Float()


class DesgloseIVA(MySchema):
    DetalleIVA = fields.List(fields.Nested(DetalleIVAEmitida), required=True)


class NoExenta(MySchema):
    TipoNoExenta = fields.String(
        required=True, validate=validate.OneOf(TIPO_NO_EXENTA_VALUES)
    )
    DesgloseIVA = fields.Nested(DesgloseIVA, required=True)


class ExentaAIVA(MySchema):  # TODO obligatorio uno de los dos
    Exenta = fields.Nested(Exenta)
    NoExenta = fields.Nested(NoExenta)


class NoSujeta(MySchema):
    ImportePorArticulos7_14_Otros = fields.Float()
    ImporteTAIReglasLocalizacion = fields.Float()


class DesgloseFacturaEmitida(MySchema):  # TODO obligatorio uno de los dos
    Sujeta = fields.Nested(ExentaAIVA)
    NoSujeta = fields.Nested(NoSujeta)


class DesgloseTipoOperacion(MySchema):  # TODO obligatorio uno de los dos
    PrestacionServicios = fields.Nested(DesgloseFacturaEmitida)
    Entrega = fields.Nested(DesgloseFacturaEmitida)


class TipoDesglose(MySchema):  # TODO obligatorio uno de los dos pero sólo puede haber uno
    DesgloseFactura = fields.Nested(DesgloseFacturaEmitida)
    DesgloseTipoOperacion = fields.Nested(DesgloseTipoOperacion)


class Contraparte(Titular):
    pass


class ImporteRectificacion(MySchema):
    BaseRectificada = fields.Float(required=True)
    CuotaRectificada = fields.Float(required=True)


class DetalleFactura(MySchema):
    TipoFactura = fields.String(
        required=True, validate=validate.OneOf(TIPO_FACTURA_VALUES)
    )
    DescripcionOperacion = fields.String(
        required=True, validate=validate.Length(max=500)
    )
    TipoRectificativa = fields.String(
        validate=validate.OneOf(TIPO_RECTIFICATIVA_VALUES)
    )  # TODO obligatorio si es una rectificativa
    ImporteRectificacion = fields.Nested(ImporteRectificacion)  # TODO obligatorio si TipoRectificativa = 'S'
    # TODO ImporteTotal OBLIGATORIO si:
    # 1.Obligatorio si Baseimponible=0 y TipoFactura=”F2” o “R5”
    # 2.Obligatorio si Baseimponible=0 y ClaveRegimenEspecialOTranscedencia = “05”o “03”
    ImporteTotal = fields.Float()


class DetalleFacturaEmitida(DetalleFactura):
    ClaveRegimenEspecialOTrascendencia = fields.String(
        required=True,
        validate=validate.OneOf(CLAVE_REGIMEN_ESPECIAL_FACTURAS_EMITIDAS)
    )
    TipoDesglose = fields.Nested(TipoDesglose, required=True)
    Contraparte = fields.Nested(Contraparte)  # TODO obligatorio si TipoFactura no es F2 ni F4


class FacturaEmitida(Factura):
    # Campos específicos para facturas emitidas
    FacturaExpedida = fields.Nested(DetalleFacturaEmitida, required=True)


class RegistroFacturas(MySchema):
    Cabecera = fields.Nested(Cabecera, required=True)


class RegistroFacturasEmitidas(RegistroFacturas):
    RegistroLRFacturasEmitidas = fields.Nested(FacturaEmitida, required=True)
    # TODO lista_facturas = fields.List(fields.Nested(Factura, dump_to='Factura'), validate=validate.Length(max=10000, error='No puede haber más de 10000 facturas'))


class SuministroFacturasEmitidas(MySchema):
    SuministroLRFacturasEmitidas = fields.Nested(
        RegistroFacturasEmitidas, required=True
    )


class DetalleIVADesglose(DetalleIVA):
    CuotaSoportada = fields.Float()
    TipoImpositivo = fields.Float()
    # TODO 1.Sólo se podrá rellenar ( y es obligatorio) si
    # ClaveRegimenEspecialOTranscedencia="02" (Operaciones por las que los
    # Empresarios satisfacen compensaciones REAGYP)
    # 2. Solo se permiten los valores 12% y 10,5 %.
    PorcentCompensacionREAGYP = fields.String()
    # TODO 1.Sólo se podrá rellenar (y es obligatorio) si
    # ClaveRegimenEspecialOTranscedencia="02" (Operaciones por las que los
    # Empresarios satisfacen compensaciones REAGYP)
    # 2. Importe compensación = Base * Porcentaje compensación +/-1 % de la
    # Base
    ImporteCompensacionREAGYP = fields.String()


class DesgloseIVARecibida(MySchema):
    DetalleIVA = fields.List(fields.Nested(DetalleIVADesglose), required=True)


class DetalleIVARecibida(DetalleIVA):
    CuotaSoportada = fields.Float(required=True)
    TipoImpositivo = fields.Float(required=True)


class DetalleIVAInversionSujetoPasivo(DesgloseIVA):
    DetalleIVA = fields.List(fields.Nested(DetalleIVARecibida), required=True)


class DesgloseFacturaRecibida(MySchema):  # TODO obligatorio uno de los dos
    InversionSujetoPasivo = fields.Nested(DetalleIVAInversionSujetoPasivo)
    DesgloseIVA = fields.Nested(DesgloseIVARecibida)


class DetalleFacturaRecibida(DetalleFactura):
    ClaveRegimenEspecialOTrascendencia = fields.String(
        required=True,
        validate=validate.OneOf(CLAVE_REGIMEN_ESPECIAL_FACTURAS_RECIBIDAS)
    )
    DesgloseFactura = fields.Nested(DesgloseFacturaRecibida, required=True)
    Contraparte = fields.Nested(Contraparte, required=True)
    FechaRegContable = DateString(
        required=True, validate=validate.Length(max=10)
    )  # TODO FechaRegContable ≥ FechaExpedicionFacturaEmisor
    CuotaDeducible = fields.Float(required=True)


class FacturaRecibida(Factura):
    # Campos específicos para facturas recibidas
    FacturaRecibida = fields.Nested(DetalleFacturaRecibida, required=True)


class RegistroFacturasRecibidas(RegistroFacturas):
    RegistroLRFacturasRecibidas = fields.Nested(FacturaRecibida, required=True)


class SuministroFacturasRecibidas(MySchema):
    SuministroLRFacturasRecibidas = fields.Nested(
        RegistroFacturasRecibidas, required=True
    )
