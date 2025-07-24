# -*- coding: utf-8 -*-

import os
import random
from decimal import Decimal
from sii.models.basic_models import *


class DataGenerator:
    def __init__(self, invoice_registered=False, contraparte_registered=True):
        self.sii_registered = invoice_registered
        self.period = Period(name='12/2016')
        self.article = Article(tipo_factura='R1', tipo_rectificativa='I')
        name_iva_21 = 'IVA 21%'
        name_iva_4 = 'IVA 4%'
        name_iva_5 = 'IVA 5%'
        name_ibi = 'IBI 15%'
        name_iva_exento = 'IVA Exento'
        tax_ibi = Tax(name=name_ibi, amount=0.15, type='percent')
        tax_iva_21 = Tax(name=name_iva_21, amount=0.21, type='percent')
        tax_iva_4 = Tax(name=name_iva_4, amount=0.04, type='percent')
        self.tax_iva_5 = Tax(name=name_iva_5, amount=0.05, type='percent')
        tax_iva_exento = Tax(name=name_iva_exento, amount=0, type='percent')
        self.invoice_line = [
            InvoiceLine(price_subtotal=100, invoice_line_tax_id=[tax_iva_21]),
            InvoiceLine(
                price_subtotal=200, invoice_line_tax_id=[tax_iva_21, tax_ibi]
            ),
            InvoiceLine(price_subtotal=400, invoice_line_tax_id=[tax_iva_4]),
            InvoiceLine(price_subtotal=800, invoice_line_tax_id=[tax_ibi]),
            InvoiceLine(
                price_subtotal=1600, invoice_line_tax_id=[tax_iva_exento]
            ),
            InvoiceLine(price_subtotal=3200, invoice_line_tax_id=[])
        ]

        base_iva_21 = sum(
            [line.price_subtotal
             for line in self.invoice_line
             if tax_iva_21 in line.invoice_line_tax_id]
        )
        base_iva_4 = sum(
            [line.price_subtotal
             for line in self.invoice_line
             if tax_iva_4 in line.invoice_line_tax_id]
        )
        base_ibi = sum(
            [line.price_subtotal
             for line in self.invoice_line
             if tax_ibi in line.invoice_line_tax_id]
        )
        base_iva_exento = sum(
            [line.price_subtotal
             for line in self.invoice_line
             if tax_iva_exento in line.invoice_line_tax_id]
        )
        invoice_tax_iva_21 = InvoiceTax(
            name=name_iva_21, base=base_iva_21,
            tax_amount=base_iva_21 * tax_iva_21.amount, tax_id=tax_iva_21
        )
        invoice_tax_iva_4 = InvoiceTax(
            name=name_iva_4, base=base_iva_4,
            tax_amount=base_iva_4 * tax_iva_4.amount, tax_id=tax_iva_4
        )
        invoice_tax_ibi = InvoiceTax(
            name=name_ibi, base=base_ibi,
            tax_amount=base_ibi * tax_ibi.amount, tax_id=tax_ibi
        )
        invoice_tax_iva_exento = InvoiceTax(
            name=name_iva_exento, base=base_iva_exento,
            tax_amount=base_iva_exento * tax_iva_exento.amount,
            tax_id=tax_iva_exento
        )
        self.tax_line = [
            invoice_tax_iva_21, invoice_tax_iva_4, invoice_tax_ibi,
            invoice_tax_iva_exento
        ]
        spain = Country(code='ES', is_eu_member=False)
        self.fiscal_name = os.environ.get(
            'FISCAL_NOMBRE_CONTRAPARTE', u'Qwerting Tarantino')
        self.fiscal_vat = os.environ.get(
            'FISCAL_VAT_CONTRAPARTE', u'ES09346536A')
        self.partner_invoice = Partner(
            name=os.environ.get('NOMBRE_CONTRAPARTE', u'Francisco García'),
            nif=os.environ.get('NIF_CONTRAPARTE', u'ES12345678Z'),
            country=spain, aeat_registered=contraparte_registered
        )
        partner_company = Partner(
            name=os.environ.get('NOMBRE_TITULAR', u'Compañía Eléctrica S.A.'),
            nif=os.environ.get('NIF_TITULAR', 'ES55555555K'), country=spain
        )
        self.company = Company(partner_id=partner_company)

        comunidad_autonoma = ComunidadAutonoma(code='01', name='Andalucia')
        provincia = State(comunidad_autonoma=comunidad_autonoma)
        self.address_contact_id = ResPartnerAddress(state=provincia)

        self.invoice_number = str(random.randrange(0, 100000)).zfill(5)
        self.origin_date_invoice = '2016-12-01'
        self.date_invoice = '2016-12-31'
        taxes_amount = sum([tax.tax_amount for tax in self.tax_line])
        base_amount = sum([line.price_subtotal for line in self.invoice_line])
        self.amount_tax = taxes_amount
        self.amount_untaxed = base_amount
        self.amount_total = taxes_amount + base_amount
        self.fiscal_position = FiscalPosition(
            name=u'Régimen Islas Canarias'
        )
        self.fiscal_position_general = FiscalPosition(
            name=u'Régimen General 2024'
        )
        self.sii_description = u'Descripción de operación estándar'
        self.sii_in_clave_regimen_especial = '01'
        self.sii_out_clave_regimen_especial = '01'

    def get_in_invoice(self):
        journal = Journal(
            name=u'Factura de Energía Recibida'
        )

        invoice = Invoice(
            invoice_type='in_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FRecib{}'.format(self.invoice_number),
            origin='FRecibOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )
        return invoice

    def get_in_invoice_with_isp(self, with_extra_lines=False):
        journal = Journal(
            name=u'Factura de Energía Recibida'
        )

        tax_iva_isp_compra_21 = Tax(
            name='IVA 21% Inversión del sujeto pasivo',
            amount=0.0, type='percent'
        )
        invoice_line = [
            InvoiceLine(
                price_subtotal=20.02,
                invoice_line_tax_id=[tax_iva_isp_compra_21])
        ]
        base_iva_isp = sum(
            [line.price_subtotal
             for line in invoice_line]
        )
        tax_iva_isp_soportado_21 = Tax(
            name='IVA 21% Inversión del sujeto pasivo (1)',
            amount=0.21, type='percent'
        )
        tax_iva_isp_repercutido_21 = Tax(
            name='IVA 21% Inversión del sujeto pasivo (1)',
            amount=-0.21, type='percent'
        )
        invoice_tax_iva_isp_soportado_21 = InvoiceTax(
            name=tax_iva_isp_soportado_21.name, base=base_iva_isp,
            tax_amount=4.2,
            tax_id=tax_iva_isp_soportado_21
        )
        tax_iva_isp_repercutido_21 = InvoiceTax(
            name=tax_iva_isp_repercutido_21.name, base=base_iva_isp,
            tax_amount=-4.2,
            tax_id=tax_iva_isp_repercutido_21
        )
        tax_line_inversion_sujeto_pasivo = [
            tax_iva_isp_repercutido_21, invoice_tax_iva_isp_soportado_21
        ]
        tax_lines = tax_line_inversion_sujeto_pasivo
        invoice_lines = invoice_line
        if with_extra_lines:
            tax_lines += self.tax_line
            invoice_lines += self.invoice_line



        invoice = Invoice(
            invoice_type='in_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FRecib{}'.format(self.invoice_number),
            origin='FRecibOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=tax_lines,
            invoice_line=invoice_lines,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )
        return invoice

    def get_in_invoice_refound_with_isp(self, with_extra_lines=False):
        journal = Journal(
            name=u'Factura de Energía Rectificativa Recibida'
        )

        tax_iva_isp_compra_21 = Tax(
            name='IVA 21% Inversión del sujeto pasivo',
            amount=0.0, type='percent'
        )
        invoice_line = [
            InvoiceLine(
                price_subtotal=20.02,
                invoice_line_tax_id=[tax_iva_isp_compra_21])
        ]
        base_iva_isp = sum(
            [line.price_subtotal
             for line in invoice_line]
        )
        tax_iva_isp_soportado_21 = Tax(
            name='IVA 21% Inversión del sujeto pasivo (1)',
            amount=0.21, type='percent'
        )
        tax_iva_isp_repercutido_21 = Tax(
            name='IVA 21% Inversión del sujeto pasivo (1)',
            amount=-0.21, type='percent'
        )
        invoice_tax_iva_isp_soportado_21 = InvoiceTax(
            name=tax_iva_isp_soportado_21.name, base=base_iva_isp,
            tax_amount=4.2,
            tax_id=tax_iva_isp_soportado_21
        )
        tax_iva_isp_repercutido_21 = InvoiceTax(
            name=tax_iva_isp_repercutido_21.name, base=base_iva_isp,
            tax_amount=-4.2,
            tax_id=tax_iva_isp_repercutido_21
        )
        tax_line_inversion_sujeto_pasivo = [
            tax_iva_isp_repercutido_21, invoice_tax_iva_isp_soportado_21
        ]
        tax_lines = tax_line_inversion_sujeto_pasivo
        invoice_lines = invoice_line
        if with_extra_lines:
            tax_lines += self.tax_line
            invoice_lines += self.invoice_line

        fra_original = Invoice(
            invoice_type='in_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FRecibRectificada{}'.format(self.invoice_number),
            origin='FRectRecibRectificadaOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=tax_lines,
            invoice_line=invoice_lines,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )

        invoice = Invoice(
            invoice_type='in_refound',
            journal_id=journal,
            rectificative_type='R',
            rectifying_id=fra_original,
            number='FRectRecib{}'.format(self.invoice_number),
            origin='FRectRecibOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=tax_lines,
            invoice_line=invoice_lines,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )
        return invoice


    def get_in_invoice_without_period(self):
        journal = Journal(
            name=u'Factura de Energía Recibida'
        )

        invoice = Invoice(
            invoice_type='in_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FRecib{}'.format(self.invoice_number),
            origin='FRecibOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=None,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )
        return invoice

    def get_out_invoice(self, with_fiscal_info=True):
        journal = Journal(
            name=u'Factura de Energía Emitida'
        )
        if with_fiscal_info:
            invoice = Invoice(
                invoice_type='out_invoice',
                journal_id=journal,
                rectificative_type='N',
                rectifying_id=False,
                number='FEmit{}'.format(self.invoice_number),
                partner_id=self.partner_invoice,
                fiscal_name=self.fiscal_name,
                fiscal_vat=self.fiscal_vat,
                address_contact_id=self.address_contact_id,
                company_id=self.company,
                amount_total=self.amount_total,
                amount_untaxed=self.amount_untaxed,
                amount_tax=self.amount_tax,
                period_id=self.period,
                date_invoice=self.date_invoice,
                tax_line=self.tax_line,
                invoice_line=self.invoice_line,
                sii_registered=self.sii_registered,
                fiscal_position=self.fiscal_position,
                sii_description=self.sii_description,
                sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
            )
        else:
            invoice = Invoice(
                invoice_type='out_invoice',
                journal_id=journal,
                rectificative_type='N',
                rectifying_id=False,
                number='FEmit{}'.format(self.invoice_number),
                partner_id=self.partner_invoice,
                address_contact_id=self.address_contact_id,
                company_id=self.company,
                amount_total=self.amount_total,
                amount_untaxed=self.amount_untaxed,
                amount_tax=self.amount_tax,
                period_id=self.period,
                date_invoice=self.date_invoice,
                tax_line=self.tax_line,
                invoice_line=self.invoice_line,
                sii_registered=self.sii_registered,
                fiscal_position=self.fiscal_position,
                sii_description=self.sii_description,
                sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
            )
        return invoice

    def get_in_refund_invoice(self):
        journal = Journal(
            name=u'Factura de Energía Rectificativa Recibida'
        )

        tax_line = self.tax_line
        for invoice_tax in tax_line:
            invoice_tax.tax_amount = -1 * abs(invoice_tax.tax_amount)

        rect_invoice = Invoice(
            invoice_type='in_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FRecibRectificada{}'.format(self.invoice_number),
            origin='FRectRecibRectificadaOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )

        invoice = Invoice(
            invoice_type='in_refund',
            journal_id=journal,
            rectificative_type='R',
            rectifying_id=rect_invoice,
            number='FRectRecib{}'.format(self.invoice_number),
            origin='FRectRecibOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )
        return invoice

    def get_out_refund_invoice(self):
        journal = Journal(
            name=u'Factura de Energía Rectificativa Emitida'
        )
        rect_tax_line = self.tax_line[:]
        for invoice_tax in rect_tax_line:
            invoice_tax.tax_amount = -1 * abs(invoice_tax.tax_amount)

        refund_tax_line = self.tax_line[:]
        for invoice_tax in refund_tax_line:
            invoice_tax.tax_amount = -1 * abs(invoice_tax.tax_amount)

        rect_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FEmitRectificada{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )

        r_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='R',
            rectifying_id=rect_invoice,
            number='FRectEmit{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=rect_tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        b_invoice = Invoice(
            invoice_type='out_refund',
            journal_id=journal,
            rectificative_type='B',
            rectifying_id=rect_invoice,
            number='FAboEmit{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=-1.0 * self.amount_total,
            amount_untaxed=-1.0 * self.amount_untaxed,
            amount_tax=-1.0 * self.amount_tax,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=refund_tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        return r_invoice, b_invoice

    def get_out_refund_invoice_iva5(self, fecha_facturas_recti=None, sii_non_current_tax_rate='R4'):
        journal = Journal(
            name=u'Factura de Energía Rectificativa Emitida'
        )
        base_bruta = 10
        invoice_tax_iva_5 = InvoiceTax(
            name=self.tax_iva_5.name, base=base_bruta,
            tax_amount=base_bruta * self.tax_iva_5.amount, tax_id=self.tax_iva_5
        )
        tax_line = [
            invoice_tax_iva_5
        ]
        n_total_amount = 0
        n_total_tax = 0
        for tl in tax_line:
            n_total_amount += tl.base + tl.tax_amount
            n_total_tax += tl.tax_amount

        n_date_invoice = '2023-01-01'
        n_period = Period(name='01/2023')

        if fecha_facturas_recti:
            b_date_invoice = fecha_facturas_recti
            y,m,d  = fecha_facturas_recti.split('-')
            b_period = Period(name='{}/{}'.format(m,y))
        else:
            b_date_invoice = '2024-10-01'
            b_period = Period(name='01/2024')
        refund_tax_line = tax_line[:]
        for invoice_tax in refund_tax_line:
            invoice_tax.tax_amount = -1 * abs(invoice_tax.tax_amount)

        orig_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FEmitRectificada{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=n_total_amount,
            amount_untaxed=base_bruta,
            amount_tax=n_total_tax,
            period_id=n_period,
            date_invoice=n_date_invoice,
            tax_line=tax_line,
            invoice_line=[], # no se usa
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
            sii_non_current_tax_rate=sii_non_current_tax_rate
        )

        r_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='R',
            rectifying_id=orig_invoice,
            number='FRectEmit{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=n_total_amount,
            amount_untaxed=base_bruta,
            amount_tax=n_total_tax,
            period_id=b_period,
            date_invoice=b_date_invoice,
            tax_line=tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
            sii_non_current_tax_rate = sii_non_current_tax_rate
        )
        b_invoice = Invoice(
            invoice_type='out_refund',
            journal_id=journal,
            rectificative_type='B',
            rectifying_id=orig_invoice,
            number='FEmitRectificada{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=-1 * n_total_amount,
            amount_untaxed=-1 * base_bruta,
            amount_tax=-1 * n_total_tax,
            period_id=b_period,
            date_invoice=b_date_invoice,
            tax_line=refund_tax_line,
            invoice_line=[], # no se usa
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
            sii_non_current_tax_rate=sii_non_current_tax_rate
        )
        return r_invoice, b_invoice

    def get_out_refund_invoice_iva5_multi(self, fecha_facturas_recti=None):
        journal = Journal(
            name=u'Factura de Energía Rectificativa Emitida'
        )
        base_bruta = 10
        invoice_tax_iva_5 = InvoiceTax(
            name=self.tax_iva_5.name, base=base_bruta,
            tax_amount=base_bruta * self.tax_iva_5.amount, tax_id=self.tax_iva_5
        )
        tax_line = [
            invoice_tax_iva_5
        ]
        n_total_amount = 0
        n_total_tax = 0
        for tl in tax_line:
            n_total_amount += tl.base + tl.tax_amount
            n_total_tax += tl.tax_amount

        n_date_invoice = '2023-01-01'
        n_period = Period(name='01/2023')

        if fecha_facturas_recti:
            b_date_invoice = fecha_facturas_recti
            y,m,d  = fecha_facturas_recti.split('-')
            b_period = Period(name='{}/{}'.format(m,y))
        else:
            b_date_invoice = '2024-10-01'
            b_period = Period(name='01/2024')
        refund_tax_line = tax_line[:]
        for invoice_tax in refund_tax_line:
            invoice_tax.tax_amount = -1 * abs(invoice_tax.tax_amount)

        orig_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FEmitRectificada{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=n_total_amount,
            amount_untaxed=base_bruta,
            amount_tax=n_total_tax,
            period_id=n_period,
            date_invoice=n_date_invoice,
            tax_line=tax_line,
            invoice_line=[], # no se usa
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )

        r_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='R',
            rectifying_id=orig_invoice,
            number='FRectEmit{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=n_total_amount,
            amount_untaxed=base_bruta,
            amount_tax=n_total_tax,
            period_id=b_period,
            date_invoice=b_date_invoice,
            tax_line=tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        b_invoice = Invoice(
            invoice_type='out_refund',
            journal_id=journal,
            rectificative_type='B',
            rectifying_id=orig_invoice,
            number='FEmitRectificada{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=-1 * n_total_amount,
            amount_untaxed=-1 * base_bruta,
            amount_tax=-1 * n_total_tax,
            period_id=b_period,
            date_invoice=b_date_invoice,
            tax_line=refund_tax_line,
            invoice_line=[], # no se usa
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        r2_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='R',
            rectifying_id=r_invoice,
            number='FRectEmit{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=n_total_amount,
            amount_untaxed=base_bruta,
            amount_tax=n_total_tax,
            period_id=b_period,
            date_invoice=b_date_invoice,
            tax_line=tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        b2_invoice = Invoice(
            invoice_type='out_refund',
            journal_id=journal,
            rectificative_type='B',
            rectifying_id=r_invoice,
            number='FEmitRectificada{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=-1 * n_total_amount,
            amount_untaxed=-1 * base_bruta,
            amount_tax=-1 * n_total_tax,
            period_id=b_period,
            date_invoice=b_date_invoice,
            tax_line=refund_tax_line,
            invoice_line=[],  # no se usa
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        return r2_invoice, b2_invoice
    def get_out_refund_mulitple_invoice(self, fecha_facturas_recti=None):
        journal = Journal(
            name=u'Factura de Energía Rectificativa Emitida'
        )
        rect_tax_line = self.tax_line[:]
        for invoice_tax in rect_tax_line:
            invoice_tax.tax_amount = -1 * abs(invoice_tax.tax_amount)

        refund_tax_line = self.tax_line[:]
        for invoice_tax in refund_tax_line:
            invoice_tax.tax_amount = -1 * abs(invoice_tax.tax_amount)

        orig_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FEmitRectificada{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            date_invoice='2023-12-07',
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )

        r1_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='R',
            rectifying_id=orig_invoice,
            number='FRectEmit{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            date_invoice='2024-01-07',
            tax_line=rect_tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        b1_invoice = Invoice(
            invoice_type='out_refund',
            journal_id=journal,
            rectificative_type='B',
            rectifying_id=orig_invoice,
            number='FAboEmit{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=-1.0 * self.amount_total,
            amount_untaxed=-1.0 * self.amount_untaxed,
            amount_tax=-1.0 * self.amount_tax,
            period_id=self.period,
            date_invoice='2024-01-07',
            tax_line=refund_tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        r2_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='R',
            rectifying_id=r1_invoice,
            number='FRect2Emit{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            date_invoice='2024-02-07',
            tax_line=rect_tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        b2_invoice = Invoice(
            invoice_type='out_refund',
            journal_id=journal,
            rectificative_type='B',
            rectifying_id=r1_invoice,
            number='FAbo2Emit{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=-1.0 * self.amount_total,
            amount_untaxed=-1.0 * self.amount_untaxed,
            amount_tax=-1.0 * self.amount_tax,
            period_id=self.period,
            date_invoice='2024-02-07',
            tax_line=refund_tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        return r2_invoice, b2_invoice

    def get_out_invoice_RA(self):
        journal = Journal(
            name=u'Factura de Energía Emitida'
        )

        rect_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FEmitRectificada{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )

        invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='RA',
            rectifying_id=rect_invoice,
            number='FEmitSinAnuladora{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )

        return invoice

    def get_in_invoice_RA(self):
        journal = Journal(
            name=u'Factura de Energía Rectificativa Recibida',
            article=self.article
        )

        tax_line = self.tax_line
        for invoice_tax in tax_line:
            invoice_tax.tax_amount = -1 * abs(invoice_tax.tax_amount)

        rect_invoice = Invoice(
            invoice_type='in_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FRecibRectificada{}'.format(self.invoice_number),
            origin='FRectRecibRectificadaOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )

        invoice = Invoice(
            invoice_type='in_invoice',
            journal_id=journal,
            rectificative_type='RA',
            rectifying_id=rect_invoice,
            number='FRectRecib{}'.format(self.invoice_number),
            origin='FRectRecibOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )
        return invoice

    def get_in_invoice_RA_N_negative(self):
        journal = Journal(
            name=u'Factura de Energía Rectificativa Recibida',
            article=self.article
        )
        tax_iva_21 = Tax(name='21% IVA Soportado', amount=0.21, type='percent')
        amount_total_n = -6.21
        amount_tax_n = -1.08
        base_amount_n = -5.13
        tax_line_n = [
            InvoiceTax(
                name='21% IVA Soportado', base=-5.13,
                tax_amount=-1.08, tax_id=tax_iva_21
            )
        ]
        amount_total_ra = 14.65
        amount_tax_ra = 2.54
        base_amount_ra = 12.11
        tax_line_ra = [
            InvoiceTax(
                name='21% IVA Soportado', base=-5.13,
                tax_amount=-1.08, tax_id=tax_iva_21
            )
        ]

        rect_invoice = Invoice(
            invoice_type='in_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FRecibRectificada{}'.format(self.invoice_number),
            origin='FRectRecibRectificadaOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=amount_total_n,
            amount_untaxed=base_amount_n,
            amount_tax=amount_tax_n,
            period_id=self.period,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=tax_line_n,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )

        invoice = Invoice(
            invoice_type='in_invoice',
            journal_id=journal,
            rectificative_type='RA',
            rectifying_id=rect_invoice,
            number='FRectRecib{}'.format(self.invoice_number),
            origin='FRectRecibOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=amount_total_ra,
            amount_untaxed=base_amount_ra,
            amount_tax=amount_tax_ra,
            period_id=self.period,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=tax_line_ra,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )
        return invoice

    def get_out_invoice_rescision(self):
        journal = Journal(
            name=u'Factura de Energía Rectificativa Rescision Emitida',
            article=self.article
        )

        tax_line = self.tax_line
        for invoice_tax in tax_line:
            invoice_tax.tax_amount = -1 * abs(invoice_tax.tax_amount)

        rect_invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FEmitRectificada{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )

        invoice = Invoice(
            invoice_type='out_refund',
            journal_id=journal,
            rectificative_type='A',
            rectifying_id=rect_invoice,
            number='FRectEmit{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        return invoice
      
    def get_out_invoice_with_irfp(self):
        journal = Journal(
            name=u'Factura de Energía Recibida'
        )

        tax_iva_irpf_19 = Tax(
            name='Retenciones a cuenta IRPF 19%',
            amount=-0.19, type='percent'
        )
        tax_iva_soportado_21 = Tax(
            name='21% IVA repercutido',
            amount=0.21, type='percent'
        )
        invoice_lines = [
            InvoiceLine(
                price_subtotal=1500.28,
                invoice_line_tax_id=[tax_iva_irpf_19, tax_iva_soportado_21])
        ]
        base_iva_irfp = sum(
            [line.price_subtotal
             for line in invoice_lines]
        )
        invoice_tax_iva_soportado_21 = InvoiceTax(
            name=tax_iva_soportado_21.name, base=base_iva_irfp,
            tax_amount=315.06,
            tax_id=tax_iva_soportado_21
        )
        tax_iva_irpf_19 = InvoiceTax(
            name=tax_iva_irpf_19.name, base=base_iva_irfp,
            tax_amount=-285.05,
            tax_id=tax_iva_irpf_19
        )
        tax_lines = [
            tax_iva_irpf_19, invoice_tax_iva_soportado_21
        ]

        invoice = Invoice(
                invoice_type='out_invoice',
                journal_id=journal,
                rectificative_type='N',
                rectifying_id=False,
                number='FEmit{}'.format(self.invoice_number),
                partner_id=self.partner_invoice,
                fiscal_name=self.fiscal_name,
                fiscal_vat=self.fiscal_vat,
                address_contact_id=self.address_contact_id,
                company_id=self.company,
                amount_total=1530.29,
                amount_untaxed=1500.28,
                amount_tax=30.01,
                period_id=self.period,
                date_invoice=self.date_invoice,
                tax_line=tax_lines,
                invoice_line=invoice_lines,
                sii_registered=self.sii_registered,
                fiscal_position=self.fiscal_position_general,
                sii_description=self.sii_description,
                sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
            )
        return invoice

    def get_out_invoice_with_irfp_and_without_iva(self):
        journal = Journal(
            name=u'Factura de Energía emitida'
        )

        tax_iva_irpf_19 = Tax(
            name='Retenciones a cuenta IRPF 19%',
            amount=-0.19, type='percent'
        )
        invoice_line = [
            InvoiceLine(
                price_subtotal=1255.02,
                invoice_line_tax_id=[tax_iva_irpf_19])
        ]
        base_irfp = 1255.02
        tax_iva_irpf_19 = InvoiceTax(
            name=tax_iva_irpf_19.name, base=base_irfp,
            tax_amount=-238.45,
            tax_id=tax_iva_irpf_19
        )
        tax_line_inversion_sujeto_pasivo = [
            tax_iva_irpf_19
        ]
        tax_lines = tax_line_inversion_sujeto_pasivo
        invoice_lines = invoice_line

        invoice = Invoice(
                invoice_type='out_invoice',
                journal_id=journal,
                rectificative_type='N',
                rectifying_id=False,
                number='FEmit{}'.format(self.invoice_number),
                partner_id=self.partner_invoice,
                fiscal_name=self.fiscal_name,
                fiscal_vat=self.fiscal_vat,
                address_contact_id=self.address_contact_id,
                company_id=self.company,
                amount_total=1016.57,
                amount_untaxed=1255.02,
                amount_tax=-238.45,
                period_id=self.period,
                date_invoice=self.date_invoice,
                tax_line=tax_lines,
                invoice_line=invoice_lines,
                sii_registered=self.sii_registered,
                fiscal_position=self.fiscal_position_general,
                sii_description=self.sii_description,
                sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
            )
        return invoice

    def get_in_invoice_with_irfp(self):
        journal = Journal(
            name=u'Factura de Energía Emitida'
        )

        tax_iva_irpf_19 = Tax(
            name='Retenciones IRPF 19%',
            amount=-0.19, type='percent'
        )
        tax_iva_soportado_21 = Tax(
            name='21% IVA Soportado (operaciones corrientes)',
            amount=0.21, type='percent'
        )
        invoice_line = [
            InvoiceLine(
                price_subtotal=2400.0,
                invoice_line_tax_id=[tax_iva_irpf_19, tax_iva_soportado_21])
        ]
        base_iva_irfp = sum(
            [line.price_subtotal
             for line in invoice_line]
        )
        invoice_tax_iva_isp_soportado_21 = InvoiceTax(
            name=tax_iva_soportado_21.name, base=base_iva_irfp,
            tax_amount=504.0,
            tax_id=tax_iva_soportado_21
        )
        tax_iva_irpf_19 = InvoiceTax(
            name=tax_iva_irpf_19.name, base=base_iva_irfp,
            tax_amount=-456.0,
            tax_id=tax_iva_irpf_19
        )
        tax_line_inversion_sujeto_pasivo = [
            tax_iva_irpf_19, invoice_tax_iva_isp_soportado_21
        ]
        tax_lines = tax_line_inversion_sujeto_pasivo
        invoice_lines = invoice_line

        invoice = Invoice(
            invoice_type='in_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number='FRecib{}'.format(self.invoice_number),
            origin='FRecibOrigen{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            address_contact_id=self.address_contact_id,
            company_id=self.company,
            amount_total=self.amount_total,
            amount_untaxed=self.amount_untaxed,
            amount_tax=self.amount_tax,
            period_id=self.period,
            origin_date_invoice=self.origin_date_invoice,
            date_invoice=self.date_invoice,
            tax_line=tax_lines,
            invoice_line=invoice_lines,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_in_clave_regimen_especial=self.sii_in_clave_regimen_especial,
        )
        return invoice

    def get_out_invoice_partner_id_type_05(self, with_fiscal_info=True):
        journal = Journal(
            name=u'Factura de Energía Emitida'
        )
        spain = Country(code='ES', is_eu_member=False)
        partner = Partner(
            name=os.environ.get('NOMBRE_CONTRAPARTE', u'Francisco García'),
            nif=os.environ.get('NIF_CONTRAPARTE', u'ES12345678Z'),
            country=spain, aeat_registered=True, auto_vat_type='05'
        )
        if with_fiscal_info:
            invoice = Invoice(
                invoice_type='out_invoice',
                journal_id=journal,
                rectificative_type='N',
                rectifying_id=False,
                number='FEmit{}'.format(self.invoice_number),
                partner_id=partner,
                fiscal_name=self.fiscal_name,
                fiscal_vat=self.fiscal_vat,
                address_contact_id=self.address_contact_id,
                company_id=self.company,
                amount_total=self.amount_total,
                amount_untaxed=self.amount_untaxed,
                amount_tax=self.amount_tax,
                period_id=self.period,
                date_invoice=self.date_invoice,
                tax_line=self.tax_line,
                invoice_line=self.invoice_line,
                sii_registered=self.sii_registered,
                fiscal_position=self.fiscal_position,
                sii_description=self.sii_description,
                sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
            )
        else:
            invoice = Invoice(
                invoice_type='out_invoice',
                journal_id=journal,
                rectificative_type='N',
                rectifying_id=False,
                number='FEmit{}'.format(self.invoice_number),
                partner_id=partner,
                address_contact_id=self.address_contact_id,
                company_id=self.company,
                amount_total=self.amount_total,
                amount_untaxed=self.amount_untaxed,
                amount_tax=self.amount_tax,
                period_id=self.period,
                date_invoice=self.date_invoice,
                tax_line=self.tax_line,
                invoice_line=self.invoice_line,
                sii_registered=self.sii_registered,
                fiscal_position=self.fiscal_position,
                sii_description=self.sii_description,
                sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
            )
        return invoice
