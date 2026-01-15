# coding=utf-8
"""
Models Marshmallow per validar les estructures XML del SII ATC

Aquests models són adaptacions dels models AEAT per treballar amb IGIC
en lloc d'IVA, mantenint la mateixa estructura de validació.
"""

from marshmallow import Schema, fields, post_dump
from marshmallow import validates_schema, ValidationError
from sii.atc import __ATC_SII_VERSION__
from sii.atc.constants import (
    TIPO_COMUNICACION_VALUES,
    TIPO_FACTURA_VALUES,
    PERIODO_VALUES,
    TIPO_IMPOSITIVO_IGIC_VALUES,
    TIPO_NO_EXENTA_VALUES,
    TIPO_RECTIFICATIVA_VALUES,
    CODIGO_PAIS_VALUES,
    ID_TYPE_VALUES,
    CLAVE_REGIMEN_ESPECIAL_VALUES
)
from datetime import datetime
import re


def convert_camel_case_to_underscore(name):
    """Converteix CamelCase a snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_error_message(field_name, value, error_msg):
    """Genera missatge d'error formatat"""
    msg = '{0}: "{1}" - {2}'.format(field_name, value, error_msg)
    return msg


class CustomStringField(fields.String):
    """Camp String personalitzat"""
    
    default_error_messages = {
        'invalid': 'No es un String valido'
    }


class DateString(fields.String):
    """Camp per dates en format String"""
    
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
    """Schema base amb configuració comuna"""
    
    class Meta:
        strict = True
        ordered = True


class TitularSchema(MySchema):
    """Schema per al Titular (emissor de la comunicació)"""
    
    nombre_razon = CustomStringField(required=True, data_key='NombreRazon')
    nif = CustomStringField(required=True, data_key='NIF')


class CabeceraSchema(MySchema):
    """Schema per a la Capçalera del missatge SII"""
    
    id_version_sii = CustomStringField(
        required=True, 
        data_key='IDVersionSii',
        validate=lambda x: x == __ATC_SII_VERSION__
    )
    titular = fields.Nested(TitularSchema, required=True, data_key='Titular')
    tipo_comunicacion = CustomStringField(
        required=True,
        data_key='TipoComunicacion',
        validate=lambda x: x in TIPO_COMUNICACION_VALUES
    )


class IDOtroSchema(MySchema):
    """Schema per identificació alternativa al NIF"""
    
    codigo_pais = CustomStringField(
        required=True,
        data_key='CodigoPais',
        validate=lambda x: x in CODIGO_PAIS_VALUES
    )
    id_type = CustomStringField(
        required=True,
        data_key='IDType',
        validate=lambda x: x in ID_TYPE_VALUES
    )
    id_field = CustomStringField(required=True, data_key='ID')


class IDEmisorFacturaSchema(MySchema):
    """Schema per identificar l'emissor de la factura"""
    
    nif = CustomStringField(data_key='NIF')
    id_otro = fields.Nested(IDOtroSchema, data_key='IDOtro')
    
    @validates_schema
    def validate_id(self, data):
        """Ha de tenir NIF o IDOtro, però no ambdós"""
        has_nif = 'nif' in data and data['nif']
        has_id_otro = 'id_otro' in data and data['id_otro']
        
        if not has_nif and not has_id_otro:
            raise ValidationError('Debe tener NIF o IDOtro')
        if has_nif and has_id_otro:
            raise ValidationError('No puede tener NIF e IDOtro simultáneamente')


class ContraparteSchema(MySchema):
    """Schema per a la Contraparte (client/proveïdor)"""
    
    nombre_razon = CustomStringField(required=True, data_key='NombreRazon')
    nif = CustomStringField(data_key='NIF')
    id_otro = fields.Nested(IDOtroSchema, data_key='IDOtro')
    
    @validates_schema
    def validate_id(self, data):
        """Ha de tenir NIF o IDOtro"""
        has_nif = 'nif' in data and data['nif']
        has_id_otro = 'id_otro' in data and data['id_otro']
        
        if not has_nif and not has_id_otro:
            raise ValidationError('Debe tener NIF o IDOtro')


class DetalleIGICSchema(MySchema):
    """
    Schema per al detall d'IGIC
    
    DIFERÈNCIA CLAU: Aquest schema és per IGIC, no IVA
    Utilitza els tipus impositius d'IGIC (0, 3, 7, 9.5, 13.5, 15, 20)
    """
    
    base_imponible = fields.Decimal(
        required=True,
        data_key='BaseImponible',
        places=2
    )
    tipo_impositivo = fields.Decimal(
        required=True,
        data_key='TipoImpositivo',
        places=2,
        validate=lambda x: float(x) in TIPO_IMPOSITIVO_IGIC_VALUES
    )
    cuota_repercutida = fields.Decimal(
        data_key='CuotaRepercutida',
        places=2
    )
    cuota_soportada = fields.Decimal(
        data_key='CuotaSoportada',
        places=2
    )
    
    @validates_schema
    def validate_cuota(self, data):
        """Ha de tenir cuota_repercutida o cuota_soportada"""
        has_repercutida = 'cuota_repercutida' in data
        has_soportada = 'cuota_soportada' in data
        
        if not has_repercutida and not has_soportada:
            raise ValidationError('Debe tener CuotaRepercutida o CuotaSoportada')


