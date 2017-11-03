# coding=utf-8

from marshmallow import Schema, fields, post_dump
from marshmallow import validates_schema, ValidationError
from sii import __SII_VERSION__
from datetime import datetime
import re

TIPO_COMUNICACION_VALUES = ['A0', 'A1', 'A4']

TIPO_FACTURA_VALUES = [
    'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'R1', 'R2', 'R3', 'R4', 'R5'
]

PERIODO_VALUES = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '0A'
]

TIPO_IMPOSITIVO_VALUES = [0.0, 4.0, 10.0, 21.0,  # Tipos impositivos actuales
                          7.0, 8.0, 16.0, 18.0]  # Tipos en fecha <= 2012

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

SITUACION_INMUEBLE_VALUES = ['1', '2', '3', '4']


def convert_camel_case_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_error_message(field_name, value, error_msg):
    msg = '{0}: "{1}" - {2}'.format(field_name, value, error_msg)
    return msg


class CustomStringField(fields.String):

    default_error_messages = {
        'invalid': 'No es un String valido'
    }


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

    @staticmethod
    def get_atleast_one_of():
        return []

    @staticmethod
    def get_atleast_one_of_error_message(choices):
        """

        :param choices:
        :type choices: list of str
        :return:
        """
        choices_str = ', '.join(['"{}"'.format(choice) for choice in choices])

        res = (
            'Al menos uno de los campos siguientes son '
            'obligatorios: {}'.format(choices_str)
        )

        return res

    def validate_field_max_length(self, value, field_name, max_chars):
        """
        Validates maximum length for the field
        :param value: field value
        :type value: str
        :param field_name: name of the field
        :type field_name: str
        :param max_chars: maximum number of chars for the field
        :type max_chars: int
        :return:
        :raise ValidationError: if len(value) is greater than max_chars
        """
        if len(value) > max_chars:
            raise ValidationError(
                self.get_max_length_error_message(
                    field_name=field_name, max_chars=max_chars
                )
            )

    @staticmethod
    def validate_field_is_one_of(value, field_name, choices):
        """
        Validates value is an element of choices
        :param value: field value
        :type value: str
        :param field_name: name of the field
        :type field_name: str
        :param choices: list of choices for the field
        :type choices: list of str
        :return:
        :raise ValidationError: if choices doesn't contain value
        """
        if value not in choices:
            raise ValidationError(
                'El campo "{}" es incorrecto'.format(field_name)
            )

    @staticmethod
    def get_max_length_error_message(field_name, max_chars):
        """
        Returns default max_length message
        :param field_name: String
        :type field_name: str
        :param max_chars: maximum number of chars for the field
        :type max_chars: int
        :return:
        """
        err_msg = 'El campo "{}" no puede contener mas ' \
                  'de {} caracteres'.format(field_name, str(max_chars))
        return err_msg

    @validates_schema
    def validate_all_fields(self, data):
        validation_errors = []
        for key in data.keys():
            underscore_key = convert_camel_case_to_underscore(key)
            validate_method = getattr(
                self, 'validate_{}'.format(underscore_key), None
            )
            try:
                if validate_method:
                    validate_method(data[key])
            except ValidationError as v:
                msg = get_error_message(
                    field_name=key, value=data[key], error_msg=v.message
                )
                validation_errors.append(msg)
        if validation_errors:
            raise ValidationError(validation_errors)

    @validates_schema
    def validate_atleast_one_of(self, data):
        choices_method = getattr(self, 'get_atleast_one_of', None)
        if choices_method:
            choices = choices_method()
            if choices:
                for elem in choices:
                    if elem in data:
                        return
                raise ValidationError(
                    self.get_atleast_one_of_error_message(choices)
                )

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        unknown = list(set(original_data) - set(self.fields))
        if unknown:
            raise ValidationError('Unknown field', unknown)


class IDOtro(MySchema):
    CodigoPais = CustomStringField(required=True)
    IDType = CustomStringField(required=True)
    ID = CustomStringField(required=True)

    def validate_codigo_pais(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Codigo de Pais',
            choices=CODIGO_PAIS_VALUES
        )

    def validate_id_type(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Tipo de Identificacion',
            choices=ID_TYPE_VALUES.keys()
        )

    def validate_id(self, value):
        self.validate_field_max_length(
            value=value, field_name='Identificacion', max_chars=20
        )


class NIF(MySchema):
    NIF = CustomStringField(required=False)

    @staticmethod
    def get_nif_field_name():
        return 'NIF'

    def validate_nif(self, value):
        self.validate_field_max_length(
            value=value, field_name=self.get_nif_field_name(), max_chars=9
        )


class Titular(NIF):
    NombreRazon = CustomStringField(required=True)

    @staticmethod
    def get_nif_field_name():
        return 'NIF del Titular'

    def validate_nombre_razon(self, value):
        self.validate_field_max_length(
            value=value, field_name='Nombre y Apellidos del Titular',
            max_chars=120
        )


