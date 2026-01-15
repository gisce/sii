# coding=utf-8
"""
Generador d'objectes XML per al SII de l'Agència Tributària Canària (ATC)

Aquest mòdul adapta les funcions del SII AEAT per treballar amb IGIC
en lloc d'IVA, mantenint la mateixa estructura i lògica.
"""
import re
from decimal import Decimal, localcontext
from datetime import date

from sii.atc import __ATC_SII_VERSION__
from sii.atc.models import invoices_record
from sii.utils import unidecode_str, VAT

# Signes de les factures segons el tipus
SIGN = {'N': 1, 'R': 1, 'A': -1, 'B': -1, 'RA': 1, 'C': 1, 'G': 1}


def is_inversion_sujeto_pasivo(tax_name):
    """
    Detecta si un impost és d'inversió del subjecte passiu
    """
    regex_isp = r'inv.*sujeto pasivo'
    return bool(re.search(regex_isp, unidecode_str(tax_name).lower()))


def get_invoice_sign(invoice):
    """
    Retorna el signe de la factura segons el tipus
    """
    if invoice.type.endswith('refund'):
        return -1
    return 1


def get_igic_values(invoice, in_invoice, is_export=False, is_import=False):
    """
    Obté els valors d'IGIC d'una factura (equivalent a get_iva_values per AEAT)
    
    DIFERÈNCIA CLAU: Aquesta funció busca 'igic' en lloc de 'iva' en els noms
    dels impostos, i genera estructura DesgloseIGIC en lloc de DesgloseIVA.
    
    :param invoice: Factura d'OpenERP
    :param in_invoice: Indica si és una factura rebuda
    :type in_invoice: bool
    :param is_export: Indica si és una exportació
    :type is_export: bool
    :param is_import: Indica si és una importació
    :type is_import: bool
    :return: Diccionari amb els valors d'IGIC
    """
    vals = {
        'sujeta_a_igic': False,
        'detalle_igic': [],
        'no_sujeta_a_igic': False,
        'igic_exento': False,
        'igic_no_exento': False,
        'detalle_igic_exento': {'BaseImponible': 0},
        'importe_no_sujeto': 0,
        'inversion_sujeto_pasivo': []
    }
    
    # igic_values agrupa els valors de l'IGIC per tipus impositiu
    # Estructura: {13.5: {'BaseImponible': ..., 'TipoImpositivo': ..., 'Cuota...': ...}}
    igic_values = {}
    
    sign = get_invoice_sign(invoice)
    invoice_total = sign * invoice.amount_total
    
    for inv_tax in invoice.tax_line:
        # CANVI CLAU: Busquem 'igic' en lloc de 'iva'
        if 'igic' in inv_tax.name.lower():
            vals['sujeta_a_igic'] = True
            
            base_igic = inv_tax.base
            base_imponible = sign * base_igic
            cuota = inv_tax.tax_amount
            tipo_impositivo_unitario = inv_tax.tax_id.amount
            tipo_impositivo = tipo_impositivo_unitario * 100
            
            invoice_total -= (base_imponible + cuota)
            
            tax_type = inv_tax.tax_id.type
            is_igic_exento = (
                tipo_impositivo_unitario == 0 and tax_type == 'percent'
            )
            
            if is_inversion_sujeto_pasivo(inv_tax.name):
                new_value = {
                    'BaseImponible': base_imponible,
                    'TipoImpositivo': tipo_impositivo,
                    'CuotaRepercutida': cuota
                }
                vals['inversion_sujeto_pasivo'].append(new_value)
            # IGIC 0% Exportacions i IGIC 0% Importacions tenen amount 0
            elif not is_export and not is_import and is_igic_exento:
                vals['igic_exento'] = True
                vals['detalle_igic_exento']['BaseImponible'] += inv_tax.base
            else:
                if in_invoice:
                    cuota_key = 'CuotaSoportada'
                else:
                    cuota_key = 'CuotaRepercutida'
                
                if tipo_impositivo in igic_values:
                    aux = igic_values[tipo_impositivo]
                    aux['BaseImponible'] += base_imponible
                    aux[cuota_key] += cuota
                else:
                    igic = {
                        'BaseImponible': base_imponible,
                        'TipoImpositivo': tipo_impositivo,
                        cuota_key: cuota
                    }
                    igic_values[tipo_impositivo] = igic
                vals['igic_no_exento'] = True
    
    vals['detalle_igic'] = list(igic_values.values())
    
    invoice_total = round(invoice_total, 2)
    if invoice_total != 0:
        vals['no_sujeta_a_igic'] = True
        vals['importe_no_sujeto'] = invoice_total
        if in_invoice:
            new_value = {
                'BaseImponible': vals['importe_no_sujeto'],
                'TipoImpositivo': 0,
                'CuotaSoportada': 0
            }
            vals['detalle_igic'].append(new_value)
    
    return vals


