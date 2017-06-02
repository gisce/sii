# coding=utf-8

from marshmallow import fields, validate
from invoices import MySchema, DateString
from invoices import Cabecera, PeriodoImpositivo, Contraparte

FACTURA_MODIFICADA_VALUES = ['S', 'N']


class RangoFechaPresentacion(MySchema):
    Desde = DateString()
    Hasta = DateString()


class FiltroConsulta(MySchema):
    PeriodoImpositivo = fields.Nested(PeriodoImpositivo, required=True)
    # TODO add IDFactura
    Contraparte = fields.Nested(Contraparte)
    FechaPresentacion = fields.Nested(RangoFechaPresentacion)
    FacturaModificada = fields.String(
        validate=validate.OneOf(FACTURA_MODIFICADA_VALUES)
    )
    # TODO add EstadoCuadre
    # TODO add ClavePaginacion


class ConsultaFacturas(MySchema):
    Cabecera = fields.Nested(Cabecera, required=True)


class ConsultaFacturasRecibidas(ConsultaFacturas):
    FiltroConsulta = fields.Nested(FiltroConsulta, required=True)


class ConsultaLRFacturasRecibidas(MySchema):
    ConsultaLRFacturasRecibidas = fields.Nested(
        ConsultaFacturasRecibidas, required=True
    )


class ConsultaFacturasRecibidas(ConsultaFacturas):
    FiltroConsulta = fields.Nested(FiltroConsulta, required=True)


class ConsultaLRFacturasEmitidas(MySchema):
    ConsultaLRFacturasEmitidas = fields.Nested(
        ConsultaFacturasEmitidas, required=True
    )