class Cabecera(MySchema):
    IDVersionSii = CustomStringField(required=True, default=__SII_VERSION__)
    Titular = fields.Nested(Titular, required=True)
    TipoComunicacion = CustomStringField(required=True)

    @staticmethod
    def validate_id_version_sii(value):
        if value != __SII_VERSION__:
            raise ValidationError(
                'La version del SII es incorrecta. '
                'Se esperaba "{}"'.format(__SII_VERSION__)
            )

    def validate_tipo_comunicacion(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Tipo de Comunicacion',
            choices=TIPO_COMUNICACION_VALUES
        )


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


class EmisorFactura(NIF):

    @staticmethod
    def get_nif_field_name():
        return 'NIF del Emisor de la factura'


class IdentificacionFactura(MySchema):
    IDEmisorFactura = fields.Nested(EmisorFactura, required=True)
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


class Factura(MySchema):
    # Campos comunes de una factura
    PeriodoImpositivo = fields.Nested(PeriodoImpositivo, required=True)
    IDFactura = fields.Nested(IdentificacionFactura, required=True)


class DetalleIVA(MySchema):
    BaseImponible = fields.Float(required=True)
    CausaExencion = CustomStringField()


class Exenta(DetalleIVA):
    pass


class DetalleIVAEmitida(DetalleIVA):
    TipoImpositivo = fields.Float()
    CuotaRepercutida = fields.Float()

    def validate_tipo_impositivo(self, value):
        self.validate_field_is_one_of(
            value=str(value), field_name='Tipo Impositivo',
            choices=[str(x) for x in TIPO_IMPOSITIVO_VALUES]
        )


class DesgloseIVA(MySchema):
    DetalleIVA = fields.List(fields.Nested(DetalleIVAEmitida), required=True)


class NoExenta(MySchema):
    TipoNoExenta = CustomStringField(required=True)
    DesgloseIVA = fields.Nested(DesgloseIVA, required=True)

    def validate_tipo_no_exenta(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Tipo No Exenta',
            choices=TIPO_NO_EXENTA_VALUES
        )


class ExentaAIVA(MySchema):
    Exenta = fields.Nested(Exenta)
    NoExenta = fields.Nested(NoExenta)

    @staticmethod
    def get_atleast_one_of():
        return ['Exenta', 'NoExenta']


class NoSujeta(MySchema):
    ImportePorArticulos7_14_Otros = fields.Float()
    ImporteTAIReglasLocalizacion = fields.Float()


class DesgloseFacturaEmitida(MySchema):
    Sujeta = fields.Nested(ExentaAIVA)
    NoSujeta = fields.Nested(NoSujeta)

    @staticmethod
    def get_atleast_one_of():
        return ['Sujeta', 'NoSujeta']


class DesgloseTipoOperacion(MySchema):
    PrestacionServicios = fields.Nested(DesgloseFacturaEmitida)
    Entrega = fields.Nested(DesgloseFacturaEmitida)

    @staticmethod
    def get_atleast_one_of():
        return ['PrestacionServicios', 'Entrega']


class TipoDesglose(MySchema):  # TODO obligatorio uno de los dos pero sólo puede haber uno
    DesgloseFactura = fields.Nested(DesgloseFacturaEmitida)
    DesgloseTipoOperacion = fields.Nested(DesgloseTipoOperacion)


class Partner(NIF):
    IDOtro = fields.Nested(IDOtro)


class Contraparte(Titular, Partner):

    @staticmethod
    def get_nif_field_name():
        return 'NIF de la Contraparte de la factura'


class ImporteRectificacion(MySchema):
    BaseRectificada = fields.Float(required=True)
    CuotaRectificada = fields.Float(required=True)


class IDFacturaRectificada(MySchema):
    NumSerieFacturaEmisor = CustomStringField(required=True)
    FechaExpedicionFacturaEmisor = DateString(required=True)

    def validate_num_serie_factura_emisor(self, value):
        self.validate_field_max_length(
            value=value, field_name='Numero de la Factura Rectificada',
            max_chars=60
        )

    def validate_fecha_expedicion_factura_emisor(self, value):
        self.validate_field_max_length(
            value=value,
            field_name='Fecha de Expedicion de la Factura Rectificada',
            max_chars=10
        )


class FacturasRectificadas(MySchema):
    IDFacturaRectificada = fields.List(
        fields.Nested(IDFacturaRectificada), required=True
    )


class DetalleFactura(MySchema):
    TipoFactura = CustomStringField(required=True)
    DescripcionOperacion = CustomStringField(required=True)
    TipoRectificativa = CustomStringField()  # TODO obligatorio si es una rectificativa
    ImporteRectificacion = fields.Nested(ImporteRectificacion)  # TODO obligatorio si TipoRectificativa = 'S'
    FacturasRectificadas = fields.Nested(FacturasRectificadas)  # TODO opcional si TipoFactura = Rectificativa
    # TODO ImporteTotal OBLIGATORIO si:
    # 1.Obligatorio si Baseimponible=0 y TipoFactura=”F2” o “R5”
    # 2.Obligatorio si Baseimponible=0 y ClaveRegimenEspecialOTranscedencia = “05”o “03”
    ImporteTotal = fields.Float()

    def validate_tipo_factura(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Tipo de Factura',
            choices=TIPO_FACTURA_VALUES
        )

    def validate_descripcion_operacion(self, value):
        self.validate_field_max_length(
            value=value, field_name='Descripcion de la Operacion',
            max_chars=500
        )

    def validate_tipo_rectificativa(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Tipo de Rectificativa',
            choices=TIPO_RECTIFICATIVA_VALUES
        )


