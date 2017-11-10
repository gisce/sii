# -*- coding: utf-8 -*-
from sii.utils import VAT


class Period:
    def __init__(self, name):
        self.name = name


class Company:
    def __init__(self, partner_id):
        self.partner_id = partner_id


class Country:
    def __init__(self, code):
        self.code = code


class ComunidadAutonoma:
    def __init__(self, code, name):
        self.codi = code
        self.name = name


class State:
    def __init__(self, comunidad_autonoma):
        self.comunitat_autonoma = comunidad_autonoma


class ResPartnerAddress:
    def __init__(self, state, ref_catastral=False):
        self.state_id = state
        self.ref_catastral = ref_catastral


class Partner:
    def __init__(self, name, nif, country, aeat_registered=True):
        self.name = name
        self.vat = nif
        self.country_id = country
        self.aeat_registered = aeat_registered

    def sii_get_vat_type(self):
        return VAT.sii_get_vat_type(self.vat)


class Journal:
    def __init__(self, name):
        self.name = name


class FiscalPosition:
    def __init__(self, name):
        self.name = name


class Tax:
    def __init__(self, name, amount, type):
        self.name = name
        self.amount = amount
        self.type = type


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
    def __init__(self,
                 journal_id,
                 number,
                 invoice_type,
                 partner_id,
                 address_contact_id,
                 company_id,
                 amount_total,
                 amount_untaxed,
                 amount_tax,
                 period_id,
                 date_invoice,
                 tax_line,
                 sii_registered,
                 rectificative_type,
                 fiscal_position,
                 invoice_line,
                 sii_description,
                 rectifying_id=False,
                 sii_in_clave_regimen_especial=None,
                 sii_out_clave_regimen_especial=None,
                 origin_date_invoice=None,
                 origin=None):
        self.journal_id = journal_id
        self.number = number
        self.type = invoice_type
        self.partner_id = partner_id
        self.address_contact_id = address_contact_id
        self.company_id = company_id
        self.period_id = period_id
        self.amount_total = amount_total
        self.amount_untaxed = amount_untaxed
        self.amount_tax = amount_tax
        self.origin_date_invoice = origin_date_invoice
        self.date_invoice = date_invoice
        self.tax_line = tax_line
        self.invoice_line = invoice_line
        self.fiscal_position = fiscal_position
        self.sii_registered = sii_registered
        self.origin = origin
        self.sii_description = sii_description
        self.sii_in_clave_regimen_especial = sii_in_clave_regimen_especial
        self.sii_out_clave_regimen_especial = sii_out_clave_regimen_especial
        self.rectificative_type = rectificative_type
        self.rectifying_id = rectifying_id
