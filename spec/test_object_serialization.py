# coding=utf-8

from sii.resource import SII
from sii.models import *
from sii import __SII_VERSION__
from expects import *
from spec.testing_data import DataGenerator

with description("El XML Generado"):
    with before.all:
        data_gen = DataGenerator()
        self.in_invoice = data_gen.get_in_invoice()
        self.out_invoice = data_gen.get_out_invoice()
        self.in_refund = data_gen.get_in_refund_invoice()
        self.out_refund = data_gen.get_out_refund_invoice()

        # Example invoice to check common fields
        self.invoice = self.out_invoice

        obj = SII.generate_object(self.invoice)

        # TODO delete print object
        print '\n'
        print '============ RESULTADO DEL DUMP ====================='
        from pprintpp import pprint
        pprint(obj)
        print '====================================================='

        self.cabecera = obj['SuministroLRFacturasEmitidas']['Cabecera']
        self.factura_emitida = obj[
            'SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']

        self.factura = self.factura_emitida

    with description("en la cabecera"):
        with it("la versión es la versión del SII"):
            expect(self.cabecera['IDVersionSii']).to(equal(__SII_VERSION__))
        with context("cuando es de tipo alta"):
            with it("el tipo de comunicación debe ser 'A0'"):
                expect(self.cabecera['TipoComunicacion']).to(equal('A0'))
        with description("en el titular"):
            with it("el nif deben ser los del titular"):
                expect(
                    self.cabecera['Titular']['NIF']
                ).to(equal(self.invoice.company_id.partner_id.vat))
            with it("el nombre y apellidos deben ser los del titular"):
                expect(
                    self.cabecera['Titular']['NombreRazon']
                ).to(equal(self.invoice.company_id.partner_id.name))

    with description("en los datos del período"):
        with it("el ejercicio es el correspondiente al año de la factura"):
            expect(
                self.factura['PeriodoImpositivo']['Ejercicio']
            ).to(equal(self.invoice.period_id.name[3:7]))
        with it("el período es el correspondiente al mes de la factura"):
            expect(
                self.factura['PeriodoImpositivo']['Periodo']
            ).to(equal(self.invoice.period_id.name[0:2]))

    with description("en los datos de la factura"):
        with it("la ClaveRegimenEspecialOTrascendencia debe ser '01'"):
            expect(
                CLAVE_REGIMEN_ESPECIAL_FACTURAS_EMITIDAS
            ).to(contain(self.factura['FacturaExpedida'][
                                         'ClaveRegimenEspecialOTrascendencia']))

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
        with it("el número de la factura debe ser igual que el de la factura original"):
            expect(
                self.factura['IDFactura']['NumSerieFacturaEmisor']
            ).to(equal(self.invoice.number))

        with it("el tipo de la factura es 'F1'"):
            expect(
                self.factura['FacturaExpedida']['TipoFactura']
            ).to(equal('F1'))
