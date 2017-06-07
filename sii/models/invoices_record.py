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

CODIGO_PAIS_VALUES = [
    'AF', 'AL', 'DE', 'AD', 'AO', 'AI', 'AQ', 'AG', 'SA', 'DZ', 'AR', 'AM',
    'AW', 'AU', 'AT', 'AZ', 'BS', 'BH', 'BD', 'BB', 'BE', 'BZ', 'BJ', 'BM',
    'BY', 'BO', 'BA', 'BW', 'BV', 'BR', 'BN', 'BG', 'BF', 'BI', 'BT', 'CV',
    'KY', 'KH', 'CM', 'CA', 'CF', 'CC', 'CO', 'KM', 'CG', 'CD', 'CK', 'KP',
    'KR', 'CI', 'CR', 'HR', 'CU', 'TD', 'CZ', 'CL', 'CN', 'CY', 'CW', 'DK',
    'DM', 'DO', 'EC', 'EG', 'AE', 'ER', 'SK', 'SI', 'ES', 'US', 'EE', 'ET',
    'FO', 'PH', 'FI', 'FJ', 'FR', 'GA', 'GM', 'GE', 'GS', 'GH', 'GI', 'GD',
    'GR', 'GL', 'GU', 'GT', 'GG', 'GN', 'GQ', 'GW', 'GY', 'HT', 'HM', 'HN',
    'HK', 'HU', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM', 'IS', 'IL', 'IT', 'JM',
    'JP', 'JE', 'JO', 'KZ', 'KE', 'KG', 'KI', 'KW', 'LA', 'LS', 'LV', 'LB',
    'LR', 'LY', 'LI', 'LT', 'LU', 'XG', 'MO', 'MK', 'MG', 'MY', 'MW', 'MV',
    'ML', 'MT', 'FK', 'MP', 'MA', 'MH', 'MU', 'MR', 'YT', 'UM', 'MX', 'FM',
    'MD', 'MC', 'MN', 'ME', 'MS', 'MZ', 'MM', 'NA', 'NR', 'CX', 'NP', 'NI',
    'NE', 'NG', 'NU', 'NF', 'NO', 'NC', 'NZ', 'IO', 'OM', 'NL', 'BQ', 'PK',
    'PW', 'PA', 'PG', 'PY', 'PE', 'PN', 'PF', 'PL', 'PT', 'PR', 'QA', 'GB',
    'RW', 'RO', 'RU', 'SB', 'SV', 'WS', 'AS', 'KN', 'SM', 'SX', 'PM', 'VC',
    'SH', 'LC', 'ST', 'SN', 'RS', 'SC', 'SL', 'SG', 'SY', 'SO', 'LK', 'SZ',
    'ZA', 'SD', 'SS', 'SE', 'CH', 'SR', 'TH', 'TW', 'TZ', 'TJ', 'PS', 'TF',
    'TL', 'TG', 'TK', 'TO', 'TT', 'TN', 'TC', 'TM', 'TR', 'TV', 'UA', 'UG',
    'UY', 'UZ', 'VU', 'VA', 'VE', 'VN', 'VG', 'VI', 'WF', 'YE', 'DJ', 'ZM',
    'ZW'
]

ID_TYPE_VALUES = {
    '02': u'NIF-IVA',
    '03': u'PASAPORTE',
    '04': u'DOCUMENTO OFICIAL DE IDENTIFICACIÓN EXPEDIDO POR EL PAIS O '
          u'TERRITORIO DE RESIDENCIA',
    '05': u'CERTIFICADO DE RESIDENCIA',
    '06': u'OTRO DOCUMENTO PROBATORIO',
    '07': u'NO CENSADO'
}