def get_partner_info(partner, in_invoice, nombre_razon=False):
    """
    Obté la informació del partner (igual que per AEAT)
    """
    vat_type = partner.sii_get_vat_type()
    contraparte = {}
    
    if nombre_razon:
        contraparte['NombreRazon'] = unidecode_str(partner.name)
    
    partner_country = partner.country_id or partner.country
    
    if vat_type == '02':
        if not partner.aeat_registered and not in_invoice:
            contraparte['IDOtro'] = {
                'CodigoPais': partner_country.code,
                'IDType': '07',
                'ID': VAT.clean_vat(partner.vat)
            }
        else:
            contraparte['NIF'] = VAT.clean_vat(partner.vat)
    else:
        contraparte['IDOtro'] = {
            'CodigoPais': partner_country.code if partner_country else 'ES',
            'IDType': vat_type,
            'ID': VAT.clean_vat(partner.vat) if partner.vat else partner.name[:40]
        }
    
    return contraparte


class SIIATC(object):
    """
    Generador d'objectes XML per al SII ATC
    
    Equivalent a la classe SII per AEAT, però adaptat per treballar amb IGIC
    i els endpoints de l'Agència Tributària Canària.
    """
    
    def __init__(self, invoice, sign_policy=None):
        """
        Inicialitza l'objecte SIIATC
        
        :param invoice: Factura d'OpenERP
        :param sign_policy: Política de signatura (opcional, per futur)
        """
        self.invoice = invoice
        self.sign_policy = sign_policy
    
    def generate_object(self):
        """
        Genera l'objecte complet per enviar al SII ATC
        
        Aquest mètode adapta la generació de l'objecte per utilitzar
        IGIC en lloc d'IVA, canviant:
        - Les referències a 'IVA' per 'IGIC'
        - L'estructura XML (DesgloseIGIC vs DesgloseIVA)
        - Els valors dels impostos (segons constants IGIC)
        
        :return: Diccionari amb l'estructura per al SOAP
        """
        inv = self.invoice
        is_out_invoice = inv.type in ('out_invoice', 'out_refund')
        
        # Generar capçalera
        cabecera = self._generate_cabecera()
        
        # Generar registre de factura
        if is_out_invoice:
            factura = self._generate_factura_emitida()
        else:
            factura = self._generate_factura_recibida()
        
        return {
            'Cabecera': cabecera,
            'RegistroLRFacturasEmitidas' if is_out_invoice else 'RegistroLRFacturasRecibidas': factura
        }
    
    def _generate_cabecera(self):
        """
        Genera la capçalera del missatge SII
        """
        inv = self.invoice
        company = inv.company_id
        
        ejercicio = inv.period_id.name[3:7] if inv.period_id else str(date.today().year)
        periodo = inv.period_id.name[0:2] if inv.period_id else '01'
        
        return {
            'IDVersionSii': __ATC_SII_VERSION__,
            'Titular': {
                'NIF': VAT.clean_vat(company.vat),
                'NombreRazon': unidecode_str(company.name)
            },
            'TipoComunicacion': 'A0',  # Alta de factura
        }
    
    def _generate_factura_emitida(self):
        """
        Genera el registre d'una factura emesa
        
        DIFERÈNCIA: Utilitza get_igic_values i estructura DesgloseIGIC
        """
        inv = self.invoice
        
        # Identificació de la factura
        id_factura = {
            'IDEmisorFactura': {
                'NIF': VAT.clean_vat(inv.company_id.vat)
            },
            'NumSerieFacturaEmisor': inv.number or '',
            'FechaExpedicionFacturaEmisor': inv.date_invoice or date.today().strftime('%d-%m-%Y')
        }
        
        # Factura expedida
        factura_expedida = {
            'TipoFactura': self._get_tipo_factura(),
            'ClaveRegimenEspecialOTrascendencia': self._get_clave_regimen(),
            'ImporteTotal': inv.amount_total,
            'DescripcionOperacion': unidecode_str(inv.name or 'Factura')[:500],
        }
        
        # CANVI CLAU: Utilitzem get_igic_values en lloc de get_iva_values
        is_out = True
        igic_values = get_igic_values(inv, in_invoice=False)
        
        # Afegir desglose IGIC (estructura diferent a IVA)
        if igic_values['sujeta_a_igic']:
            desglose = {'DesgloseIGIC': {}}
            
            if igic_values['igic_no_exento']:
                desglose['DesgloseIGIC']['DetalleIGIC'] = igic_values['detalle_igic']
            
            factura_expedida['TipoDesglose'] = desglose
        
        # Contraparte
        contraparte = get_partner_info(inv.partner_id, in_invoice=False, nombre_razon=True)
        
        return {
            'PeriodoLiquidacion': self._get_periodo_liquidacion(),
            'IDFactura': id_factura,
            'FacturaExpedida': factura_expedida,
            'Contraparte': contraparte
        }
    
    def _generate_factura_recibida(self):
        """
        Genera el registre d'una factura rebuda
        
        DIFERÈNCIA: Utilitza get_igic_values i estructura DesgloseIGIC
        """
        inv = self.invoice
        
        # Identificació de la factura
        id_factura = {
            'IDEmisorFactura': get_partner_info(inv.partner_id, in_invoice=True),
            'NumSerieFacturaEmisor': inv.supplier_invoice_number or inv.number or '',
            'FechaExpedicionFacturaEmisor': inv.date_invoice or date.today().strftime('%d-%m-%Y')
        }
        
        # Factura rebuda
        factura_recibida = {
            'TipoFactura': self._get_tipo_factura(),
            'ClaveRegimenEspecialOTrascendencia': self._get_clave_regimen(),
            'ImporteTotal': inv.amount_total,
            'DescripcionOperacion': unidecode_str(inv.name or 'Factura')[:500],
        }
        
        # CANVI CLAU: Utilitzem get_igic_values
        igic_values = get_igic_values(inv, in_invoice=True)
        
        # Afegir desglose IGIC
        if igic_values['sujeta_a_igic']:
            desglose = {'DesgloseIGIC': {}}
            
            if igic_values['igic_no_exento']:
                desglose['DesgloseIGIC']['DetalleIGIC'] = igic_values['detalle_igic']
            
            factura_recibida['DesgloseFactura'] = desglose
        
        return {
            'PeriodoLiquidacion': self._get_periodo_liquidacion(),
            'IDFactura': id_factura,
            'FacturaRecibida': factura_recibida
        }
    
    def _get_tipo_factura(self):
        """
        Determina el tipus de factura (igual que AEAT)
        """
        inv = self.invoice
        if inv.type.endswith('refund'):
            return 'R1'  # Rectificativa
        return 'F1'  # Factura normal
    
    def _get_clave_regimen(self):
        """
        Determina la clau de règim especial
        """
        # CANVI: Per defecte '08' (Operacions subjectes a IGIC)
        # en lloc de '01' (Règim general IVA)
        return '08'
    
    def _get_periodo_liquidacion(self):
        """
        Obté el període de liquidació
        """
        inv = self.invoice
        if inv.period_id:
            ejercicio = inv.period_id.name[3:7]
            periodo = inv.period_id.name[0:2]
        else:
            today = date.today()
            ejercicio = str(today.year)
            periodo = '{:02d}'.format(today.month)
        
        return {
            'Ejercicio': ejercicio,
            'Periodo': periodo
        }