class DetalleInmueble(MySchema):
    SituacionInmueble = CustomStringField(required=True)
    ReferenciaCatastral = CustomStringField()  # TODO obligatorio si SituaciónInmueble <> 3 o 4

    def validate_situacion_inmueble(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Situacion Inmueble',
            choices=SITUACION_INMUEBLE_VALUES
        )


class DatosInmueble(MySchema):
    DetalleInmueble = fields.Nested(DetalleInmueble)
    # TODO comprobar si es obligatorio y añadir máximo 15
    # <element name="DetalleInmueble" type="sii:DatosInmuebleType" maxOccurs="15"/>


class DetalleFacturaEmitida(DetalleFactura):
    ClaveRegimenEspecialOTrascendencia = CustomStringField(
        required=True,
        error_messages={
            'invalid': 'La Clave de Regimen Especial para '
                       'Facturas Emitidas no es valida'
        }
    )
    TipoDesglose = fields.Nested(TipoDesglose, required=True)
    Contraparte = fields.Nested(Contraparte)  # TODO obligatorio si TipoFactura no es F2 ni F4
    DatosInmueble = fields.Nested(DatosInmueble)  # TODO obligatorio si ClaveRegimenEspecialOTranscedencia= “12” o “13”

    def validate_clave_regimen_especial_o_trascendencia(self, value):
        self.validate_field_is_one_of(
            value=value, choices=sorted(dict(CRE_FACTURAS_EMITIDAS).keys()),
            field_name='Clave de Regimen Especial para Facturas Emitidas'
        )


class EmisorFacturaRecibida(EmisorFactura, Partner):

    @staticmethod
    def get_atleast_one_of():
        return ['NIF', 'IDOtro']


class IdentificacionFacturaRecibida(IdentificacionFactura):
    IDEmisorFactura = fields.Nested(EmisorFacturaRecibida, required=True)


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
    PorcentCompensacionREAGYP = CustomStringField()
    # TODO 1.Sólo se podrá rellenar (y es obligatorio) si
    # ClaveRegimenEspecialOTranscedencia="02" (Operaciones por las que los
    # Empresarios satisfacen compensaciones REAGYP)
    # 2. Importe compensación = Base * Porcentaje compensación +/-1 % de la
    # Base
    ImporteCompensacionREAGYP = CustomStringField()


class DesgloseIVARecibida(MySchema):
    DetalleIVA = fields.List(fields.Nested(DetalleIVADesglose), required=True)


class DetalleIVARecibida(DetalleIVA):
    CuotaSoportada = fields.Float(required=True)
    TipoImpositivo = fields.Float(required=True)


class DetalleIVAInversionSujetoPasivo(DesgloseIVA):
    DetalleIVA = fields.List(fields.Nested(DetalleIVARecibida), required=True)


class DesgloseFacturaRecibida(MySchema):
    InversionSujetoPasivo = fields.Nested(DetalleIVAInversionSujetoPasivo)
    DesgloseIVA = fields.Nested(DesgloseIVARecibida)

    @staticmethod
    def get_atleast_one_of():
        return ['InversionSujetoPasivo', 'DesgloseIVA']


class DetalleFacturaRecibida(DetalleFactura):
    ClaveRegimenEspecialOTrascendencia = CustomStringField(
        required=True,
        error_messages={
            'invalid': 'La Clave de Regimen Especial para '
                       'Facturas Recibidas no es valida'
        }
    )
    DesgloseFactura = fields.Nested(DesgloseFacturaRecibida, required=True)
    Contraparte = fields.Nested(Contraparte, required=True)
    FechaRegContable = DateString(required=True)  # TODO FechaRegContable ≥ FechaExpedicionFacturaEmisor
    CuotaDeducible = fields.Float(required=True)

    def validate_clave_regimen_especial_o_trascendencia(self, value):
        self.validate_field_is_one_of(
            value=value, choices=sorted(dict(CRE_FACTURAS_RECIBIDAS).keys()),
            field_name='Clave de Regimen Especial para Facturas Recibidas'
        )

    def validate_fecha_reg_contable(self, value):
        self.validate_field_max_length(
            value=value, field_name='Fecha de Registro Contable',
            max_chars=10
        )


class FacturaRecibida(Factura):
    # Campos específicos para facturas recibidas
    IDFactura = fields.Nested(IdentificacionFacturaRecibida, required=True)
    FacturaRecibida = fields.Nested(DetalleFacturaRecibida, required=True)


class RegistroFacturasRecibidas(RegistroFacturas):
    RegistroLRFacturasRecibidas = fields.Nested(FacturaRecibida, required=True)


class SuministroFacturasRecibidas(MySchema):
    SuministroLRFacturasRecibidas = fields.Nested(
        RegistroFacturasRecibidas, required=True
    )
