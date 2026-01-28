# coding=utf-8
"""
Models Marshmallow per validar les estructures XML del SII ATC

Aquests models són adaptacions dels models AEAT per treballar amb IGIC
en lloc d'IVA, seguint EXACTAMENT la mateixa estructura que sii/models/invoices_record.py
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
    """Camp per dates en format String
    
    Accepta format YYYY-MM-DD (ISO) i el serialitza a DD-MM-YYYY (ATC format)
    """
    
    def _validate(self, value):
        if value is None:
            return None
        try:
            # Validar que és una data vàlida en format ISO
            datetime.strptime(value, '%Y-%m-%d')
        except (ValueError, AttributeError):
            raise ValidationError('Invalid date string, expected YYYY-MM-DD format', value)
    
    def _serialize(self, value, attr, obj, **kwargs):
        """Converteix de YYYY-MM-DD a DD-MM-YYYY"""
        if value is None:
            return None
        
        # Si ja està en format DD-MM-YYYY, retornar-lo
        if len(value) == 10 and value[2] == '-' and value[5] == '-':
            return value
            
        # Convertir de YYYY-MM-DD a DD-MM-YYYY
        try:
            date_obj = datetime.strptime(value, '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%Y')
        except (ValueError, AttributeError):
            # Si falla, retornar el valor original
            return value


class MySchema(Schema):
    """Schema base amb configuració comuna"""
    
    class Meta:
        strict = True
        ordered = True
    
    @staticmethod
    def validate_field_is_one_of(value, field_name, choices):
        """Valida que el valor sigui un dels permesos"""
        if value not in choices:
            raise ValidationError(
                get_error_message(field_name, value, 'El campo es incorrecto')
            )


# ============================================================================
# SCHEMAS BÀSICS (Titular, Cabecera, IDOtro, etc.)
# ============================================================================

class Titular(MySchema):
    """Titular dels llibres de registre"""
    NombreRazon = CustomStringField(required=True)
    NIF = CustomStringField(required=True)


class Cabecera(MySchema):
    """Capçalera del missatge SII"""
    IDVersionSii = CustomStringField(required=True, default=__ATC_SII_VERSION__)
    Titular = fields.Nested(Titular, required=True)
    TipoComunicacion = CustomStringField(required=True)
    
    @staticmethod
    def validate_id_version_sii(value):
        if value != __ATC_SII_VERSION__:
            raise ValidationError(
                'La version del SII ATC es incorrecta. '
                'Se esperaba "{}"'.format(__ATC_SII_VERSION__)
            )
    
    def validate_tipo_comunicacion(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Tipo de Comunicacion',
            choices=TIPO_COMUNICACION_VALUES
        )


class IDOtro(MySchema):
    """Identificació alternativa al NIF"""
    CodigoPais = CustomStringField(required=True)
    IDType = CustomStringField(required=True)
    ID = CustomStringField(required=True)
    
    def validate_codigo_pais(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Codigo Pais',
            choices=CODIGO_PAIS_VALUES
        )
    
    def validate_id_type(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='IDType',
            choices=ID_TYPE_VALUES.keys()
        )


class NIF(MySchema):
    """NIF espanyol"""
    NIF = CustomStringField(required=True)


class IDEmisorFactura(NIF):
    """ID de l'emissor de la factura"""
    pass


class Contraparte(MySchema):
    """Informació de la contraparte (client/proveïdor)"""
    NombreRazon = CustomStringField(required=True)
    # Només un dels dos: NIF o IDOtro
    NIF = CustomStringField()
    IDOtro = fields.Nested(IDOtro)
    
    @validates_schema
    def validate_one_id(self, data):
        """Validar que hi hagi exactament un camp d'identificació"""
        has_nif = 'NIF' in data and data['NIF']
        has_idotro = 'IDOtro' in data and data['IDOtro']
        
        if not has_nif and not has_idotro:
            raise ValidationError('Cal proporcionar NIF o IDOtro')
        if has_nif and has_idotro:
            raise ValidationError('Només es pot proporcionar NIF o IDOtro, no ambdós')