# Valores para la Clave de Régimen Especial para facturas emitidas
CRE_FACTURAS_EMITIDAS = [
    ('01', u'Operación de régimen general'),
    ('02', u'Exportación'),
    ('03', u'Operaciones a las que se aplique el régimen especial de bienes '
           u'usados, objetos de arte, antigüedades y objetos de colección'),
    ('04', u'Régimen especial del oro de inversión'),
    ('05', u'Régimen especial de las agencias de viajes'),
    ('06', u'Régimen especial grupo de entidades en IVA (Nivel Avanzado)'),
    ('07', u'Régimen especial del criterio de caja'),
    ('08', u'Operaciones sujetas al IPSI / IGIC (Impuesto sobre la Producción, '
           u'los Servicios y la Importación / Impuesto General Indirecto '
           u'Canario)'),
    ('09', u'Facturación de las prestaciones de servicios de agencias de viaje '
           u'que actúan como mediadoras en nombre y por cuenta ajena (D.A.4ª '
           u'RD1619/2012)'),
    ('10', u'Cobros por cuenta de terceros de honorarios profesionales o de '
           u'derechos derivados de la propiedad industrial, de autor u otros '
           u'por cuenta de sus socios, asociados o colegiados efectuados por '
           u'sociedades, asociaciones, colegios profesionales u otras '
           u'entidades que realicen estas funciones de cobro'),
    ('11', u'Operaciones de arrendamiento de local de negocio sujetas a '
           u'retención'),
    ('12', u'Operaciones de arrendamiento de local de negocio no sujetos a '
           u'retención'),
    ('13', u'Operaciones de arrendamiento de local de negocio sujetas y no '
           u'sujetas a retención'),
    ('14', u'Factura con IVA pendiente de devengo en certificaciones de obra '
           u'cuyo destinatario sea una Administración Pública'),
    ('15', u'Factura con IVA pendiente de devengo en operaciones de tracto '
           u'sucesivo'),
    ('16', u'Primer semestre 2017')
]

CRE_FACTURAS_RECIBIDAS = [
    ('01', u'Operación de régimen general'),
    ('02', u'Operaciones por las que los empresarios satisfacen compensaciones '
           u'en las adquisiciones a personas acogidas al Régimen especial de '
           u'la agricultura, ganadería y pesca'),
    ('03', u'Operaciones a las que se aplique el régimen especial de bienes '
           u'usados, objetos de arte, antigüedades y objetos de colección'),
    ('04', u'Régimen especial del oro de inversión'),
    ('05', u'Régimen especial de las agencias de viajes'),
    ('06', u'Régimen especial grupo de entidades en IVA (Nivel Avanzado)'),
    ('07', u'Régimen especial del criterio de caja'),
    ('08', u'Operaciones sujetas al IPSI / IGIC (Impuesto sobre la Producción, '
           u'los Servicios y la Importación / Impuesto General Indirecto '
           u'Canario)'),
    ('09', u'Adquisiciones intracomunitarias de bienes y prestaciones de '
           u'servicios'),
    ('12', u'Operaciones de arrendamiento de local de negocio'),
    ('13', u'Factura correspondiente a una importación (informada sin asociar '
           u'a un DUA)'),
    ('14', u'Primer semestre 2017')
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


class IDOtro(MySchema):
    CodigoPais = fields.String(
        required=True, validate=validate.OneOf(CODIGO_PAIS_VALUES)
    )
    IDType = fields.String(
        required=True, validate=validate.OneOf(ID_TYPE_VALUES.keys())
    )
    ID = fields.String(required=True, validate=validate.Length(max=20))


class NIF(MySchema):
    NIF = fields.String(required=False, validate=validate.Length(max=9))


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
    IDOtro = fields.Nested(IDOtro)
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
        validate=validate.OneOf(
            choices=sorted(dict(CRE_FACTURAS_EMITIDAS).keys()),
            labels=[v for k, v in sorted(dict(CRE_FACTURAS_EMITIDAS).items())],
            error='El valor "{input}" de la Clave de Regimen Especial para '
                  'facturas emitidas de la posicion fiscal de la factura no es '
                  'valido'
        )
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
        validate=validate.OneOf(
            choices=sorted(dict(CRE_FACTURAS_RECIBIDAS).keys()),
            labels=[v for k, v in sorted(dict(CRE_FACTURAS_RECIBIDAS).items())],
            error='El valor "{input}" de la Clave de Regimen Especial para '
                  'facturas recibidas de la posicion fiscal de la factura no '
                  'es valido'
        )
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
