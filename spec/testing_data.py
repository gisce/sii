# -*- coding: utf-8 -*-

import os
import random
from decimal import Decimal
from sii.models.basic_models import *


class DataGenerator:
    def __init__(self, invoice_registered=False, contraparte_registered=True):
        self.sii_registered = invoice_registered
        self.period = Period(name='12/2016')
        name_iva_21 = 'IVA 21%'
        name_iva_4 = 'IVA 4%'
        name_ibi = 'IBI 15%'
        name_iva_exento = 'IVA Exento'
        tax_ibi = Tax(name=name_ibi, amount=0.15, type='percent')
        tax_iva_21 = Tax(name=name_iva_21, amount=0.21, type='percent')
        tax_iva_4 = Tax(name=name_iva_21, amount=0.04, type='percent')
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
            tax_line=tax_line,
            invoice_line=self.invoice_line,
            sii_registered=self.sii_registered,
            fiscal_position=self.fiscal_position,
            sii_description=self.sii_description,
            sii_out_clave_regimen_especial=self.sii_out_clave_regimen_especial,
        )
        return invoice

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