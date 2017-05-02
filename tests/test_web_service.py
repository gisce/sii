# -*- coding: UTF-8 -*-

from expects import *
import xml.dom.minidom
from sii.resource import SII
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


with description("El XML Generado"):
    with before.all:
        print 'Generando obj'
        period = Period(name='03/2016')
        tax_line = [
            InvoiceLineTaxes('IVA 21%', base_imponible=12.34),
            InvoiceLineTaxes('IBI 15%', base_imponible=56.78)
        ]
        partner = Partner(name='Francisco García', nif='12345678T')
        invoice = Invoice(
            number='F012345', type='out_invoice', partner=partner,
            amount_total=15, period_id=period, date_invoice='2016-03-25',
            tax_line_ids=tax_line
        )

        dict_to_xml = SII.generate_object(invoice)
        dict_to_xml = dicttoxml(dict_to_xml, root=False, attr_type=False)
        xml_pretty = xml.dom.minidom.parseString(dict_to_xml)
        pretty_xml_as_string = xml_pretty.toprettyxml()
        print 'El XML generado es:\n', pretty_xml_as_string