# ============================================================================
# SCHEMAS PER IGIC (DetalleIGIC, DesgloseIGIC, etc.)
# ============================================================================

class DetalleIGIC(MySchema):
    """Detall d'IGIC per tipus impositiu"""
    TipoImpositivo = fields.Decimal(places=2)  # Optional segons XSD
    BaseImponible = fields.Decimal(required=True, places=2)
    CuotaRepercutida = fields.Decimal(places=2)  # Optional
    CuotaSoportada = fields.Decimal(places=2)  # Optional (només per factures rebudes)
    
    def validate_tipo_impositivo(self, value):
        """Validar que el tipus impositiu sigui un dels permesos"""
        if value is not None:
            self.validate_field_is_one_of(
                value=float(value), field_name='TipoImpositivo',
                choices=TIPO_IMPOSITIVO_IGIC_VALUES
            )


class DesgloseIGIC(MySchema):
    """Desglose d'IGIC amb llista de detalls"""
    DetalleIGIC = fields.List(fields.Nested(DetalleIGIC), required=True)


class NoExenta(MySchema):
    """Operació no exempta"""
    TipoNoExenta = CustomStringField(required=True)
    DesgloseIGIC = fields.Nested(DesgloseIGIC, required=True)
    
    def validate_tipo_no_exenta(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='TipoNoExenta',
            choices=TIPO_NO_EXENTA_VALUES
        )


class Exenta(MySchema):
    """Operació exempta"""
    BaseImponible = fields.Decimal(required=True, places=2)
    CausaExencion = CustomStringField(required=True)


class Sujeta(MySchema):
    """Operació subjecta a IGIC"""
    # Només un dels dos: Exenta o NoExenta
    Exenta = fields.Nested(Exenta)
    NoExenta = fields.Nested(NoExenta)
    
    @validates_schema
    def validate_one_type(self, data):
        """Validar que hi hagi exactament un camp: Exenta o NoExenta"""
        has_exenta = 'Exenta' in data and data['Exenta']
        has_no_exenta = 'NoExenta' in data and data['NoExenta']
        
        if not has_exenta and not has_no_exenta:
            raise ValidationError('Cal proporcionar Exenta o NoExenta')
        if has_exenta and has_no_exenta:
            raise ValidationError('Només es pot proporcionar Exenta o NoExenta, no ambdós')


class NoSujeta(MySchema):
    """Operació no subjecta"""
    ImportePorArticulos7_14_Otros = fields.Decimal(places=2)
    ImporteTAIReglasLocalizacion = fields.Decimal(places=2)


# ============================================================================
# SCHEMAS PER TIPUS DE DESGLOSE
# ============================================================================

class PrestacionServicios(MySchema):
    """Prestació de serveis"""
    # Només un dels dos: Sujeta o NoSujeta
    Sujeta = fields.Nested(Sujeta)
    NoSujeta = fields.Nested(NoSujeta)


class Entrega(MySchema):
    """Lliurament de béns"""
    # Només un dels dos: Sujeta o NoSujeta
    Sujeta = fields.Nested(Sujeta)
    NoSujeta = fields.Nested(NoSujeta)


class DesgloseTipoOperacion(MySchema):
    """Desglose per tipus d'operació"""
    PrestacionServicios = fields.Nested(PrestacionServicios)
    Entrega = fields.Nested(Entrega)


class TipoDesglose(MySchema):
    """Tipus de desglose (per operació o per destinatari)"""
    DesgloseTipoOperacion = fields.Nested(DesgloseTipoOperacion, required=True)
    # TODO: Afegir DesgloseFactura si és necessari


# ============================================================================
# SCHEMAS PER FACTURES
# ============================================================================

class PeriodoLiquidacion(MySchema):
    """Període de liquidació"""
    Ejercicio = CustomStringField(required=True)
    Periodo = CustomStringField(required=True)
    
    def validate_ejercicio(self, value):
        """Validar que l'exercici sigui un any vàlid"""
        if not value.isdigit() or int(value) < 2000 or int(value) > 3000:
            raise ValidationError(
                get_error_message('Ejercicio', value, 'El campo es incorrecto')
            )
    
    def validate_periodo(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='Periodo',
            choices=PERIODO_VALUES
        )


