# coding=utf-8

from sii.resource import SII
import sii
from expects import *


class Period():
    def __init__(self):
        pass


class Partner():
    def __init__(self, name, nif):
        self.name = name
        self.nif = nif
        pass


class Invoice():
    def __init__(self, number, type, partner, period=None):
        self.number = number
        self.type = type
        self.partner_id = partner
        self.period = period
        self.tax_ids = []


with description("El XML Generado"):
    with before.all:
        invoice = Invoice('F012345')
        self.xml = SII.generate_xml(invoice)

    with description("en la cabecera"):
        with context("cuando es de tipo alta"):
            with it("el tipo de comunicación debe ser 'A0'"):

                expect(self.xml['cabecera']['tipo_comunicacion']).to(equal('A0'))

    with _description("en los datos del período"):
        with it("el ejercicio es el correspondiente al año de la factura"):
            pass
        with it("el período es el correspondiente al mes de la factura"):
            pass

    with _description("en los datos de la identificación de la factura"):
        with it("el NIF de la factura es el NIF del emisor"):
            pass
        with context("en las facturas emitidas"):
            with _it("el número de factura debe ser igual al número de la factura original"):
                pass
        with context("en las facturas recibidas"):
            with _it("el número de factura debe ser igual al número de factura"):
                pass
        with it("la fecha de la factura es la fecha de expedición de la factura"):
            pass

    with description("en la factura"):
        with before.all:
            inv = Invoice('F012345')
        # with it("el número de la factura debe ser igual que el de la factura original"):
        #     fact = Factura()
        #
        #     expect(fact.numero).to(equal(inv.number))
