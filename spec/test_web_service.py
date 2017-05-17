# -*- coding: UTF-8 -*-

from expects import *
import xml.dom.minidom
from sii.server import *
from dicttoxml import dicttoxml

class Period():
    def __init__(self, name):
        self.name = name


class Partner():
    def __init__(self, name, nif):
        self.name = name
        self.nif = nif


class InvoiceLineTaxes():
    def __init__(self, name, base_imponible):
        self.name = name
        self.base = base_imponible


class Invoice():
    def __init__(self, number, type, partner, amount_total, period_id, date_invoice, tax_line_ids):
        self.number = number
        self.type = type
        self.partner_id = partner
        self.period_id = period_id
        self.amount_total = amount_total
        self.date_invoice = date_invoice
        self.tax_line = tax_line_ids


with description("The webservice steps: "):
    with before.all:
        period = Period(name='03/2016')
        tax_line = [
            InvoiceLineTaxes('IVA 21%', base_imponible=12.34),
            InvoiceLineTaxes('IBI 15%', base_imponible=56.78)
        ]
        partner = Partner(name='Francisco García', nif='12345678T')
        self.invoice = Invoice(
            number='F012345', type='out_invoice', partner=partner,
            amount_total=15, period_id=period, date_invoice='2016-03-25',
            tax_line_ids=tax_line
        )
        self.expected_dict = {
            u'SuministroLRFacturasEmitidas': {
                u'Cabecera': {
                    u'IDVersionSii': u'0.6',
                    u'TipoComunicacion': u'A0',
                    u'Titular': {
                        u'NIF': u'12345678T',
                        u'NombreRazon': u'Francisco García',
                    },
                },
                u'RegistroLRFacturasEmitidas': {
                    u'FacturaExpedida': {
                        u'ClaveRegimenEspecialOTrascendencia': u'',
                        u'Contraparte': {u'NIF': u'', u'NombreRazon': u''},
                        u'DescripcionOperacion': u'',
                        u'ImporteTotal': 15.0,
                        u'TipoDesglose': {
                            u'DesgloseFactura': {
                                u'Sujeta': {
                                    u'NoExenta': {
                                        u'DesgloseIVA': {
                                            u'DetalleIVA': {
                                                u'BaseImponible': 12.34,
                                                u'CuotaRepercutida': 0.0,
                                                u'TipoImpositivo': u'',
                                            },
                                        },
                                        u'TipoNoExenta': u'S1',
                                    },
                                },
                            },
                        },
                        u'TipoFactura': u'F1',
                    },
                    u'IDFactura': {
                        u'FechaExpedicionFacturaEmisor': u'25-03-2016',
                        u'IDEmisorFactura': {u'NIF': u''},
                        u'NumSerieFacturaEmisor': u'F012345',
                    },
                    u'PeriodoImpositivo': {u'Ejercicio': u'2016', u'Periodo': u'03'},
                },
            },
        }

        # # xml_pretty = xml.dom.minidom.parseString(xml_from_dict)
        # # pretty_xml_as_string = xml_pretty.toprettyxml()
        #
        # print '\n'
        # print '============ RESULT FROM DICTTOXML ====================='
        # print(pretty_xml_as_string)
        # print '====================================================='

    with description("1. generate the dictionary"):
        with it(" from an invoice object"):

            s = ServiceSII()
            head, body = s.get_msg(invoice=self.invoice)

