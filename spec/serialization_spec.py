# coding=utf-8

from sii.resource import SII, SIIDeregister
from sii.models.invoices_record import CRE_FACTURAS_EMITIDAS
from sii.utils import unidecode_str, VAT
from expects import *
from datetime import datetime
from spec.testing_data import DataGenerator, Tax, InvoiceLine, InvoiceTax
from mamba import *
import os


def group_by_tax_rate(iva_values):
    aux_iva_values = {}

    for iva in iva_values:
        tipo_impositivo = iva['TipoImpositivo']
        base_imponible = iva['BaseImponible']
        cuota_key = (
            'CuotaSoportada'
            if 'CuotaSoportada' in iva.keys()
            else 'CuotaRepercutida'
        )
        cuota = iva[cuota_key]
        if tipo_impositivo in aux_iva_values:
            aux = aux_iva_values[tipo_impositivo]
            aux['BaseImponible'] += base_imponible
            aux[cuota_key] += cuota
        else:
            aux_iva_values[tipo_impositivo] = iva.copy()

    return aux_iva_values


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

        with it('la versión es la "1.0"'):
            expect(self.cabecera['IDVersionSii']).to(equal('1.0'))

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
                ).to(equal(
                    VAT.clean_vat(self.invoice.company_id.partner_id.vat)
                ))

            with it('el nombre y apellidos deben ser los del titular'):
                expect(
                    self.cabecera['Titular']['NombreRazon']
                ).to(equal(
                    unidecode_str(self.invoice.company_id.partner_id.name))
                )

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

        with it('la descripción de la operación debe ser el de la factura'):
            expect(
                self.factura['FacturaExpedida']['DescripcionOperacion']
            ).to(equal(self.invoice.sii_description))

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
                detalle_iva = (
                    self.factura_emitida['FacturaExpedida']['TipoDesglose']
                    ['DesgloseFactura']['Sujeta']['NoExenta']['DesgloseIVA']
                    ['DetalleIVA']
                )
                self.grouped_detalle_iva = group_by_tax_rate(detalle_iva)

            with it('la BaseImponible debe ser la original'):
                expect(
                    self.grouped_detalle_iva[21.0]['BaseImponible']
                ).to(equal(
                    self.out_invoice.tax_line[0].base
                ))
            with it('la CuotaRepercutida debe ser la original'):
                expect(
                    self.grouped_detalle_iva[21.0]['CuotaRepercutida']
                ).to(equal(
                    self.out_invoice.tax_line[0].tax_amount
                ))
            with it('el TipoImpositivo debe ser la original'):
                expect(
                    self.grouped_detalle_iva[21.0]['TipoImpositivo']
                ).to(equal(
                    self.out_invoice.tax_line[0].tax_id.amount * 100
                ))

        with context('en los detalles del IVA inversion sujeto pasivo'):
            with before.all:
                name_iva_isp = 'IVA 21% Inv. Sujeto pasivo'
                tax_iva_isp = Tax(name=name_iva_isp, amount=0, type='percent')
                self.out_invoice.invoice_line.append(InvoiceLine(
                    price_subtotal=3200, invoice_line_tax_id=[tax_iva_isp]
                ))
                base_iva_isp = sum(
                    [line.price_subtotal
                     for line in self.out_invoice.invoice_line
                     if tax_iva_isp in line.invoice_line_tax_id]
                )
                invoice_tax_isp = InvoiceTax(
                    name=name_iva_isp, base=base_iva_isp,
                    tax_amount=base_iva_isp * tax_iva_isp.amount,
                    tax_id=tax_iva_isp
                )
                self.out_invoice.tax_line.append(invoice_tax_isp)
                self.out_invoice_obj = SII(self.out_invoice).generate_object()
                self.factura_emitida = (
                    self.out_invoice_obj['SuministroLRFacturasEmitidas']
                    ['RegistroLRFacturasEmitidas']
                )

                detalle_iva_isp = (
                    self.factura_emitida['FacturaExpedida']['TipoDesglose']
                    ['DesgloseTipoOperacion']['Entrega']['Sujeta']['NoExenta']
                    ['DesgloseIVA']['DetalleIVA']
                )
                self.grouped_detalle_iva_isp = group_by_tax_rate(
                    detalle_iva_isp
                )

            with it('la BaseImponible debe ser la original'):
                expect(
                    self.grouped_detalle_iva_isp[0.0]['BaseImponible']
                ).to(equal(
                    self.out_invoice.tax_line[4].base
                ))
            with it('la CuotaRepercutida debe ser la original'):
                expect(
                    self.grouped_detalle_iva_isp[0.0]['CuotaRepercutida']
                ).to(equal(
                    self.out_invoice.tax_line[4].tax_amount
                ))
            with it('el TipoImpositivo debe ser la original'):
                expect(
                    self.grouped_detalle_iva_isp[0.0]['TipoImpositivo']
                ).to(equal(
                    self.out_invoice.tax_line[4].tax_id.amount * 100
                ))

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
                    detalle_iva = (
                        self.factura_emitida['FacturaExpedida']['TipoDesglose']
                        ['DesgloseTipoOperacion']['Entrega']['Sujeta']
                        ['NoExenta']['DesgloseIVA']['DetalleIVA']
                    )
                    self.grouped_detalle_iva = group_by_tax_rate(detalle_iva)

                with it('la BaseImponible debe ser la original'):
                    expect(
                        self.grouped_detalle_iva[21.0]['BaseImponible']
                    ).to(equal(
                        self.out_invoice.tax_line[0].base
                    ))
                with it('la CuotaRepercutida debe ser la original'):
                    expect(
                        self.grouped_detalle_iva[21.0]['CuotaRepercutida']
                    ).to(equal(
                        self.out_invoice.tax_line[0].tax_amount
                    ))
                with it('el TipoImpositivo debe ser la original'):
                    expect(
                        self.grouped_detalle_iva[21.0]['TipoImpositivo']
                    ).to(equal(
                        self.out_invoice.tax_line[0].tax_id.amount * 100
                    ))

        with context('si es una operación de alquiler (CRE "12" o "13")'):
            with before.all:
                new_data_gen = DataGenerator()
                self.out_invoice = new_data_gen.get_out_invoice()
                self.out_invoice.sii_out_clave_regimen_especial = '12'
                provincia = (
                    self.out_invoice.address_contact_id.state_id
                )
                self.comunidad_autonoma = provincia.comunitat_autonoma

            with context('si el inmueble pertenece a España'):

                with it('si tiene referencia catastral'):
                    ref_catastral = '9872023 VH5797S 0001 WX'
                    self.out_invoice.address_contact_id.ref_catastral = \
                        ref_catastral
                    out_invoice_obj = SII(self.out_invoice).generate_object()
                    factura_expedida = (
                        out_invoice_obj['SuministroLRFacturasEmitidas']
                        ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                    )
                    detalle_inmueble = (
                        factura_expedida['DatosInmueble']['DetalleInmueble']
                    )

                    expect(
                        dict(CRE_FACTURAS_EMITIDAS).keys()
                    ).to(contain(
                        (factura_expedida[
                             'ClaveRegimenEspecialOTrascendencia'
                         ])
                    ))

                    expect(detalle_inmueble['ReferenciaCatastral']).to(equal(
                        ref_catastral
                    ))

                with context('si no tiene referencia catastral'):
                    with it('no debe tener referencia catastral'):
                        ref_catastral = '9872023 VH5797S 0001 WX'
                        self.out_invoice.address_contact_id.ref_catastral = \
                            False
                        out_invoice_obj = \
                            SII(self.out_invoice).generate_object()
                        factura_expedida = (
                            out_invoice_obj['SuministroLRFacturasEmitidas']
                            ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                        )
                        detalle_inmueble = (
                            factura_expedida['DatosInmueble']['DetalleInmueble']
                        )

                        expect(
                            dict(CRE_FACTURAS_EMITIDAS).keys()
                        ).to(contain(
                            (factura_expedida[
                                 'ClaveRegimenEspecialOTrascendencia'
                             ])
                        ))

                        expect(detalle_inmueble.keys()).not_to(
                            contain('ReferenciaCatastral')
                        )

                with it('si no es de Navarra ni País Basco la situación '
                        'inmueble debe ser "1"'):
                    self.comunidad_autonoma.codi = '01'
                    out_invoice_obj = SII(self.out_invoice).generate_object()
                    detalle_inmueble = (
                        out_invoice_obj['SuministroLRFacturasEmitidas']
                        ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                        ['DatosInmueble']['DetalleInmueble']
                    )

                    expect(detalle_inmueble['SituacionInmueble']).to(equal('1'))

                with it('si es de Navarra la situación inmueble debe ser "2"'):
                    self.comunidad_autonoma.codi = '15'
                    out_invoice_obj = SII(self.out_invoice).generate_object()
                    detalle_inmueble = (
                        out_invoice_obj['SuministroLRFacturasEmitidas']
                        ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                        ['DatosInmueble']['DetalleInmueble']
                    )

                    expect(detalle_inmueble['SituacionInmueble']).to(equal('2'))

                with it('si es de País Basco la situación inmueble '
                        'debe ser "2"'):
                    self.comunidad_autonoma.codi = '16'
                    out_invoice_obj = SII(self.out_invoice).generate_object()
                    detalle_inmueble = (
                        out_invoice_obj['SuministroLRFacturasEmitidas']
                        ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                        ['DatosInmueble']['DetalleInmueble']
                    )

                    expect(detalle_inmueble['SituacionInmueble']).to(equal('2'))

            with context('si el inmueble no pertenece a España'):

                with it('la situación inmueble debe ser "4"'):
                    self.comunidad_autonoma.codi = '20'
                    out_invoice_obj = SII(self.out_invoice).generate_object()
                    detalle_inmueble = (
                        out_invoice_obj['SuministroLRFacturasEmitidas']
                        ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                        ['DatosInmueble']['DetalleInmueble']
                    )

                    expect(detalle_inmueble['SituacionInmueble']).to(equal('4'))

    with description('en los datos de una factura recibida'):
        with before.all:
            self.in_invoice = self.data_gen.get_in_invoice()
            self.in_invoice_obj = SII(self.in_invoice).generate_object()
            self.factura_recibida = (
                self.in_invoice_obj['SuministroLRFacturasRecibidas']
                ['RegistroLRFacturasRecibidas']
            )

        with context('en los datos del emisor de la factura'):

            with context('si no está registrado en la AEAT'):
                with before.all:
                    new_data_gen = DataGenerator(contraparte_registered=False)
                    self.in_invoice = new_data_gen.get_in_invoice()
                    # Valid French TVA FR23334175221
                    self.in_invoice.partner_id.country_id.code = 'FR'
                    self.in_invoice.partner_id.vat = 'FR23334175221'

                    in_invoice_obj = SII(self.in_invoice).generate_object()
                    self.emisor_factura = (
                        in_invoice_obj['SuministroLRFacturasRecibidas']
                        ['RegistroLRFacturasRecibidas']['IDFactura']
                        ['IDEmisorFactura']
                    )

                with it('el ID debe ser el NIF del emisor'):
                    nif_emisor = self.in_invoice.partner_id.vat[2:]
                    expect(
                        self.emisor_factura['IDOtro']['ID']
                    ).to(equal(nif_emisor))

                with it('el IDType debe ser "04"'):
                    expect(
                        self.emisor_factura['IDOtro']['IDType']
                    ).to(equal('04'))

                with it('el CodigoPais debe ser "FR"'):
                    expect(
                        self.emisor_factura['IDOtro']['CodigoPais']
                    ).to(equal('FR'))

        with context('en los detalles del IVA'):
            with before.all:
                detalle_iva_desglose_iva = (
                    self.factura_recibida['FacturaRecibida']['DesgloseFactura']
                    ['DesgloseIVA']['DetalleIVA']
                )
                self.grouped_detalle_iva = group_by_tax_rate(
                    detalle_iva_desglose_iva
                )

            with it('el detalle de DesgloseIVA debe ser la original'):
                expect(
                    self.grouped_detalle_iva[21.0]['BaseImponible']
                ).to(equal(
                    self.in_invoice.tax_line[0].base
                ))
                expect(
                    self.grouped_detalle_iva[21.0]['CuotaSoportada']
                ).to(equal(
                    self.in_invoice.tax_line[0].tax_amount
                ))
                expect(
                    self.grouped_detalle_iva[21.0]['TipoImpositivo']
                ).to(equal(
                    self.in_invoice.tax_line[0].tax_id.amount * 100
                ))

            with _it('el detalle de DesgloseIVA para importe no sujeto a '
                     'impuesto debe ser correcto'):
                expect(
                    self.grouped_detalle_iva[0.0]['BaseImponible']
                ).to(equal(
                    self.in_invoice.invoice_line[5].price_subtotal
                ))
                expect(
                    self.grouped_detalle_iva[0.0]['CuotaSoportada']
                ).to(equal(0))
                expect(
                    self.grouped_detalle_iva[0.0]['TipoImpositivo']
                ).to(equal(0))

        with context('si es una importación'):
            with before.all:
                # Clave Régimen Especial importación: '13'
                self.cre_importacion = '13'
                self.in_invoice.sii_in_clave_regimen_especial = (
                    self.cre_importacion
                )

                self.import_inv_obj = SII(self.in_invoice).generate_object()
                self.factura_recibida = (
                    self.import_inv_obj['SuministroLRFacturasRecibidas']
                    ['RegistroLRFacturasRecibidas']
                )

            with context('en los detalles del IVA'):
                with it('el detalle de DesgloseIVA debe ser la original'):
                    # TODO change TipoImpositivo and CuotaSoportada should be '0'
                    detalle_iva_desglose_iva = (
                        self.factura_recibida['FacturaRecibida']
                        ['DesgloseFactura']['DesgloseIVA']['DetalleIVA']
                    )
                    self.grouped_detalle_iva = group_by_tax_rate(
                        detalle_iva_desglose_iva
                    )

                    expect(
                        self.grouped_detalle_iva[21.0]['BaseImponible']
                    ).to(equal(
                        self.in_invoice.tax_line[0].base
                    ))
                    expect(
                        self.grouped_detalle_iva[21.0]['CuotaSoportada']
                    ).to(equal(
                        self.in_invoice.tax_line[0].tax_amount
                    ))
                    expect(
                        self.grouped_detalle_iva[21.0]['TipoImpositivo']
                    ).to(equal(
                        self.in_invoice.tax_line[0].tax_id.amount * 100
                    ))

        with context('si es una factura del primer semestre 2017'):
            with before.all:
                # Clave Régimen Especial para
                # Facturas Recibidas Primer Semestre 2017: '14'
                self.cre_primer_semestre = '14'
                self.in_invoice.sii_in_clave_regimen_especial = (
                    self.cre_primer_semestre
                )

                self.first_semester_in_inv_obj = (
                    SII(self.in_invoice).generate_object()
                )
                self.factura_recibida = (
                    self.first_semester_in_inv_obj
                    ['SuministroLRFacturasRecibidas']
                    ['RegistroLRFacturasRecibidas']
                )

            with it('debe tener Clave de Régimen Especial "14"'):
                expect(
                    self.factura_recibida['FacturaRecibida']
                    ['ClaveRegimenEspecialOTrascendencia']
                ).to(equal(self.cre_primer_semestre))

            with it('la cuota deducible debe ser 0'):
                expect(
                    self.factura_recibida['FacturaRecibida']['CuotaDeducible']
                ).to(equal(0))

            with it('la fecha de registro contable debe ser la fecha del '
                    'envío'):
                expect(
                    self.factura_recibida['FacturaRecibida']
                    ['FechaRegContable']
                ).to(equal(datetime.today().strftime('%d-%m-%Y')))

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
                detalle_iva = (
                    self.fact_rect_emit['FacturaExpedida']['TipoDesglose']
                    ['DesgloseFactura']['Sujeta']['NoExenta']['DesgloseIVA']
                    ['DetalleIVA']
                )
                self.grouped_detalle_iva = group_by_tax_rate(detalle_iva)

            with it('la BaseImponible debe ser la original'):
                expect(
                    self.grouped_detalle_iva[21.0]['BaseImponible']
                ).to(equal(
                    -1 * abs(self.out_refund.tax_line[0].base)
                ))
            with it('la CuotaRepercutida debe ser la original'):
                expect(
                    self.grouped_detalle_iva[21.0]['CuotaRepercutida']
                ).to(equal(
                    -1 * abs(self.out_refund.tax_line[0].tax_amount)
                ))
            with it('el TipoImpositivo debe ser la original'):
                expect(
                    self.grouped_detalle_iva[21.0]['TipoImpositivo']
                ).to(equal(
                    self.out_refund.tax_line[0].tax_id.amount * 100
                ))

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
                detalle_iva = (
                    self.fact_rect_recib['FacturaRecibida']['DesgloseFactura']
                    ['DesgloseIVA']['DetalleIVA']
                )
                self.grouped_detalle_iva = group_by_tax_rate(detalle_iva)

            with it('la BaseImponible debe ser la original'):
                expect(
                    self.grouped_detalle_iva[21.0]['BaseImponible']
                ).to(equal(
                    -1 * abs(self.in_refund.tax_line[0].base)
                ))
            with it('la CuotaRepercutida debe ser la original'):
                expect(
                    self.grouped_detalle_iva[21.0]['CuotaSoportada']
                ).to(equal(
                    -1 * abs(self.in_refund.tax_line[0].tax_amount)
                ))
            with it('el TipoImpositivo debe ser la original'):
                expect(
                    self.grouped_detalle_iva[21.0]['TipoImpositivo']
                ).to(equal(
                    self.in_refund.tax_line[0].tax_id.amount * 100
                ))

    with description('en los datos de una factura emitida rectificativa '
                     'sin anuladora RA'):
        with before.all:
            self.out_invoice_RA = self.data_gen.get_out_invoice_RA()
            self.out_invoice_RA.rectifying_id.sii_registered = True
            self.out_invoice_RA_obj = SII(self.out_invoice_RA).generate_object()
            self.fact_RA_emitida = (
                self.out_invoice_RA_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )

        with context('en los datos de rectificación'):
            with it('el TipoRectificativa debe ser por sustitución (S)'):
                expect(
                    self.fact_RA_emitida['FacturaExpedida']['TipoRectificativa']
                ).to(equal('S'))

            with it('debe contener las FacturasRectificadas'):
                expect(
                    self.fact_RA_emitida['FacturaExpedida']
                    ['FacturasRectificadas']['IDFacturaRectificada'][0]
                    ['NumSerieFacturaEmisor']
                ).to(equal(
                    self.out_invoice_RA.rectifying_id.number
                ))

                fecha_expedicion = (
                    self.fact_RA_emitida['FacturaExpedida']
                    ['FacturasRectificadas']['IDFacturaRectificada'][0]
                    ['FechaExpedicionFacturaEmisor']
                )
                expect(
                    datetime.strptime(
                        fecha_expedicion, '%d-%m-%Y'
                    ).strftime('%Y-%m-%d')
                ).to(equal(
                    self.out_invoice_RA.rectifying_id.date_invoice
                ))

            with it('debe contener el ImporteRectificacion'):
                expect(
                    self.fact_RA_emitida['FacturaExpedida']
                    ['ImporteRectificacion']['BaseRectificada']
                ).to(equal(
                    self.out_invoice_RA.rectifying_id.amount_untaxed
                ))

                expect(
                    self.fact_RA_emitida['FacturaExpedida']
                    ['ImporteRectificacion']['CuotaRectificada']
                ).to(equal(
                    self.out_invoice_RA.rectifying_id.amount_tax
                ))

