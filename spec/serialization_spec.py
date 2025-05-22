# coding=utf-8

from sii.resource import SII, SIIDeregister, get_iva_values
from sii.models.invoices_record import CRE_FACTURAS_EMITIDAS
from sii.utils import unidecode_str, VAT
from expects import *
from datetime import datetime
from decimal import Decimal
from spec.testing_data import DataGenerator, Tax, InvoiceLine, InvoiceTax
from mamba import *
import os


def group_by_tax_rate(iva_values, in_invoice):
    aux_iva_values = {}

    if in_invoice:
        cuota_key = 'CuotaSoportada'
    else:
        cuota_key = 'CuotaRepercutida'

    for iva in iva_values:
        tipo_impositivo = iva.get('TipoImpositivo', 0.0)
        base_imponible = iva['BaseImponible']
        cuota = iva.get(cuota_key, 0.0)
        if tipo_impositivo in aux_iva_values:
            aux = aux_iva_values[tipo_impositivo]
            aux['BaseImponible'] += base_imponible
            if aux.get(cuota_key, False):
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

        with it('la versión es la "1.1"'):
            expect(self.cabecera['IDVersionSii']).to(equal('1.1'))

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

        with context('en los NIFs involucrados sin fiscal info'):
            with before.all:
                os.environ['NIF_TITULAR'] = 'ES12345678T'
                os.environ['NIF_CONTRAPARTE'] = 'ES18745529T'
                os.environ['FISCAL_VAT_CONTRAPARTE'] = 'ES18745529T'

                new_data_gen = DataGenerator()
                nifs_test_invoice = new_data_gen.get_out_invoice(with_fiscal_info=False)
                self.nif_contraparte = nifs_test_invoice.partner_id.vat[2:]
                self.nombre_contraparte = unidecode_str(nifs_test_invoice.partner_id.name)
                self.nombre_partner = unidecode_str(nifs_test_invoice.partner_id.name)
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
            with it('el Nombre de la Contraparte debe ser igual al valor partner'):
                expect(
                    self.nifs_test_obj['SuministroLRFacturasEmitidas']
                    ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                    ['Contraparte']['NombreRazon']
                ).to(equal(self.nombre_partner))
            with it('el Nombre de la Contraparte debe ser igual al del partner'):
                expect(
                    self.nifs_test_obj['SuministroLRFacturasEmitidas']
                    ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                    ['Contraparte']['NombreRazon']
                ).to(equal(self.nombre_partner))

        with context('en los NIFs involucrados con fiscal info'):
            with before.all:
                os.environ['NIF_TITULAR'] = 'ES12345678T'
                os.environ['NIF_CONTRAPARTE'] = 'ES18745529T'
                os.environ['FISCAL_VAT_CONTRAPARTE'] = 'ES18745529T'

                new_data_gen = DataGenerator()
                nifs_test_invoice = new_data_gen.get_out_invoice()
                self.nif_contraparte = nifs_test_invoice.fiscal_vat[2:]
                self.nif_titular = (
                    nifs_test_invoice.company_id.partner_id.vat[2:]
                )
                self.nombre_contraparte = nifs_test_invoice.fiscal_name
                self.nombre_partner = nifs_test_invoice.partner_id.name

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
            with it('el Nombre de la Contraparte debe ser igual al valor fiscal'):
                expect(
                    self.nifs_test_obj['SuministroLRFacturasEmitidas']
                    ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                    ['Contraparte']['NombreRazon']
                ).to(equal(self.nombre_contraparte))
            with it('el Nombre de la Contraparte debe ser distinto al del partner'):
                expect(
                    self.nifs_test_obj['SuministroLRFacturasEmitidas']
                    ['RegistroLRFacturasEmitidas']['FacturaExpedida']
                    ['Contraparte']['NombreRazon']
                ).not_to(equal(self.nombre_partner))

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
                self.periodo = self.factura['PeriodoLiquidacion']

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
                self.grouped_detalle_iva = group_by_tax_rate(
                    detalle_iva, in_invoice=False
                )

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
                    detalle_iva_isp, in_invoice=False
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
                        ['Exenta']['DetalleExenta']
                    )
                    self.detalle_iva = detalle_iva

                with it('la BaseImponible debe ser la original'):
                    total_base = sum([x.base for x in self.out_invoice.tax_line if 'IVA' in x.name])
                    expect(
                        self.detalle_iva['BaseImponible']
                    ).to(equal(
                        total_base
                    ))
                with it('la Causa Exención tiene que ser E2'):
                    expect(
                        self.detalle_iva['CausaExencion']
                    ).to(equal('E2'))
                with it('No lleva ni tipo impositivo ni Cuota'):
                    expect(
                        self.detalle_iva.get('TipoImpositivo','NOTEXIST')
                    ).to(equal('NOTEXIST'))
                    expect(
                        self.detalle_iva.get('CuotaRepercutida','NOTEXIST')
                    ).to(equal('NOTEXIST'))

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

        with context('en los detalles del IVA con IRPF'):
            with before.all:
                self.out_invoice_irpf = self.data_gen.get_out_invoice_with_irfp()

                self.out_invoice_obj = SII(self.out_invoice_irpf).generate_object()
                self.factura_emitida = (
                    self.out_invoice_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
                )
                self.detalle_iva_irpf_list = get_iva_values(self.out_invoice_irpf, in_invoice=False)
                self.detalle_iva_desglose_irpf = (
                    self.factura_emitida['FacturaExpedida']['TipoDesglose']
                    ['DesgloseFactura']['Sujeta']['NoExenta']['DesgloseIVA']
                    ['DetalleIVA'][0]
                )

            with context('debe contener'):
                with it('solo la parte del IVA'):
                    tax_line_iva = None
                    for x in self.out_invoice_irpf.tax_line:
                        if 'IVA' in x.name.upper():
                            tax_line_iva = x
                    expect(
                        self.detalle_iva_desglose_irpf['BaseImponible']
                    ).to(equal(
                        tax_line_iva.base
                    ))
                    expect(
                        Decimal('2400')
                    ).to(
                        equal(
                            self.detalle_iva_desglose_irpf['BaseImponible']
                        )
                    )
                    expect(
                        Decimal('504')
                    ).to(
                        equal(
                            self.detalle_iva_desglose_irpf['CuotaRepercutida']

                        )
                    )
                    expect(
                        self.detalle_iva_desglose_irpf['CuotaRepercutida']
                    ).to(equal(
                        tax_line_iva.tax_amount
                    ))
                    expect(
                        Decimal('21.0')
                    ).to(
                        equal(
                            self.detalle_iva_desglose_irpf['TipoImpositivo']
                        )
                    )
                    expect(
                        self.detalle_iva_desglose_irpf['TipoImpositivo']
                    ).to(equal(
                        tax_line_iva.tax_id.amount * 100
                    ))

    with description('en los datos de una factura recibida'):
        with before.all:
            self.in_invoice = self.data_gen.get_in_invoice()
            self.in_invoice_obj = SII(self.in_invoice).generate_object()
            self.factura_recibida = (
                self.in_invoice_obj['SuministroLRFacturasRecibidas']
                ['RegistroLRFacturasRecibidas']
            )
        with context('la fecha de factura del periodo de liquidacion'):
            with it('debe ser la fecha factura'):
                period_value = '{}/{}'.format(
                    self.factura_recibida['PeriodoLiquidacion']['Periodo'],
                    self.factura_recibida['PeriodoLiquidacion']['Ejercicio']
                )
                expect(
                    period_value
                ).to(equal('12/2016'))

        with context('en los datos del emisor de la factura'):

            with context('si no está registrado en la AEAT'):
                with before.all:
                    new_data_gen = DataGenerator(contraparte_registered=False)
                    self.in_invoice = new_data_gen.get_in_invoice()
                    # Valid French TVA FR23334175221
                    self.in_invoice.partner_id.country_id.code = 'FR'
                    self.in_invoice.partner_id.country_id.is_eu_member = True
                    self.in_invoice.partner_id.vat = 'FR23334175221'

                    in_invoice_obj = SII(self.in_invoice).generate_object()
                    self.emisor_factura = (
                        in_invoice_obj['SuministroLRFacturasRecibidas']
                        ['RegistroLRFacturasRecibidas']['IDFactura']
                        ['IDEmisorFactura']
                    )

                with it('el ID debe ser el NIF del emisor'):
                    nif_emisor = self.in_invoice.partner_id.vat
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
                    detalle_iva_desglose_iva, in_invoice=True
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

        with context('en los detalles del IVA inversion sujeto pasivo'):
            with before.all:
                in_invoice_isp = self.data_gen.get_in_invoice_with_isp()

                self.in_invoice_obj = SII(in_invoice_isp).generate_object()
                self.factura_recibida = (
                    self.in_invoice_obj['SuministroLRFacturasRecibidas']
                    ['RegistroLRFacturasRecibidas']
                )
                self.detalle_iva_isp_list = get_iva_values(in_invoice_isp, in_invoice=True)
                self.detalle_iva_isp = (
                    self.factura_recibida['FacturaRecibida']['DesgloseFactura']
                    ['InversionSujetoPasivo']
                )

                # self.grouped_detalle_iva_isp = group_by_tax_rate(
                #     self.detalle_iva_isp, in_invoice=True
                # )
            with context('debe contener Sujeto Passivo'):
                with it('la parte de detalle de iva debe tener los valores de la factura'):
                    expect(
                        Decimal('20.02')
                    ).to(
                        equal(
                            self.detalle_iva_isp_list[
                                'inversion_sujeto_pasivo'][0]['BaseImponible']
                        )
                    )
                    expect(
                        Decimal('4.20')
                    ).to(
                        equal(
                            self.detalle_iva_isp_list[
                                      'inversion_sujeto_pasivo'][0]['CuotaSoportada']

                        )
                    )
                    expect(
                        Decimal('21.0')
                    ).to(
                        equal(
                            self.detalle_iva_isp_list[
                                'inversion_sujeto_pasivo'][0]['TipoImpositivo']
                        )
                    )
                with it('la parte de detalle de iva debe tener los valores de la factura tiene que ser igual que el los datos a enviar'):
                    expect(
                        self.detalle_iva_isp_list[
                            'inversion_sujeto_pasivo'][0]['BaseImponible']
                    ).to(
                        equal(
                            Decimal(
                                str(self.detalle_iva_isp['DetalleIVA'][0]['BaseImponible'])
                            )
                        )
                    )
                    expect(
                        self.detalle_iva_isp_list[
                            'inversion_sujeto_pasivo'][0]['CuotaSoportada']
                    ).to(
                        equal(
                            Decimal(str(self.detalle_iva_isp['DetalleIVA'][0]['CuotaSoportada']))
                        )
                    )
                    expect(
                        self.detalle_iva_isp_list[
                            'inversion_sujeto_pasivo'][0]['TipoImpositivo']
                    ).to(
                        equal(
                            Decimal(str(self.detalle_iva_isp['DetalleIVA'][0]['TipoImpositivo']))
                        )
                    )
                with it('los datos a enviar tienen que ser igual'):
                    expect(
                        20.02
                    ).to(
                        equal(
                            self.detalle_iva_isp['DetalleIVA'][0]['BaseImponible']
                        )
                    )
                    expect(
                        4.20
                    ).to(
                        equal(
                            self.detalle_iva_isp['DetalleIVA'][0]['CuotaSoportada']
                        )
                    )
                    expect(
                        21.0
                    ).to(
                        equal(
                            self.detalle_iva_isp['DetalleIVA'][0]['TipoImpositivo']
                        )
                    )

        with context('en los detalles del IVA con IRPF'):
            with before.all:
                self.in_invoice_irpf = self.data_gen.get_in_invoice_with_irfp()

                self.in_invoice_obj = SII(self.in_invoice_irpf).generate_object()
                self.factura_recibida = (
                    self.in_invoice_obj['SuministroLRFacturasRecibidas']
                    ['RegistroLRFacturasRecibidas']
                )
                self.detalle_iva_irpf_list = get_iva_values(self.in_invoice_irpf, in_invoice=True)
                self.detalle_iva_desglose_irpf = (
                    self.factura_recibida['FacturaRecibida']['DesgloseFactura']
                    ['DesgloseIVA']['DetalleIVA'][0]
                )

            with context('debe contener'):
                with it('solo la parte del IVA'):
                    tax_line_iva = None
                    for x in self.in_invoice_irpf.tax_line:
                        if 'IVA' in x.name.upper():
                            tax_line_iva = x
                    expect(
                        self.detalle_iva_desglose_irpf['BaseImponible']
                    ).to(equal(
                        tax_line_iva.base
                    ))
                    expect(
                        Decimal('2400')
                    ).to(
                        equal(
                            self.detalle_iva_desglose_irpf['BaseImponible']
                        )
                    )
                    expect(
                        Decimal('504')
                    ).to(
                        equal(
                            self.detalle_iva_desglose_irpf['CuotaSoportada']

                        )
                    )
                    expect(
                        self.detalle_iva_desglose_irpf['CuotaSoportada']
                    ).to(equal(
                        tax_line_iva.tax_amount
                    ))
                    expect(
                        Decimal('21.0')
                    ).to(
                        equal(
                            self.detalle_iva_desglose_irpf['TipoImpositivo']
                        )
                    )
                    expect(
                        self.detalle_iva_desglose_irpf['TipoImpositivo']
                    ).to(equal(
                        tax_line_iva.tax_id.amount * 100
                    ))

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
                        detalle_iva_desglose_iva, in_invoice=True
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

    with description('en los datos de una factura recibida sin periodo'):
        with before.all:
            self.in_invoice = self.data_gen.get_in_invoice_without_period()
            self.in_invoice_obj = SII(self.in_invoice).generate_object()
            self.factura_recibida = (
                self.in_invoice_obj['SuministroLRFacturasRecibidas']
                ['RegistroLRFacturasRecibidas']
            )
        with context('la fecha de factura del periodo de liquidacion'):
            with it('debe ser la fecha factura'):
                period_value = '{}/{}'.format(
                    self.factura_recibida['PeriodoLiquidacion']['Periodo'],
                    self.factura_recibida['PeriodoLiquidacion']['Ejercicio']
                )
                expect(
                    period_value
                ).to(equal('12/2016'))

        with context('en los datos del emisor de la factura'):

            with context('si no está registrado en la AEAT'):
                with before.all:
                    new_data_gen = DataGenerator(contraparte_registered=False)
                    self.in_invoice = new_data_gen.get_in_invoice()
                    # Valid French TVA FR23334175221
                    self.in_invoice.partner_id.country_id.code = 'FR'
                    self.in_invoice.partner_id.country_id.is_eu_member = True
                    self.in_invoice.partner_id.vat = 'FR23334175221'

                    in_invoice_obj = SII(self.in_invoice).generate_object()
                    self.emisor_factura = (
                        in_invoice_obj['SuministroLRFacturasRecibidas']
                        ['RegistroLRFacturasRecibidas']['IDFactura']
                        ['IDEmisorFactura']
                    )

                with it('el ID debe ser el NIF del emisor'):
                    nif_emisor = self.in_invoice.partner_id.vat
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
                    detalle_iva_desglose_iva, in_invoice=True
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
                        detalle_iva_desglose_iva, in_invoice=True
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
            self.out_refund, self.out_b_inovice = self.data_gen.get_out_refund_invoice()
            self.out_refund_obj = SII(self.out_refund).generate_object()
            self.out_b_inovice_obj = SII(self.out_b_inovice).generate_object()
            self.fact_rect_emit = (
                self.out_refund_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
            self.fact_refund_emit = (
                self.out_b_inovice_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
        with context('en los datos de abonadora'):
            with it('la FechaOperacion NO debe ser informado'):
                expect(
                     self.fact_refund_emit['FacturaExpedida'].get('FechaOperacion', False)
                ).to(equal(False))
        with context('en los datos de rectificación'):
            with it('el TipoRectificativa debe ser por sustitución (S)'):
                expect(
                    self.fact_rect_emit['FacturaExpedida']['TipoRectificativa']
                ).to(equal('S'))

            with it('la FechaOperacion NO debe ser informado'):
                expect(
                    self.fact_rect_emit['FacturaExpedida'].get('FechaOperacion', False)
                ).to(equal(False))

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
                self.grouped_detalle_iva = group_by_tax_rate(
                    detalle_iva, in_invoice=False
                )

            with it('la BaseImponible debe ser la original'):
                expect(
                    self.grouped_detalle_iva[21.0]['BaseImponible']
                ).to(equal(
                    self.out_refund.tax_line[0].base
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

    with description('en los datos de una factura rectificativa emitida con IVA 5% fecha postrior vigencia como tipo R4'):
        with before.all:
            self.out_refund, self.out_b_inovice = self.data_gen.get_out_refund_invoice_iva5(sii_non_current_tax_rate='R4')
            self.out_refund_obj = SII(self.out_refund).generate_object()
            self.out_b_inovice_obj = SII(self.out_b_inovice).generate_object()
            self.fact_rect_emit = (
                self.out_refund_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
            self.fact_refund_emit = (
                self.out_b_inovice_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
        with context('en los datos de abonadora'):
            with it('la FechaOperacion debe ser por factura original'):
                expect(
                     self.fact_refund_emit['FacturaExpedida']['FechaOperacion']
                ).to(equal('01-01-2023'))
            with it('la TipoRectificativa debe ser S'):
                expect(
                    self.fact_refund_emit['FacturaExpedida']['TipoRectificativa']
                ).to(equal('S'))
            with it('la TipoFactura tiene que ser R4'):
                expect(
                    self.fact_refund_emit['FacturaExpedida'][
                        'TipoFactura']
                ).to(equal('R4'))
        with context('en los datos de rectificación'):
            with it('el TipoRectificativa debe ser por sustitución (S)'):
                expect(
                    self.fact_rect_emit['FacturaExpedida']['TipoRectificativa']
                ).to(equal('S'))

            with it('la FechaOperacion debe ser por factura original'):
                expect(
                    self.fact_rect_emit['FacturaExpedida']['FechaOperacion']
                ).to(equal('01-01-2023'))

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
                self.grouped_detalle_iva = group_by_tax_rate(
                    detalle_iva, in_invoice=False
                )

            with it('la BaseImponible debe ser la original'):
                expect(
                    self.grouped_detalle_iva[5.0]['BaseImponible']
                ).to(equal(
                    self.out_refund.tax_line[0].base
                ))
            with it('la CuotaRepercutida debe ser la original'):
                expect(
                    self.grouped_detalle_iva[5.0]['CuotaRepercutida']
                ).to(equal(
                    -1 * abs(self.out_refund.tax_line[0].tax_amount)
                ))
            with it('el TipoImpositivo debe ser la original'):
                expect(
                    self.grouped_detalle_iva[5.0]['TipoImpositivo']
                ).to(equal(
                    self.out_refund.tax_line[0].tax_id.amount * 100
                ))

    with description('en los datos de una factura rectificativa emitida con IVA 5% fecha postrior vigencia como tipo F1'):
        with before.all:
            self.out_refund, self.out_b_inovice = self.data_gen.get_out_refund_invoice_iva5(sii_non_current_tax_rate='F1')
            self.out_refund_obj = SII(self.out_refund).generate_object()
            self.out_b_inovice_obj = SII(self.out_b_inovice).generate_object()
            self.fact_rect_emit = (
                self.out_refund_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
            self.fact_refund_emit = (
                self.out_b_inovice_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
        with context('en los datos de abonadora'):
            with it('la FechaOperacion debe ser por factura original'):
                expect(
                    self.fact_refund_emit['FacturaExpedida']['FechaOperacion']
                ).to(equal('01-01-2023'))
            with it('la TipoRectificativa NO debe existir'):
                expect(
                    self.fact_refund_emit['FacturaExpedida'].get(
                        'TipoRectificativa', False)
                ).to(equal(False))
            with it('la TipoFactura tiene que ser F1'):
                expect(
                    self.fact_refund_emit['FacturaExpedida'][
                        'TipoFactura']
                ).to(equal('F1'))
        with context('en los datos de rectificación'):
            with it('el TipoRectificativa debe ser por sustitución (S)'):
                expect(
                    self.fact_rect_emit['FacturaExpedida']['TipoRectificativa']
                ).to(equal('S'))

            with it('la FechaOperacion debe ser por factura original'):
                expect(
                    self.fact_rect_emit['FacturaExpedida']['FechaOperacion']
                ).to(equal('01-01-2023'))

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
                self.grouped_detalle_iva = group_by_tax_rate(
                    detalle_iva, in_invoice=False
                )

            with it('la BaseImponible debe ser la original'):
                expect(
                    self.grouped_detalle_iva[5.0]['BaseImponible']
                ).to(equal(
                    self.out_refund.tax_line[0].base
                ))
            with it('la CuotaRepercutida debe ser la original'):
                expect(
                    self.grouped_detalle_iva[5.0]['CuotaRepercutida']
                ).to(equal(
                    -1 * abs(self.out_refund.tax_line[0].tax_amount)
                ))
            with it('el TipoImpositivo debe ser la original'):
                expect(
                    self.grouped_detalle_iva[5.0]['TipoImpositivo']
                ).to(equal(
                    self.out_refund.tax_line[0].tax_id.amount * 100
                ))

    with description('en los datos de una factura rectificativa emitida con IVA 5% fecha en vigencia'):
        with before.all:
            self.out_refund, self.out_b_inovice = self.data_gen.get_out_refund_invoice_iva5(fecha_facturas_recti='2024-03-18')
            self.out_refund_obj = SII(self.out_refund).generate_object()
            self.out_b_inovice_obj = SII(self.out_b_inovice).generate_object()
            self.fact_rect_emit = (
                self.out_refund_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
            self.fact_refund_emit = (
                self.out_b_inovice_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
        with context('en los datos de abonadora'):
            with it('la FechaOperacion debe ser por factura original'):
                expect(
                     self.fact_refund_emit['FacturaExpedida'].get(
                         'FechaOperacion', False)
                ).to(equal(False))
            with it('la TipoRectificativa NO debe ser informado'):
                expect(
                    self.fact_refund_emit['FacturaExpedida'].get('TipoRectificativa',False)
                ).to(equal(False))
            with it('la TipoFactura tiene que ser F1'):
                expect(
                    self.fact_refund_emit['FacturaExpedida'].get('TipoFactura', False)
                ).to(equal('F1'))
        with context('en los datos de rectificación'):
            with it('el TipoRectificativa debe ser por sustitución (S)'):
                expect(
                    self.fact_rect_emit['FacturaExpedida']['TipoRectificativa']
                ).to(equal('S'))

            with it('la FechaOperacion no debe existir'):
                expect(
                    self.fact_rect_emit['FacturaExpedida'].get('FechaOperacion', False)
                ).to(equal(False))
            with it('la TipoRectificativa debe ser S'):
                expect(
                    self.fact_rect_emit['FacturaExpedida'].get('TipoRectificativa',False)
                ).to(equal('S'))
            with it('la TipoFactura tiene que ser R4'):
                expect(
                    self.fact_rect_emit['FacturaExpedida'][
                        'TipoFactura']
                ).to(equal('R4'))

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
                self.grouped_detalle_iva = group_by_tax_rate(
                    detalle_iva, in_invoice=False
                )

            with it('la BaseImponible debe ser la original'):
                expect(
                    self.grouped_detalle_iva[5.0]['BaseImponible']
                ).to(equal(
                    self.out_refund.tax_line[0].base
                ))
            with it('la CuotaRepercutida debe ser la original'):
                expect(
                    self.grouped_detalle_iva[5.0]['CuotaRepercutida']
                ).to(equal(
                    -1 * abs(self.out_refund.tax_line[0].tax_amount)
                ))
            with it('el TipoImpositivo debe ser la original'):
                expect(
                    self.grouped_detalle_iva[5.0]['TipoImpositivo']
                ).to(equal(
                    self.out_refund.tax_line[0].tax_id.amount * 100
                ))

    with description('en los datos de una factura rectificativa de una rectificativa emitida iva 5%'):
        with before.all:
            self.out_refund, self.out_b_inovice = self.data_gen.get_out_refund_invoice_iva5_multi()
            self.out_refund_obj = SII(self.out_refund).generate_object()
            self.out_b_inovice_obj = SII(self.out_b_inovice).generate_object()
            self.fact_rect_emit = (
                self.out_refund_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
            self.fact_refund_emit = (
                self.out_b_inovice_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
        with context('en los datos de abonadora'):
            with it('la FechaOperacion debe ser por factura original'):
                expect(
                    self.fact_refund_emit['FacturaExpedida']['FechaOperacion']
                ).to(equal('01-01-2023'))
            with it('la TipoRectificativa debe ser S'):
                expect(
                    self.fact_refund_emit['FacturaExpedida']['TipoRectificativa']
                ).to(equal('S'))
            with it('la TipoFactura tiene que ser R4'):
                expect(
                    self.fact_refund_emit['FacturaExpedida'][
                        'TipoFactura']
                ).to(equal('R4'))
        with context('en los datos de rectificación'):
            with it('la FechaOperacion debe ser por factura original'):
                expect(
                    self.fact_rect_emit['FacturaExpedida']['FechaOperacion']
                ).to(equal('01-01-2023'))

    with description('en los datos de una factura rectificativa de una rectificativa emitida'):
        with before.all:
            self.out_refund, self.out_b_inovice = self.data_gen.get_out_refund_mulitple_invoice()
            self.out_refund_obj = SII(self.out_refund).generate_object()
            self.out_b_inovice_obj = SII(self.out_b_inovice).generate_object()
            self.fact_rect_emit = (
                self.out_refund_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
            self.fact_refund_emit = (
                self.out_b_inovice_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )
        with context('en los datos de abonadora'):
            with it('la FechaOperacion debe ser por factura original'):
                expect(
                    self.fact_refund_emit['FacturaExpedida'].get('FechaOperacion', False)
                ).to(equal(False))
        with context('en los datos de rectificación'):
            with it('la FechaOperacion NO debe existir'):
                expect(
                    self.fact_rect_emit['FacturaExpedida'].get('FechaOperacion', False)
                ).to(equal(False))

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
                self.grouped_detalle_iva = group_by_tax_rate(
                    detalle_iva, in_invoice=True
                )

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
            factura_rectificada = self.out_invoice_RA.rectifying_id
            self.out_invoice_origin_obj = SII(factura_rectificada).generate_object()
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
                    700
                ))

                expect(
                    self.fact_RA_emitida['FacturaExpedida']
                    ['ImporteRectificacion']['CuotaRectificada']
                ).to(equal(
                    79
                ))

    with description('en los datos de una factura recibida rectificativa '
                     'sin anuladora RA'):
        with before.all:
            self.in_invoice_RA = self.data_gen.get_in_invoice_RA()
            self.in_invoice_RA.rectifying_id.sii_registered = True
            self.in_invoice_RA_obj = SII(self.in_invoice_RA).generate_object()
            factura_rectificada = self.in_invoice_RA.rectifying_id
            self.in_invoice_origin_obj = SII(factura_rectificada).generate_object()
            self.fact_RA_recibida = (
                self.in_invoice_RA_obj['SuministroLRFacturasRecibidas']
                ['RegistroLRFacturasRecibidas']
            )
            self.fact_origin = (
                self.in_invoice_origin_obj['SuministroLRFacturasRecibidas']
                ['RegistroLRFacturasRecibidas']
            )

        with context('en los datos de rectificación'):
            with it('el TipoRectificativa debe ser por sustitución (S)'):
                expect(
                    self.fact_RA_recibida['FacturaRecibida']['TipoRectificativa']
                ).to(equal('S'))
            with it('la FechaOperacion NO debe existir'):
                expect(
                    self.fact_RA_recibida['FacturaRecibida'].get('FechaOperacion', False)
                ).to(equal(False))
            with it('debe contener las FacturasRectificadas'):
                expect(
                    self.fact_RA_recibida['FacturaRecibida']
                    ['FacturasRectificadas']['IDFacturaRectificada'][0]
                    ['NumSerieFacturaEmisor']
                ).to(equal(
                    self.in_invoice_RA.rectifying_id.origin
                ))

                fecha_expedicion = (
                    self.fact_RA_recibida['FacturaRecibida']
                    ['FacturasRectificadas']['IDFacturaRectificada'][0]
                    ['FechaExpedicionFacturaEmisor']
                )
                expect(
                    datetime.strptime(
                        fecha_expedicion, '%d-%m-%Y'
                    ).strftime('%Y-%m-%d')
                ).to(equal(
                    self.in_invoice_RA.rectifying_id.origin_date_invoice
                ))

            with it('debe contener el ImporteRectificacion'):
                expect(
                    self.fact_RA_recibida['FacturaRecibida']
                    ['ImporteRectificacion']['BaseRectificada']
                ).to(equal(
                    6608.0
                ))

                expect(
                    self.fact_RA_recibida['FacturaRecibida']
                    ['ImporteRectificacion']['CuotaRectificada']
                ).to(equal(
                    -79.0
                ))
            with it('los Importes de rectificacion debe ser igual que los datos de la factura original'):
                base_presentada = sum(x['BaseImponible'] for x in
                    self.fact_origin['FacturaRecibida']['DesgloseFactura'][
                        'DesgloseIVA']['DetalleIVA'])
                cuota_presentada = sum(
                    x.get('CuotaSoportada', 0.0) for x in
                    self.fact_origin['FacturaRecibida'][
                        'DesgloseFactura']['DesgloseIVA']['DetalleIVA'])
                expect(
                    self.fact_RA_recibida['FacturaRecibida']
                    ['ImporteRectificacion']['BaseRectificada']
                ).to(equal(
                    base_presentada
                ))

                expect(
                    self.fact_RA_recibida['FacturaRecibida']
                    ['ImporteRectificacion']['CuotaRectificada']
                ).to(equal(
                    cuota_presentada
                ))

    with description('en los datos de una factura recibida rectificativa '
                     'sin anuladora RA sobre una factura original negativa'):
        with before.all:
            self.in_invoice_RA = self.data_gen.get_in_invoice_RA_N_negative()
            self.in_invoice_RA.rectifying_id.sii_registered = True
            self.in_invoice_RA_obj = SII(self.in_invoice_RA).generate_object()
            factura_rectificada = self.in_invoice_RA.rectifying_id
            self.in_invoice_origin_obj = SII(factura_rectificada).generate_object()
            self.fact_RA_recibida = (
                self.in_invoice_RA_obj['SuministroLRFacturasRecibidas']
                ['RegistroLRFacturasRecibidas']
            )
            self.fact_origin = (
                self.in_invoice_origin_obj['SuministroLRFacturasRecibidas']
                ['RegistroLRFacturasRecibidas']
            )

        with context('en los datos de rectificación'):
            with it('el TipoRectificativa debe ser por sustitución (S)'):
                expect(
                    self.fact_RA_recibida['FacturaRecibida']['TipoRectificativa']
                ).to(equal('S'))
            with it('la FechaOperacion NO debe existir'):
                expect(
                    self.fact_RA_recibida['FacturaRecibida'].get('FechaOperacion', False)
                ).to(equal(False))
            with it('debe contener las FacturasRectificadas'):
                expect(
                    self.fact_RA_recibida['FacturaRecibida']
                    ['FacturasRectificadas']['IDFacturaRectificada'][0]
                    ['NumSerieFacturaEmisor']
                ).to(equal(
                    self.in_invoice_RA.rectifying_id.origin
                ))

                fecha_expedicion = (
                    self.fact_RA_recibida['FacturaRecibida']
                    ['FacturasRectificadas']['IDFacturaRectificada'][0]
                    ['FechaExpedicionFacturaEmisor']
                )
                expect(
                    datetime.strptime(
                        fecha_expedicion, '%d-%m-%Y'
                    ).strftime('%Y-%m-%d')
                ).to(equal(
                    self.in_invoice_RA.rectifying_id.origin_date_invoice
                ))

            with it('debe contener el ImporteRectificacion'):
                expect(
                    self.fact_RA_recibida['FacturaRecibida']
                    ['ImporteRectificacion']['BaseRectificada']
                ).to(equal(
                    -5.13
                ))

                expect(
                    self.fact_RA_recibida['FacturaRecibida']
                    ['ImporteRectificacion']['CuotaRectificada']
                ).to(equal(
                    -1.08
                ))
            with it('los Importes de rectificacion debe ser igual que los datos de la factura original'):
                base_presentada = sum(x['BaseImponible'] for x in
                    self.fact_origin['FacturaRecibida']['DesgloseFactura'][
                        'DesgloseIVA']['DetalleIVA'])
                cuota_presentada = sum(
                    x.get('CuotaSoportada', 0.0) for x in
                    self.fact_origin['FacturaRecibida'][
                        'DesgloseFactura']['DesgloseIVA']['DetalleIVA'])
                expect(
                    self.fact_RA_recibida['FacturaRecibida']
                    ['ImporteRectificacion']['BaseRectificada']
                ).to(equal(
                    base_presentada
                ))

                expect(
                    self.fact_RA_recibida['FacturaRecibida']
                    ['ImporteRectificacion']['CuotaRectificada']
                ).to(equal(
                    cuota_presentada
                ))

with description('El XML Generado en una baja de una factura emitida'):
    with before.all:
        self.data_gen = DataGenerator()

    with description('en la cabecera'):
        with before.all:
            self.invoice = self.data_gen.get_out_invoice()
            self.invoice_obj = (
                SIIDeregister(self.invoice).generate_object()
            )
            self.cabecera = (
                self.invoice_obj['BajaLRFacturasEmitidas']['Cabecera']
            )

        with it('la versión es la "1.1"'):
            expect(self.cabecera['IDVersionSii']).to(equal('1.1'))

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
                SIIDeregister(self.invoice).generate_object()
            )
            self.factura_emitida = (
                self.invoice_obj['BajaLRFacturasEmitidas']
                ['RegistroLRBajaExpedidas']
            )

        with context('en los datos del período'):
            with before.all:
                self.periodo = self.factura_emitida['PeriodoLiquidacion']

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
                SIIDeregister(self.invoice).generate_object()
            )
            self.cabecera = (
                self.invoice_obj['BajaLRFacturasRecibidas']['Cabecera']
            )

        with it('la versión es la "1.1"'):
            expect(self.cabecera['IDVersionSii']).to(equal('1.1'))

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
                SIIDeregister(self.invoice).generate_object()
            )
            self.factura_recibida = (
                self.invoice_obj['BajaLRFacturasRecibidas']
                ['RegistroLRBajaRecibidas']
            )

        with context('en los datos del período'):
            with before.all:
                self.periodo = self.factura_recibida['PeriodoLiquidacion']

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

    with description('en los datos de una factura rectificativa emitida'):
        with before.all:
            self.out_refund = self.data_gen.get_out_invoice_rescision()
            self.out_refund_obj = SII(self.out_refund).generate_object()
            self.fact_rect_emit = (
                self.out_refund_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )

        with context('en los datos de rectificación'):
            with it('el TipoRectificativa debe ser por sustitución (S)'):
                expect(
                    self.fact_rect_emit['FacturaExpedida']['TipoRectificativa']
                ).to(equal('I'))

        with context('en los detalles del IVA'):
            with before.all:
                detalle_iva = (
                    self.fact_rect_emit['FacturaExpedida']['TipoDesglose']
                    ['DesgloseFactura']['Sujeta']['NoExenta']['DesgloseIVA']
                    ['DetalleIVA']
                )
                self.grouped_detalle_iva = group_by_tax_rate(
                    detalle_iva, in_invoice=False
                )

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

    with description('en los datos de una factura emitida'):
        with before.all:
            self.out_invoice = self.data_gen.get_out_invoice()
            self.out_invoice_obj = SII(self.out_invoice).generate_object()
            self.factura_emitida = (
                self.out_invoice_obj['SuministroLRFacturasEmitidas']
                ['RegistroLRFacturasEmitidas']
            )

        with context('en una contraparte con IDType 05'):
            with before.all:
                new_data_gen = DataGenerator(contraparte_registered=False)
                self.out_invoice = new_data_gen.get_out_invoice_partner_id_type_05()
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

            with it('el IDType debe ser "05"'):
                expect(self.contraparte['IDOtro']['IDType']).to(equal('05'))

            with it('el CodigoPais debe ser "ES"'):
                expect(self.contraparte['IDOtro']['CodigoPais']).to(equal('ES'))