class IDFactura(MySchema):
    """Identificació de la factura"""
    IDEmisorFactura = fields.Nested(IDEmisorFactura, required=True)
    NumSerieFacturaEmisor = CustomStringField(required=True)
    FechaExpedicionFacturaEmisor = DateString(required=True)


class FacturaExpedida(MySchema):
    """Dades de la factura expedida"""
    TipoFactura = CustomStringField(required=True)
    ClaveRegimenEspecialOTrascendencia = CustomStringField(required=True)
    ImporteTotal = fields.Decimal(required=True, places=2)
    DescripcionOperacion = CustomStringField(required=True)
    TipoDesglose = fields.Nested(TipoDesglose, required=True)
    Contraparte = fields.Nested(Contraparte, required=True)
    # Camps opcionals
    EmitidaPorTerceros = CustomStringField()
    FacturaSimplificadaArt7_2_9 = CustomStringField()
    
    def validate_tipo_factura(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='TipoFactura',
            choices=TIPO_FACTURA_VALUES
        )
    
    def validate_clave_regimen(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='ClaveRegimenEspecialOTrascendencia',
            choices=[code for code, desc in CLAVE_REGIMEN_ESPECIAL_VALUES]
        )


class DesgloseFactura(MySchema):
    """Desglose de factura rebuda"""
    DesgloseIGIC = fields.Nested(DesgloseIGIC, required=True)


class FacturaRecibida(MySchema):
    """Dades de la factura rebuda"""
    TipoFactura = CustomStringField(required=True)
    ClaveRegimenEspecialOTrascendencia = CustomStringField(required=True)
    ImporteTotal = fields.Decimal(required=True, places=2)
    DescripcionOperacion = CustomStringField(required=True)
    DesgloseFactura = fields.Nested(DesgloseFactura, required=True)
    Contraparte = fields.Nested(Contraparte, required=True)
    FechaRegContable = DateString(required=True)
    CuotaDeducible = fields.Decimal(places=2)
    # Camps opcionals
    FechaOperacion = DateString()
    
    def validate_tipo_factura(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='TipoFactura',
            choices=TIPO_FACTURA_VALUES
        )
    
    def validate_clave_regimen(self, value):
        self.validate_field_is_one_of(
            value=value, field_name='ClaveRegimenEspecialOTrascendencia',
            choices=[code for code, desc in CLAVE_REGIMEN_ESPECIAL_VALUES]
        )


# ============================================================================
# SCHEMAS PER REGISTRES
# ============================================================================

class RegistroLRFacturasEmitidas(MySchema):
    """Registre de factura emesa al llibre de registre"""
    PeriodoLiquidacion = fields.Nested(PeriodoLiquidacion, required=True)
    IDFactura = fields.Nested(IDFactura, required=True)
    FacturaExpedida = fields.Nested(FacturaExpedida, required=True)


class RegistroLRFacturasRecibidas(MySchema):
    """Registre de factura rebuda al llibre de registre"""
    PeriodoLiquidacion = fields.Nested(PeriodoLiquidacion, required=True)
    IDFactura = fields.Nested(IDFactura, required=True)
    FacturaRecibida = fields.Nested(FacturaRecibida, required=True)


# ============================================================================
# SCHEMAS PRINCIPALS (Suministros)
# ============================================================================

class SuministroLRFacturasEmitidas(MySchema):
    """Suministro de factures emeses"""
    Cabecera = fields.Nested(Cabecera, required=True)
    RegistroLRFacturasEmitidas = fields.Nested(
        RegistroLRFacturasEmitidas,
        required=True
    )


class SuministroLRFacturasRecibidas(MySchema):
    """Suministro de factures rebudes"""
    Cabecera = fields.Nested(Cabecera, required=True)
    RegistroLRFacturasRecibidas = fields.Nested(
        RegistroLRFacturasRecibidas,
        required=True
    )