class SIIATCDeregister(object):
    """
    Generador d'objectes per donar de baixa factures al SII ATC
    
    Equivalent a SIIDeregister per AEAT
    """
    
    def __init__(self, invoice):
        self.invoice = invoice
    
    def generate_object(self):
        """
        Genera l'objecte per donar de baixa una factura
        """
        inv = self.invoice
        is_out_invoice = inv.type in ('out_invoice', 'out_refund')
        
        cabecera = {
            'IDVersionSii': __ATC_SII_VERSION__,
            'Titular': {
                'NIF': VAT.clean_vat(inv.company_id.vat),
                'NombreRazon': unidecode_str(inv.company_id.name)
            },
        }
        
        id_factura = {
            'IDEmisorFactura': {
                'NIF': VAT.clean_vat(inv.company_id.vat if is_out_invoice else inv.partner_id.vat)
            },
            'NumSerieFacturaEmisor': inv.number or '',
            'FechaExpedicionFacturaEmisor': inv.date_invoice or date.today().strftime('%d-%m-%Y')
        }
        
        return {
            'Cabecera': cabecera,
            'RegistroLRBajaExpedidas' if is_out_invoice else 'RegistroLRBajaRecibidas': {
                'PeriodoLiquidacion': self._get_periodo_liquidacion(),
                'IDFactura': id_factura
            }
        }
    
    def _get_periodo_liquidacion(self):
        """
        Obté el període de liquidació
        """
        inv = self.invoice
        if inv.period_id:
            ejercicio = inv.period_id.name[3:7]
            periodo = inv.period_id.name[0:2]
        else:
            today = date.today()
            ejercicio = str(today.year)
            periodo = '{:02d}'.format(today.month)
        
        return {
            'Ejercicio': ejercicio,
            'Periodo': periodo
        }