with description('El XML Generado en una baja de una factura emitida'):
    with before.all:
        self.data_gen = DataGenerator()

    with description('en la cabecera'):
        with before.all:
            self.invoice = self.data_gen.get_out_invoice()
            self.invoice_obj = (
                SIIDeregister(self.invoice).generate_deregister_object()
            )
            self.cabecera = (
                self.invoice_obj['BajaLRFacturasEmitidas']['Cabecera']
            )

        with it('la versión es la "1.0"'):
            expect(self.cabecera['IDVersionSii']).to(equal('1.0'))

        with it('no debe contener el campo "TipoComunicacion"'):
            expect(self.cabecera).not_to(have_key('TipoComunicacion'))

        with context('en el titular'):
            with it('el nif deben ser los del titular'):
                expect(
                    self.cabecera['Titular']['NIF']
                ).to(equal(
                    VAT.clean_vat(self.invoice.company_id.partner_id.vat)
                ))

            with it('el nombre y apellidos deben ser los del titular'):
                expect(
                    self.cabecera['Titular']['NombreRazon']
                ).to(equal(
                    unidecode_str(self.invoice.company_id.partner_id.name))
                )

    with description('en la baja de una factura'):
        with before.all:
            self.invoice = self.data_gen.get_out_invoice()
            self.invoice_obj = (
                SIIDeregister(self.invoice).generate_deregister_object()
            )
            self.factura_emitida = (
                self.invoice_obj['BajaLRFacturasEmitidas']
                ['RegistroLRBajaExpedidas']
            )

        with context('en los datos del período'):
            with before.all:
                self.periodo = self.factura_emitida['PeriodoImpositivo']

            with it('el ejercicio es el correspondiente al año de la factura'):
                expect(
                    self.periodo['Ejercicio']
                ).to(equal(self.invoice.period_id.name[3:7]))

            with it('el período es el correspondiente al mes de la factura'):
                expect(
                    self.periodo['Periodo']
                ).to(equal(self.invoice.period_id.name[0:2]))

        with context('en los datos de la factura'):
            with before.all:
                self.factura = self.factura_emitida['IDFactura']

            with it('el NIF del emisor de la factura es correcto'):
                expect(
                    self.factura['IDEmisorFactura']['NIF']
                ).to(equal(
                    VAT.clean_vat(self.invoice.company_id.partner_id.vat)
                ))

            with it('el número de factura es correcto'):
                expect(
                    self.factura['NumSerieFacturaEmisor']
                ).to(equal(
                    self.invoice.number
                ))

            with it('la fecha de factura es correcto'):
                expect(
                    datetime.strptime(
                        self.factura['FechaExpedicionFacturaEmisor'], '%d-%m-%Y'
                    ).strftime('%Y-%m-%d')
                ).to(equal(
                    self.invoice.date_invoice
                ))