class DesgloseIGICSchema(MySchema):
    """
    Schema per al desglossament d'IGIC
    
    DIFERÈNCIA CLAU: DesgloseIGIC en lloc de DesgloseIVA
    """
    
    detalle_igic = fields.List(
        fields.Nested(DetalleIGICSchema),
        data_key='DetalleIGIC'
    )


class TipoDesgloseSchema(MySchema):
    """Schema per al tipus de desglossament"""
    
    desglose_igic = fields.Nested(
        DesgloseIGICSchema,
        data_key='DesgloseIGIC'
    )


class PeriodoLiquidacionSchema(MySchema):
    """Schema per al període de liquidació"""
    
    ejercicio = CustomStringField(
        required=True,
        data_key='Ejercicio',
        validate=lambda x: len(x) == 4 and x.isdigit()
    )
    periodo = CustomStringField(
        required=True,
        data_key='Periodo',
        validate=lambda x: x in PERIODO_VALUES
    )


class IDFacturaSchema(MySchema):
    """Schema per identificar una factura"""
    
    id_emisor_factura = fields.Nested(
        IDEmisorFacturaSchema,
        required=True,
        data_key='IDEmisorFactura'
    )
    num_serie_factura_emisor = CustomStringField(
        required=True,
        data_key='NumSerieFacturaEmisor'
    )
    fecha_expedicion_factura_emisor = DateString(
        required=True,
        data_key='FechaExpedicionFacturaEmisor'
    )


class FacturaExpedidaSchema(MySchema):
    """Schema per factura expedida (emesa)"""
    
    tipo_factura = CustomStringField(
        required=True,
        data_key='TipoFactura',
        validate=lambda x: x in TIPO_FACTURA_VALUES
    )
    clave_regimen_especial_o_trascendencia = CustomStringField(
        required=True,
        data_key='ClaveRegimenEspecialOTrascendencia',
        validate=lambda x: x in CLAVE_REGIMEN_ESPECIAL_VALUES
    )
    importe_total = fields.Decimal(
        required=True,
        data_key='ImporteTotal',
        places=2
    )
    descripcion_operacion = CustomStringField(
        required=True,
        data_key='DescripcionOperacion',
        validate=lambda x: len(x) <= 500
    )
    tipo_desglose = fields.Nested(
        TipoDesgloseSchema,
        data_key='TipoDesglose'
    )


class FacturaRecibidaSchema(MySchema):
    """Schema per factura rebuda"""
    
    tipo_factura = CustomStringField(
        required=True,
        data_key='TipoFactura',
        validate=lambda x: x in TIPO_FACTURA_VALUES
    )
    clave_regimen_especial_o_trascendencia = CustomStringField(
        required=True,
        data_key='ClaveRegimenEspecialOTrascendencia',
        validate=lambda x: x in CLAVE_REGIMEN_ESPECIAL_VALUES
    )
    importe_total = fields.Decimal(
        required=True,
        data_key='ImporteTotal',
        places=2
    )
    descripcion_operacion = CustomStringField(
        required=True,
        data_key='DescripcionOperacion',
        validate=lambda x: len(x) <= 500
    )
    desglose_factura = fields.Nested(
        TipoDesgloseSchema,
        data_key='DesgloseFactura'
    )


class RegistroLRFacturasEmitidasSchema(MySchema):
    """Schema per registre de factures emeses"""
    
    periodo_liquidacion = fields.Nested(
        PeriodoLiquidacionSchema,
        required=True,
        data_key='PeriodoLiquidacion'
    )
    id_factura = fields.Nested(
        IDFacturaSchema,
        required=True,
        data_key='IDFactura'
    )
    factura_expedida = fields.Nested(
        FacturaExpedidaSchema,
        required=True,
        data_key='FacturaExpedida'
    )
    contraparte = fields.Nested(
        ContraparteSchema,
        data_key='Contraparte'
    )


class RegistroLRFacturasRecibidasSchema(MySchema):
    """Schema per registre de factures rebudes"""
    
    periodo_liquidacion = fields.Nested(
        PeriodoLiquidacionSchema,
        required=True,
        data_key='PeriodoLiquidacion'
    )
    id_factura = fields.Nested(
        IDFacturaSchema,
        required=True,
        data_key='IDFactura'
    )
    factura_recibida = fields.Nested(
        FacturaRecibidaSchema,
        required=True,
        data_key='FacturaRecibida'
    )


class SuministroLRFacturasEmitidasSchema(MySchema):
    """Schema principal per enviament de factures emeses"""
    
    cabecera = fields.Nested(
        CabeceraSchema,
        required=True,
        data_key='Cabecera'
    )
    registro_lr_facturas_emitidas = fields.List(
        fields.Nested(RegistroLRFacturasEmitidasSchema),
        required=True,
        data_key='RegistroLRFacturasEmitidas'
    )


class SuministroLRFacturasRecibidasSchema(MySchema):
    """Schema principal per enviament de factures rebudes"""
    
    cabecera = fields.Nested(
        CabeceraSchema,
        required=True,
        data_key='Cabecera'
    )
    registro_lr_facturas_recibidas = fields.List(
        fields.Nested(RegistroLRFacturasRecibidasSchema),
        required=True,
        data_key='RegistroLRFacturasRecibidas'
    )
