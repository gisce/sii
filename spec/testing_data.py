# -*- coding: utf-8 -*-


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


class FiscalPosition:
    def __init__(self, cre_in_invoice, cre_out_invoice):
        self.sii_in_clave_regimen_especial = cre_in_invoice
        self.sii_out_clave_regimen_especial = cre_out_invoice


class Tax:
    def __init__(self, amount):
        self.amount = amount


class InvoiceLineTaxes:
    def __init__(self, name, base, tax_amount, tax_id):
        self.name = name
        self.base = base  # base imponible
        self.tax_amount = tax_amount
        self.tax_id = tax_id


class Invoice:

    def __init__(self, description, number, type, partner_id, company_id,
                 amount_total, period_id, date_invoice, tax_line, sii_sent,
                 rectificative_type, fiscal_position):
        self.name = description
        self.number = number
        self.type = type
        self.partner_id = partner_id
        self.company_id = company_id
        self.period_id = period_id
        self.amount_total = amount_total
        self.date_invoice = date_invoice
        self.tax_line = tax_line
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
        self.period = Period(name='03/2016')
        tax_ibi = Tax(amount=0.15)
        tax_iva_21 = Tax(amount=0.21)
        tax_iva_4 = Tax(amount=0.04)
        self.tax_line = [
            InvoiceLineTaxes(
                name='IVA 21%', base=1000, tax_amount=210, tax_id=tax_iva_21
            ),
            InvoiceLineTaxes(
                name='IVA 4%', base=1000, tax_amount=40, tax_id=tax_iva_4
            ),
            InvoiceLineTaxes(
                name='IBI 15%', base=1000, tax_amount=150, tax_id=tax_ibi
            )
        ]
        self.partner_invoice = Partner(
            name=unicode('Francisco García', 'utf-8'), nif='12345678T'
        )
        partner_company = Partner(
            name=unicode('Compañía Eléctrica S.A.', 'utf-8'), nif='55555555T'
        )
        self.company = Company(partner_id=partner_company)

        self.invoice_number = 'F012345'
        self.date_invoice = '2016-12-31'
        self.amount_total = 15
        cre_in_invoice = '01'
        cre_out_invoice = '01'
        self.fiscal_position = FiscalPosition(
            cre_in_invoice=cre_in_invoice, cre_out_invoice=cre_out_invoice
        )

    def get_in_invoice(self):
        invoice = Invoice(
            type='in_invoice',
            description='Factura recibida',
            rectificative_type='N',
            number=self.invoice_number,
            partner_id=self.partner_invoice,
            company_id=self.company,
            amount_total=self.amount_total,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            sii_sent=self.sii_sent,
            fiscal_position=self.fiscal_position
        )
        return invoice

    def get_out_invoice(self):
        invoice = Invoice(
            type='out_invoice',
            description='Factura emitida',
            rectificative_type='N',
            number=self.invoice_number,
            partner_id=self.partner_invoice,
            company_id=self.company,
            amount_total=self.amount_total,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            sii_sent=self.sii_sent,
            fiscal_position=self.fiscal_position
        )
        return invoice

    def get_in_refund_invoice(self):
        invoice = Invoice(
            type='in_refund',
            description='Factura rectificativa recibida',
            rectificative_type='R',
            number=self.invoice_number,
            partner_id=self.partner_invoice,
            company_id=self.company,
            amount_total=self.amount_total,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            sii_sent=self.sii_sent,
            fiscal_position=self.fiscal_position
        )
        return invoice

    def get_out_refund_invoice(self):
        invoice = Invoice(
            type='out_refund',
            description='Factura rectificativa emitida',
            rectificative_type='R',
            number=self.invoice_number,
            partner_id=self.partner_invoice,
            company_id=self.company,
            amount_total=self.amount_total,
            period_id=self.period,
            date_invoice=self.date_invoice,
            tax_line=self.tax_line,
            sii_sent=self.sii_sent,
            fiscal_position=self.fiscal_position
        )
        return invoice