with description('El XML Generado en una baja de una factura recibida'):
    with before.all:
        self.data_gen = DataGenerator()

    with description('en la cabecera'):
        with before.all:
            self.invoice = self.data_gen.get_in_invoice()
            self.invoice_obj = (
                SIIDeregister(self.invoice).generate_deregister_object()
            )
            self.cabecera = (
                self.invoice_obj['BajaLRFacturasRecibidas']['Cabecera']
            )

        with it('la versión es la "1.0"'):
            expect(self.cabecera['IDVersionSii']).to(equal('1.0'))

        with it('no debe contener el campo "TipoComunicacion"'):
            expect(self.cabecera).not_to(have_key('TipoComunicacion'))

        with context('en el titular'):
            with it('el nif deben ser los del titular'):
                expect(
                    self.cabecera['Titular']['NIF']
                ).to(equal(
                    VAT.clean_vat(self.invoice.company_id.partner_id.vat)
                ))

            with it('el nombre y apellidos deben ser los del titular'):
                expect(
                    self.cabecera['Titular']['NombreRazon']
                ).to(equal(
                    unidecode_str(self.invoice.company_id.partner_id.name))
                )

    with description('en la baja de una factura'):
        with before.all:
            self.invoice = self.data_gen.get_in_invoice()
            self.invoice_obj = (
                SIIDeregister(self.invoice).generate_deregister_object()
            )
            self.factura_recibida = (
                self.invoice_obj['BajaLRFacturasRecibidas']
                ['RegistroLRBajaRecibidas']
            )

        with context('en los datos del período'):
            with before.all:
                self.periodo = self.factura_recibida['PeriodoImpositivo']

            with it('el ejercicio es el correspondiente al año de la factura'):
                expect(
                    self.periodo['Ejercicio']
                ).to(equal(self.invoice.period_id.name[3:7]))

            with it('el período es el correspondiente al mes de la factura'):
                expect(
                    self.periodo['Periodo']
                ).to(equal(self.invoice.period_id.name[0:2]))

        with context('en los datos de la factura'):
            with before.all:
                self.factura = self.factura_recibida['IDFactura']

            with it('el nombre del emisor de la factura es correcto'):
                expect(
                    self.factura['IDEmisorFactura']['NombreRazon']
                ).to(equal(
                    unidecode_str(self.invoice.partner_id.name)
                ))

            with it('el NIF del emisor de la factura es correcto'):
                expect(
                    self.factura['IDEmisorFactura']['NIF']
                ).to(equal(
                    VAT.clean_vat(self.invoice.partner_id.vat)
                ))

            with it('el número de factura es correcto'):
                expect(
                    self.factura['NumSerieFacturaEmisor']
                ).to(equal(
                    self.invoice.origin
                ))

            with it('la fecha de factura es correcto'):
                expect(
                    datetime.strptime(
                        self.factura['FechaExpedicionFacturaEmisor'], '%d-%m-%Y'
                    ).strftime('%Y-%m-%d')
                ).to(equal(
                    self.invoice.origin_date_invoice
                ))
