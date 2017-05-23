# -*- coding: utf-8 -*-

import os
import random


class Period:
    def __init__(self, name):
        self.name = name


class Company:
    def __init__(self, partner_id):
        self.partner_id = partner_id


class Partner:
    def __init__(self, name, nif):
        self.name = name
        self.vat = nif


class Journal:
    def __init__(self, name):
        self.name = name


class FiscalPosition:
    def __init__(self, name, cre_in_invoice, cre_out_invoice):
        self.name = name
        self.sii_in_clave_regimen_especial = cre_in_invoice
        self.sii_out_clave_regimen_especial = cre_out_invoice


class Tax:
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount


class InvoiceTax:
    def __init__(self, name, base, tax_amount, tax_id):
        self.name = name
        self.base = base  # base imponible
        self.tax_amount = tax_amount
        self.tax_id = tax_id


class InvoiceLine:
    def __init__(self, price_subtotal, invoice_line_tax_id):
        self.price_subtotal = price_subtotal
        self.invoice_line_tax_id = invoice_line_tax_id


class Invoice:
    def __init__(self, journal_id, number, type, partner_id, company_id,
                 amount_total, period_id, date_invoice, tax_line, sii_sent,
                 rectificative_type, fiscal_position, invoice_line):
        self.journal_id = journal_id
        self.number = number
        self.type = type
        self.partner_id = partner_id
        self.company_id = company_id
        self.period_id = period_id
        self.amount_total = amount_total
        self.date_invoice = date_invoice
        self.tax_line = tax_line
        self.invoice_line = invoice_line
        self.fiscal_position = fiscal_position
        self.sii_sent = sii_sent
        self.rectificative_type = rectificative_type
        # RECTIFICATIVE_TYPE_SELECTION = [
        #     ('N', 'Normal'),
        #     ('R', 'Rectificative'),
        #     ('A', 'Nullifier'),
        #     ('B', 'Nullifier with substitution')
        # ]


class DataGenerator:
    def __init__(self):
        self.sii_sent = False
        self.period = Period(name='12/2016')
        name_iva_21 = 'IVA 21%'
        name_iva_4 = 'IVA 4%'
        name_ibi = 'IBI 15%'
        tax_ibi = Tax(name=name_ibi, amount=0.15)
        tax_iva_21 = Tax(name=name_iva_21, amount=0.21)
        tax_iva_4 = Tax(name=name_iva_21, amount=0.04)
        self.invoice_line = [
            InvoiceLine(price_subtotal=100, invoice_line_tax_id=[tax_iva_21]),
            InvoiceLine(price_subtotal=200,
                        invoice_line_tax_id=[tax_iva_21, tax_ibi]),
            InvoiceLine(price_subtotal=400, invoice_line_tax_id=[tax_iva_4]),
            InvoiceLine(price_subtotal=800, invoice_line_tax_id=[tax_ibi])
        ]

        base_iva_21 = sum(
            [line.price_subtotal
             for line in self.invoice_line
             if tax_iva_21.amount
             in [tax.amount for tax in line.invoice_line_tax_id]]
        )
        base_iva_4 = sum(
            [line.price_subtotal
             for line in self.invoice_line
             if tax_iva_4.amount
             in [tax.amount for tax in line.invoice_line_tax_id]]
        )
        base_ibi = sum(
            [line.price_subtotal
             for line in self.invoice_line
             if tax_ibi.amount
             in [tax.amount for tax in line.invoice_line_tax_id]]
        )
        invoice_tax_iva_21 = InvoiceTax(  # TODO les tax_line són una per cada tipus d'impost repetit i suma
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
        self.tax_line = [invoice_tax_iva_21, invoice_tax_iva_4, invoice_tax_ibi]  # No hi ha impostos repetits

        self.partner_invoice = Partner(
            name=os.environ.get('NOMBRE_TITULAR', u'Francisco García'),
            nif=os.environ.get('NIF_TITULAR', u'12345678T')
        )
        partner_company = Partner(
            name=os.environ.get(
                'NOMBRE_CONTRAPARTE', u'Compañía Eléctrica S.A.'
            ),
            nif=os.environ.get('NIF_CONTRAPARTE', '55555555T')
        )
        self.company = Company(partner_id=partner_company)

        self.invoice_number = str(random.randrange(0, 100000)).zfill(5)
        self.date_invoice = '2016-12-31'
        taxes_amount = sum([tax.tax_amount for tax in self.tax_line])
        base_amount = sum([line.price_subtotal for line in self.invoice_line])
        self.amount_total = taxes_amount + base_amount
        cre_in_invoice = '01'
        cre_out_invoice = '01'
        self.fiscal_position = FiscalPosition(
            name=u'Régimen Islas Canarias', cre_in_invoice=cre_in_invoice,
            cre_out_invoice=cre_out_invoice
        )

    def get_in_invoice(self):
        journal = Journal(name='Factura de Energía Recibida')

        invoice = Invoice(
            type='in_invoice',
            journal_id=journal,
            rectificative_type='N',
            number='FRecib}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            company_id=self.company,
            amount_total=self.amount_total,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_sent=self.sii_sent,
            fiscal_position=self.fiscal_position
        )
        return invoice

    def get_out_invoice(self):
        journal = Journal(name='Factura de Energía Emitida')

        invoice = Invoice(
            type='out_invoice',
            journal_id=journal,
            rectificative_type='N',
            number='FEmit}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            company_id=self.company,
            amount_total=self.amount_total,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_sent=self.sii_sent,
            fiscal_position=self.fiscal_position
        )
        return invoice

    def get_in_refund_invoice(self):
        journal = Journal(name='Factura de Energía Rectificativa Recibida')

        invoice = Invoice(
            type='in_refund',
            journal_id=journal,
            rectificative_type='R',
            number='FRectRecib}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            company_id=self.company,
            amount_total=self.amount_total,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_sent=self.sii_sent,
            fiscal_position=self.fiscal_position
        )
        return invoice

    def get_out_refund_invoice(self):
        journal = Journal(name='Factura de Energía Rectificativa Emitida')

        invoice = Invoice(
            type='out_refund',
            journal_id=journal,
            rectificative_type='R',
            number='FRectEmit{}'.format(self.invoice_number),
            partner_id=self.partner_invoice,
            company_id=self.company,
            amount_total=self.amount_total,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            invoice_line=self.invoice_line,
            sii_sent=self.sii_sent,
            fiscal_position=self.fiscal_position
        )
        return invoice
