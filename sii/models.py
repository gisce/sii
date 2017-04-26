# coding=utf-8

from marshmallow import Schema, fields, validate
from sii import __SII_VERSION__


class Titular(Schema):
    nombre_razon = fields.String(
        attribute='NombreRazon', dump_to='NombreRazon',
        validate=validate.Length(max=40, error='Nombre demasiado largo')
    )
    nif = fields.String(
        attribute='NIF', dump_to='NIF',
        validate=validate.Length(max=9, error='NIF demasiado largo')  # TODO validate if it belongs to a NIF ??
    )


class Cabecera(Schema):
    version = fields.String(
        attribute='IDVersionSii', dump_to='IDVersionSii',
        default=__SII_VERSION__
    )
    titular = fields.Nested(Titular, attribute='Titular', dump_to='Titular')
    tipo_comunicacion = fields.String(
        attribute='TipoComunicacion', dump_to='TipoComunicacion'
    )


class PeriodoImpositivo(Schema):
    ejercicio = fields.String(dump_to='Ejercicio')  # TODO validate Año en formato 'YYYY'
    periodo = fields.String(dump_to='Periodo')  # TODO validate Enumeration '01' para enero, '02' para febrero, ..., '0A' Periodicidad anual


class EmisorFactura(Schema):
    nif = fields.String(dump_to='NIF')


class IDFactura(Schema):
    IDEmisorFactura = fields.Nested(EmisorFactura)
    NumSerieFacturaEmisor = fields.String()
    FechaExpedicionFacturaEmisor = fields.String()


class Factura(Schema):
    # Campos comunes de una factura
    periodo = fields.Nested(PeriodoImpositivo, dump_to='PeriodoImpositivo')
    detalle_factura = fields.Nested(
        IDFactura, attribute='IDFactura', dump_to='IDFactura'
    )


class FacturaEmitida(IDFactura):
    # Campos específicos para facturas emitidas
    factura_emitida = fields.String(dump_to='FacturaExpedida')  # TODO add missing fields


class FacturaRecibida(IDFactura):
    # Campos específicos para facturas recibidas
    factura_recibida = fields.String(dump_to='FacturaRecibida')  # TODO add missing fields


class RegistroFacturasEmitidas(Schema):
    cabecera = fields.Nested(Cabecera, attribute='Cabecera', dump_to='Cabecera')
    factura = fields.Nested(
        Factura, attribute='RegistroLRFacturasEmitidas',
        dump_to='RegistroLRFacturasEmitidas'
    )
    # TODO lista_facturas = fields.List(fields.Nested(Factura, dump_to='Factura'), validate=validate.Length(max=10000, error='No puede haber más de 10000 facturas'))


class SuministroFacturasEmitidas(Schema):
    SuministroLRFacturasEmitidas = fields.Nested(RegistroFacturasEmitidas)


class SuministroFacturasRecibidas(Schema):
    pass
