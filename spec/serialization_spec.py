# coding=utf-8

from sii.resource import SII
from sii.models.invoices_record import CRE_FACTURAS_EMITIDAS
from expects import *
from spec.testing_data import DataGenerator
import os

with description('El XML Generado'):
    with before.all:
        self.data_gen = DataGenerator()

    with description('en la cabecera'):
        with before.all:
            # Example invoice to check common fields
            self.invoice = self.data_gen.get_out_invoice()
            self.invoice_obj = SII(self.invoice).generate_object()
            self.cabecera = (
                self.invoice_obj['SuministroLRFacturasEmitidas']['Cabecera']
            )

        with it('la versión es la "0.7"'):
            expect(self.cabecera['IDVersionSii']).to(equal('0.7'))

        with context('cuando es de tipo alta'):
            with it('el tipo de comunicación debe ser "A0"'):
                expect(self.cabecera['TipoComunicacion']).to(equal('A0'))

        with context('cuando es de tipo modificación'):
            with before.all:
                new_data_gen = DataGenerator(invoice_registered=True)
                invoice = new_data_gen.get_out_invoice()
                invoice_obj = SII(invoice).generate_object()
                self.cabecera = (
                    invoice_obj['SuministroLRFacturasEmitidas']['Cabecera']
                )

            with it('el tipo de comunicación debe ser "A1"'):
                expect(self.cabecera['TipoComunicacion']).to(equal('A1'))

        with context('en el titular'):
            with it('el nif deben ser los del titular'):
                expect(
                    self.cabecera['Titular']['NIF']
                ).to(equal(self.invoice.company_id.partner_id.vat))

            with it('el nombre y apellidos deben ser los del titular'):
                expect(
                    self.cabecera['Titular']['NombreRazon']
                ).to(equal(self.invoice.company_id.partner_id.name))

    with description('en los datos comunes de una factura'):
        with before.all:
            # Example invoice to check common fields
            self.invoice = self.data_gen.get_out_invoice()
            self.invoice_obj = SII(self.invoice).generate_object()
            self.factura = (
                self.invoice_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )

        with context('en los NIFs involucrados'):
            with before.all:
                os.environ['NIF_TITULAR'] = 'ES12345678T'
                os.environ['NIF_CONTRAPARTE'] = 'esES654321P'

                new_data_gen = DataGenerator()
                nifs_test_invoice = new_data_gen.get_out_invoice()
                self.nif_contraparte = nifs_test_invoice.partner_id.vat[2:]
                self.nif_titular = (
                    nifs_test_invoice.company_id.partner_id.vat[2:]
                )

                self.nifs_test_obj = SII(nifs_test_invoice).generate_object()

            with it('el NIF del Titular no debe empezar por "ES"'):
                expect(
                    self.nifs_test_obj['SuministroLRFacturasEmitidas']
                    ['Cabecera']['Titular']['NIF']
                ).to(equal(self.nif_titular))

            with it('el NIF de la Contraparte no debe empezar por "ES"'):
                expect(
                    self.nifs_test_obj['SuministroLRFacturasEmitidas']
                    ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                    ['Contraparte']['NIF']
                ).to(equal(self.nif_contraparte))

        with it('la ClaveRegimenEspecialOTrascendencia debe ser válido'):
            expect(
                dict(CRE_FACTURAS_EMITIDAS).keys()
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

    with description('en los datos de una factura emitida'):
        with before.all:
            self.out_invoice = self.data_gen.get_out_invoice()
            self.invoice_obj = SII(self.invoice).generate_object()
            self.out_invoice_obj = SII(self.out_invoice).generate_object()
            self.factura_emitida = (
                self.out_invoice_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )

        with context('en una contraparte con NIF no registrado en la AEAT'):
            with before.all:
                new_data_gen = DataGenerator(contraparte_registered=False)
                self.out_invoice = new_data_gen.get_out_invoice()
                self.nif_contraparte = self.out_invoice.partner_id.vat[2:]

                out_invoice_obj = SII(self.out_invoice).generate_object()
                self.contraparte = (
                    out_invoice_obj['SuministroLRFacturasEmitidas']
                    ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                    ['Contraparte']
                )

            with it('el ID debe ser el NIF de la contraparte'):
                expect(
                    self.contraparte['IDOtro']['ID']
                ).to(equal(self.nif_contraparte))

            with it('el IDType debe ser "07"'):
                expect(self.contraparte['IDOtro']['IDType']).to(equal('07'))

            with it('el CodigoPais debe ser "ES"'):
                expect(self.contraparte['IDOtro']['CodigoPais']).to(equal('ES'))

        with context('en los detalles del IVA'):
            with before.all:
                self.detalle_iva = (
                    self.factura_emitida['FacturaExpedida']['TipoDesglose']
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

        with context('si es una exportación'):
            with before.all:
                # Clave Régimen Especial exportación: '02'
                self.cre_exportacion = '02'
                self.out_invoice.sii_out_clave_regimen_especial = (
                    self.cre_exportacion
                )
                self.export_inv_obj = SII(self.out_invoice).generate_object()
                self.factura_emitida = (
                    self.export_inv_obj['SuministroLRFacturasEmitidas']
                    ['RegistroLRFacturasEmitidas']
                )

            with context('en los detalles del IVA'):
                with before.all:
                    self.detalle_iva = (
                        self.factura_emitida['FacturaExpedida']['TipoDesglose']
                        ['DesgloseTipoOperacion']['Entrega']['Sujeta']
                        ['NoExenta']['DesgloseIVA']['DetalleIVA']
                    )

                with it('la BaseImponible debe ser la original'):
                    expect(self.detalle_iva[0]['BaseImponible']).to(equal(
                        self.out_invoice.tax_line[0].base)
                    )
                with it('la CuotaRepercutida debe ser la original'):
                    expect(self.detalle_iva[0]['CuotaRepercutida']).to(equal(
                        self.out_invoice.tax_line[0].tax_amount)
                    )
                with it('el TipoImpositivo debe ser la original'):
                    expect(self.detalle_iva[0]['TipoImpositivo']).to(equal(
                        self.out_invoice.tax_line[0].tax_id.amount * 100)
                    )

    with description('en los datos de una factura recibida'):
        with before.all:
            self.in_invoice = self.data_gen.get_in_invoice()
            self.in_invoice_obj = SII(self.in_invoice).generate_object()
            self.factura_recibida = (
                self.in_invoice_obj['SuministroLRFacturasRecibidas']
                ['RegistroLRFacturasRecibidas']
            )

        with context('en los detalles del IVA'):
            with it('el detalle de DesgloseIVA debe ser la original'):
                detalle_iva_desglose_iva = (
                    self.factura_recibida['FacturaRecibida']['DesgloseFactura']
                    ['DesgloseIVA']['DetalleIVA']
                )
                expect(
                    detalle_iva_desglose_iva[0]['BaseImponible']
                ).to(equal(
                    self.in_invoice.tax_line[0].base)
                )
                expect(
                    detalle_iva_desglose_iva[0]['CuotaSoportada']
                ).to(equal(
                    self.in_invoice.tax_line[0].tax_amount)
                )
                expect(
                    detalle_iva_desglose_iva[0]['TipoImpositivo']
                ).to(equal(
                    self.in_invoice.tax_line[0].tax_id.amount * 100)
                )

    with description('en los datos de una factura rectificativa emitida'):
        with before.all:
            self.out_refund = self.data_gen.get_out_refund_invoice()
            self.out_refund_obj = SII(self.out_refund).generate_object()
            self.fact_rect_emit = (
                self.out_refund_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )

        with context('en los datos de rectificación'):
            with it('el TipoRectificativa debe ser por sustitución (S)'):
                expect(
                    self.fact_rect_emit['FacturaExpedida']['TipoRectificativa']
                ).to(equal('S'))

            with before.all:
                self.importe_rectificacion = (
                    self.fact_rect_emit['FacturaExpedida']
                    ['ImporteRectificacion']
                )

            with it('la BaseRectificada debe ser 0'):
                expect(
                    self.importe_rectificacion['BaseRectificada']
                ).to(equal(0))

            with it('la CuotaRectificada debe ser 0'):
                expect(
                    self.importe_rectificacion['CuotaRectificada']
                ).to(equal(0))

        with context('en los detalles del IVA'):
            with before.all:
                self.detalle_iva = (
                    self.fact_rect_emit['FacturaExpedida']['TipoDesglose']
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

    with description('en los datos de una factura rectificativa recibida'):
        with before.all:
            self.in_refund = self.data_gen.get_in_refund_invoice()
            self.in_refund_obj = SII(self.in_refund).generate_object()
            self.fact_rect_recib = (
                self.in_refund_obj['SuministroLRFacturasRecibidas']
                ['RegistroLRFacturasRecibidas']
            )

        with context('en los datos de rectificación'):
            with it('el TipoRectificativa debe ser por sustitución (S)'):
                expect(
                    self.fact_rect_recib['FacturaRecibida']['TipoRectificativa']
                ).to(equal('S'))

            with before.all:
                self.importe_rectificacion = (
                    self.fact_rect_recib['FacturaRecibida']
                    ['ImporteRectificacion']
                )

            with it('la BaseRectificada debe ser 0'):
                expect(
                    self.importe_rectificacion['BaseRectificada']
                ).to(equal(0))

            with it('la CuotaRectificada debe ser 0'):
                expect(
                    self.importe_rectificacion['CuotaRectificada']
                ).to(equal(0))

        with context('en los detalles del IVA'):
            with before.all:
                self.detalle_iva = (
                    self.fact_rect_recib['FacturaRecibida']['DesgloseFactura']
                    ['DesgloseIVA']['DetalleIVA']
                )

            with it('la BaseImponible debe ser la original'):
                expect(self.detalle_iva[0]['BaseImponible']).to(equal(
                    self.invoice.tax_line[0].base)
                )
            with it('la CuotaRepercutida debe ser la original'):
                expect(self.detalle_iva[0]['CuotaSoportada']).to(equal(
                    self.invoice.tax_line[0].tax_amount)
                )
            with it('el TipoImpositivo debe ser la original'):
                expect(self.detalle_iva[0]['TipoImpositivo']).to(equal(
                    self.invoice.tax_line[0].tax_id.amount * 100)
                )
