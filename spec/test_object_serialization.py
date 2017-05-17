# coding=utf-8

from sii.resource import SII
from sii.models.invoices_record import CLAVE_REGIMEN_ESPECIAL_FACTURAS_EMITIDAS
from expects import *
from spec.testing_data import DataGenerator

with description('El XML Generado'):
    with before.all:
        data_gen = DataGenerator()
        self.in_invoice = data_gen.get_in_invoice()
        self.out_invoice = data_gen.get_out_invoice()
        self.in_refund = data_gen.get_in_refund_invoice()
        self.out_refund = data_gen.get_out_refund_invoice()

        # Example invoice to check common fields
        self.invoice = self.out_invoice

        self.obj = SII.generate_object(self.invoice)

    with description('en la cabecera'):
        with before.all:
            self.cabecera = self.obj['SuministroLRFacturasEmitidas']['Cabecera']

        with it('la versión es la "0.7"'):
            expect(self.cabecera['IDVersionSii']).to(equal('0.7'))

        with context('cuando es de tipo alta'):
            with it('el tipo de comunicación debe ser "A0"'):
                expect(self.cabecera['TipoComunicacion']).to(equal('A0'))

        with context('en el titular'):
            with it('el nif deben ser los del titular'):
                expect(
                    self.cabecera['Titular']['NIF']
                ).to(equal(self.invoice.company_id.partner_id.vat))

            with it('el nombre y apellidos deben ser los del titular'):
                expect(
                    self.cabecera['Titular']['NombreRazon']
                ).to(equal(self.invoice.company_id.partner_id.name))

    with description('en los datos de la factura'):
        with before.all:
            self.factura = (
                self.obj['SuministroLRFacturasEmitidas'][
                    'RegistroLRFacturasEmitidas']
            )

        with it('la ClaveRegimenEspecialOTrascendencia debe ser "01"'):
            expect(
                CLAVE_REGIMEN_ESPECIAL_FACTURAS_EMITIDAS
            ).to(contain(
                (self.factura['FacturaExpedida']
                 ['ClaveRegimenEspecialOTrascendencia'])
            ))

        with it('el número de la factura debe ser el de la factura original'):
            expect(
                self.factura['IDFactura']['NumSerieFacturaEmisor']
            ).to(equal(self.invoice.number))

        with it('el tipo de la factura es "F1"'):
            expect(
                self.factura['FacturaExpedida']['TipoFactura']
            ).to(equal('F1'))

        with context('en los datos del período'):
            with before.all:
                self.periodo = self.factura['PeriodoImpositivo']

            with it('el ejercicio es el correspondiente al año de la factura'):
                expect(
                    self.periodo['Ejercicio']
                ).to(equal(self.invoice.period_id.name[3:7]))

            with it('el período es el correspondiente al mes de la factura'):
                expect(
                    self.periodo['Periodo']
                ).to(equal(self.invoice.period_id.name[0:2]))

        with context('en los detalles del IVA'):
            with before.all:
                self.detalle_iva = (
                    self.factura['FacturaExpedida']['TipoDesglose']
                    ['DesgloseFactura']['Sujeta']['NoExenta']['DesgloseIVA']
                    ['DetalleIVA']
                )

            with it('la BaseImponible debe ser la original'):
                expect(self.detalle_iva[0]['BaseImponible']).to(equal(
                    self.invoice.tax_line[0].base)
                )
            with it('la CuotaRepercutida debe ser la original'):
                expect(self.detalle_iva[0]['CuotaRepercutida']).to(equal(
                    self.invoice.tax_line[0].tax_amount)
                )
            with it('el TipoImpositivo debe ser la original'):
                expect(self.detalle_iva[0]['TipoImpositivo']).to(equal(
                    self.invoice.tax_line[0].tax_id.amount * 100)
                )

    with description('en la factura'):
        with before.all:
            self.factura = (
                self.obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
