# -*- coding: utf-8 -*-
"""
Generador de dades de test per l'ATC (IGIC)

Aquest mòdul proporciona dades de test per factures amb IGIC
per utilitzar en els tests amb Mamba.
"""

import os
import random
from sii.models.basic_models import *


class DataGeneratorATC:
    """
    Generador de dades per tests ATC
    
    Similar a DataGenerator però amb impostos IGIC en lloc d'IVA
    """
    
    def __init__(self, invoice_registered=False, contraparte_registered=True):
        self.sii_registered = invoice_registered
        self.period = Period(name='12/2016')
        
        # Impostos IGIC - 7 tipus disponibles
        name_igic_0 = 'IGIC 0%'
        name_igic_3 = 'IGIC 3%'
        name_igic_7 = 'IGIC 7%'
        name_igic_95 = 'IGIC 9,5%'
        name_igic_135 = 'IGIC 13,5%'
        name_igic_15 = 'IGIC 15%'
        name_igic_20 = 'IGIC 20%'
        name_igic_exento = 'IGIC Exento'
        
        # Altres impostos
        name_aiem = 'AIEM 15%'  # Arbitrio sobre Importaciones y Entregas de Mercancías
        
        # Crear objectes Tax
        tax_igic_0 = Tax(name=name_igic_0, amount=0.0, type='percent')
        tax_igic_3 = Tax(name=name_igic_3, amount=0.03, type='percent')
        tax_igic_7 = Tax(name=name_igic_7, amount=0.07, type='percent')
        tax_igic_95 = Tax(name=name_igic_95, amount=0.095, type='percent')
        tax_igic_135 = Tax(name=name_igic_135, amount=0.135, type='percent')
        tax_igic_15 = Tax(name=name_igic_15, amount=0.15, type='percent')
        tax_igic_20 = Tax(name=name_igic_20, amount=0.20, type='percent')
        tax_igic_exento = Tax(name=name_igic_exento, amount=0, type='percent')
        tax_aiem = Tax(name=name_aiem, amount=0.15, type='percent')
        
        # Línies de factura amb diferents tipus d'IGIC
        self.invoice_line = [
            InvoiceLine(price_subtotal=100, invoice_line_tax_id=[tax_igic_135]),  # Tipus general
            InvoiceLine(
                price_subtotal=200, invoice_line_tax_id=[tax_igic_135, tax_aiem]
            ),  # Amb AIEM
            InvoiceLine(price_subtotal=400, invoice_line_tax_id=[tax_igic_7]),  # Tipus reduït
            InvoiceLine(price_subtotal=800, invoice_line_tax_id=[tax_aiem]),  # Només AIEM
            InvoiceLine(
                price_subtotal=1600, invoice_line_tax_id=[tax_igic_exento]
            ),  # Exempt
            InvoiceLine(price_subtotal=3200, invoice_line_tax_id=[])  # Sense impost
        ]
        
        # Calcular bases per cada tipus d'IGIC
        base_igic_135 = sum(
            [line.price_subtotal
             for line in self.invoice_line
             if tax_igic_135 in line.invoice_line_tax_id]
        )
        base_igic_7 = sum(
            [line.price_subtotal
             for line in self.invoice_line
             if tax_igic_7 in line.invoice_line_tax_id]
        )
        base_aiem = sum(
            [line.price_subtotal
             for line in self.invoice_line
             if tax_aiem in line.invoice_line_tax_id]
        )
        base_igic_exento = sum(
            [line.price_subtotal
             for line in self.invoice_line
             if tax_igic_exento in line.invoice_line_tax_id]
        )
        
        # Crear línies de tax amb càlculs
        invoice_tax_igic_135 = InvoiceTax(
            name=name_igic_135, base=base_igic_135,
            tax_amount=base_igic_135 * tax_igic_135.amount, tax_id=tax_igic_135
        )
        invoice_tax_igic_7 = InvoiceTax(
            name=name_igic_7, base=base_igic_7,
            tax_amount=base_igic_7 * tax_igic_7.amount, tax_id=tax_igic_7
        )
        invoice_tax_aiem = InvoiceTax(
            name=name_aiem, base=base_aiem,
            tax_amount=base_aiem * tax_aiem.amount, tax_id=tax_aiem
        )
        invoice_tax_igic_exento = InvoiceTax(
            name=name_igic_exento, base=base_igic_exento,
            tax_amount=base_igic_exento * tax_igic_exento.amount,
            tax_id=tax_igic_exento
        )
        
        self.tax_line = [
            invoice_tax_igic_135, invoice_tax_igic_7, invoice_tax_aiem,
            invoice_tax_igic_exento
        ]
        
        # Partners (mateix format que AEAT)
        spain = Country(code='ES')
        self.partner_invoice = Partner(
            name=os.environ.get('NOMBRE_CONTRAPARTE_ATC', u'Juan Pérez García'),
            nif=os.environ.get('NIF_CONTRAPARTE_ATC', u'ES87654321A'),
            country=spain, aeat_registered=contraparte_registered
        )
        partner_company = Partner(
            name=os.environ.get('NOMBRE_TITULAR_ATC', u'Distribuidora Canaria S.L.'),
            nif=os.environ.get('NIF_TITULAR_ATC', 'ES11111111B'), country=spain
        )
        self.company = Company(partner_id=partner_company)
        
        # Adreça a Canàries
        comunidad_autonoma = ComunidadAutonoma(code='05', name='Canarias')  # Codi Canàries
        provincia = State(comunidad_autonoma=comunidad_autonoma)
        self.address_contact_id = ResPartnerAddress(state=provincia)
        
        # Dades factura
        self.invoice_number = 'ATC' + str(random.randrange(0, 100000)).zfill(5)
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
    
    def get_out_invoice(self):
        """Genera una factura emesa (out_invoice) amb IGIC"""
        journal = Journal(name=u'Factura de Energía Emitida')
        
        invoice = Invoice(
            invoice_type='out_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number=self.invoice_number,
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
            sii_description=u'Factura con IGIC',
            sii_out_clave_regimen_especial='08'
        )
        return invoice
    
    def get_in_invoice(self):
        """Genera una factura rebuda (in_invoice) amb IGIC"""
        journal = Journal(name=u'Factura de Energía Recibida')
        
        invoice = Invoice(
            invoice_type='in_invoice',
            journal_id=journal,
            rectificative_type='N',
            rectifying_id=False,
            number=self.invoice_number,
            origin='PROV' + self.invoice_number,
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
            sii_description=u'Factura recibida con IGIC',
            sii_in_clave_regimen_especial='08'
        )
        return invoice
    
    def get_out_refund(self):
        """Genera una factura rectificativa emesa (out_refund) amb IGIC"""
        journal = Journal(name=u'Abono de Energía Emitida')
        
        invoice = Invoice(
            invoice_type='out_refund',
            journal_id=journal,
            rectificative_type='I',
            rectifying_id=False,
            number='R' + self.invoice_number,
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
            sii_description=u'Factura rectificativa con IGIC',
            sii_out_clave_regimen_especial='08'
        )
        return invoice
    
    def get_in_refund(self):
        """Genera una factura rectificativa rebuda (in_refund) amb IGIC"""
        journal = Journal(name=u'Abono de Energía Recibida')
        
        invoice = Invoice(
            invoice_type='in_refund',
            journal_id=journal,
            rectificative_type='I',
            rectifying_id=False,
            number='R' + self.invoice_number,
            origin='RPROV' + self.invoice_number,
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
            sii_description=u'Abono recibido con IGIC',
            sii_in_clave_regimen_especial='08'
        )
        return invoice
