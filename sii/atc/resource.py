# coding=utf-8
"""
Resource per SII ATC - Agència Tributària Canària

Aquest mòdul genera els objectes per enviar al SII ATC utilitzant IGIC.
Segueix EXACTAMENT la mateixa estructura que sii/resource.py però adaptat per IGIC.
"""
import re
from decimal import Decimal
from datetime import date, datetime

from sii.atc import __ATC_SII_VERSION__
from sii.utils import unidecode_str, VAT
from sii.atc.models import invoices_record

SIGN = {'N': 1, 'R': 1, 'A': -1, 'B': -1, 'RA': 1, 'C': 1, 'G': 1}


def convert_date_to_atc_format(date_value):
    """
    Converteix una data de format ISO (YYYY-MM-DD) a format ATC (DD-MM-YYYY)
    
    Args:
        date_value: String amb data en format ISO o ja en format ATC
        
    Returns:
        String amb data en format DD-MM-YYYY
    """
    if not date_value or not isinstance(date_value, str):
        return date_value
    
    # Si ja està en format DD-MM-YYYY, retornar
    if len(date_value) == 10 and date_value[2] == '-' and date_value[5] == '-':
        return date_value
    
    # Si està en format ISO (YYYY-MM-DD), convertir
    if len(date_value) == 10 and date_value[4] == '-' and date_value[7] == '-':
        try:
            date_obj = datetime.strptime(date_value, '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%Y')
        except ValueError:
            pass  # Si falla, retornar el valor original
    
    return date_value


def get_clave_regimen_especial_atc(invoice, is_out_invoice=True):
    """
    Obté la Clave de Régimen Especial específica per ATC des de la factura
    
    Crida al mètode de la factura per obtenir el CRE específic d'ATC.
    El mètode get_clave_regimen_especial_atc() està implementat al
    mòdul ERP (account_invoice.py) i gestiona la lògica de cache.
    
    Args:
        invoice: Objecte factura (browse)
        is_out_invoice: True si és factura emesa, False si és rebuda
        
    Returns:
        string: Codi CRE ('01'-'20' per emeses, '01'-'15' per rebudes)
    
    Raises:
        AttributeError: Si l'invoice no té el mètode get_clave_regimen_especial_atc()
    """
    return invoice.get_clave_regimen_especial_atc(is_out_invoice=is_out_invoice)


def get_periodo_ejercicio(invoice):
    """
    Extreu període i exercici de la factura.
    
    Intenta primer usar period_id.name amb format MM/YYYY,
    si no és vàlid, usa period_id.date_start per calcular-ho.
    
    Returns:
        tuple: (periodo, ejercicio) ex: ('01', '2026')
    
    Raises:
        ValueError: Si no es pot determinar el període i exercici
    """
    if invoice.period_id:
        # Intentar usar period_id.name amb format MM/YYYY
        period_name = invoice.period_id.name
        if '/' in period_name and len(period_name) >= 7:
            periodo = period_name[0:2]
            ejercicio = period_name[3:7]
            # Validar que siguin dígits
            if periodo.isdigit() and ejercicio.isdigit():
                return (periodo, ejercicio)
        
        # Fallback: usar date_start per calcular període i exercici
        if hasattr(invoice.period_id, 'date_start') and invoice.period_id.date_start:
            date_start = invoice.period_id.date_start
            # Convertir string a datetime si cal
            if isinstance(date_start, str):
                date_start = datetime.strptime(date_start, '%Y-%m-%d')
            periodo = '{:02d}'.format(date_start.month)
            ejercicio = str(date_start.year)
            return (periodo, ejercicio)
    
    # Últim fallback: usar date_invoice
    if hasattr(invoice, 'date_invoice') and invoice.date_invoice:
        date_invoice = invoice.date_invoice
        if isinstance(date_invoice, str):
            date_invoice = datetime.strptime(date_invoice, '%Y-%m-%d')
        periodo = '{:02d}'.format(date_invoice.month)
        ejercicio = str(date_invoice.year)
        return (periodo, ejercicio)
    
    # Si tot falla, llançar error
    raise ValueError(
        "No s'ha pogut determinar el període i exercici de la factura. "
        "La factura ha de tenir period_id amb date_start o date_invoice vàlids."
    )


def is_inversion_sujeto_pasivo(tax_name):
    regex_isp = r'inv.*sujeto pasivo'
    return bool(re.search(regex_isp, unidecode_str(tax_name).lower()))


def get_invoice_sign(invoice):
    if invoice.type.endswith('refund'):
        return -1
    return 1


def get_igic_values(invoice, in_invoice, is_export=False, is_import=False):
    """Obté els valors d'IGIC (CANVI: busca 'igic' en lloc de 'iva')"""
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

    igic_values = {}
    sign = get_invoice_sign(invoice)
    invoice_total = sign * invoice.amount_total

    for inv_tax in invoice.tax_line:
        if 'igic' in inv_tax.name.lower():  # CANVI CLAU
            vals['sujeta_a_igic'] = True
            base_igic = inv_tax.base
            base_imponible = sign * base_igic
            cuota = inv_tax.tax_amount
            tipo_impositivo_unitario = inv_tax.tax_id.amount
            tipo_impositivo = tipo_impositivo_unitario * 100
            tax_name = inv_tax.tax_id.name.lower()
            invoice_total -= (base_imponible + cuota)
            tax_type = inv_tax.tax_id.type
            is_igic_exento = (tipo_impositivo_unitario == 0 and tax_type == 'percent' and ('exento' in tax_name or 'exempt' in tax_name))
            
            if is_inversion_sujeto_pasivo(inv_tax.name):
                new_value = {
                    'BaseImponible': base_imponible,
                    'TipoImpositivo': tipo_impositivo,
                    'CuotaRepercutida': cuota
                }
                vals['inversion_sujeto_pasivo'].append(new_value)
            elif not is_export and not is_import and is_igic_exento:
                vals['igic_exento'] = True
                vals['detalle_igic_exento']['BaseImponible'] += inv_tax.base
            else:
                cuota_key = 'CuotaSoportada' if in_invoice else 'CuotaRepercutida'
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
    Obté informació del partner per al SII ATC.
    Adaptació de sii.resource.get_partner_info() per IGIC.
    """
    vat_type_result = partner.sii_get_vat_type()
    # sii_get_vat_type() pot retornar tupla (vat_type, auto_vat) o només vat_type
    if isinstance(vat_type_result, tuple):
        vat_type, auto_vat = vat_type_result
    else:
        vat_type = vat_type_result
        auto_vat = False
    
    contraparte = {}
    
    partner_country = partner.country_id or partner.country
    if nombre_razon:
        contraparte['NombreRazon'] = unidecode_str(partner.name)
    
    # Per factures rebudes amb auto_vat i vat_type '07', convertir a '02' (NIF)
    if auto_vat and vat_type == '07' and in_invoice:
        vat_type = '02'
    
    # NIFs espanyols (vat_type '02') sempre usen camp NIF
    if vat_type == '02':
        contraparte['NIF'] = VAT.clean_vat(partner.vat)
    else:
        contraparte['IDOtro'] = {
            'CodigoPais': partner_country.code,
            'IDType': vat_type,
            'ID': VAT.clean_vat(partner.vat)
        }
    
    return contraparte


def get_header(invoice):
    """Genera la capçalera del missatge"""
    # TipoComunicacion: A0 (alta) o A1 (modificació)
    # A1 només si ja s'ha enviat amb èxit anteriorment
    sii_atc_registered = (
        hasattr(invoice, 'sii_atc_sent') and 
        invoice.sii_atc_sent and 
        hasattr(invoice, 'sii_atc_state') and
        invoice.sii_atc_state == 'Correcto'
    )
    tipo_comunicacion = 'A1' if sii_atc_registered else 'A0'
    
    return {
        'IDVersionSii': __ATC_SII_VERSION__,
        'Titular': {
            'NombreRazon': unidecode_str(invoice.company_id.partner_id.name),
            'NIF': VAT.clean_vat(invoice.company_id.partner_id.vat)
        },
        'TipoComunicacion': tipo_comunicacion
    }


def get_factura_emitida_tipo_desglose(invoice):
    in_invoice = False
    is_export = invoice.sii_out_clave_regimen_especial == '02'
    igic_values = get_igic_values(invoice, in_invoice=in_invoice, is_export=is_export)

    if bool(is_export):
        if igic_values['sujeta_a_igic']:
            detalle_igic = igic_values['detalle_igic']
            entrega = {
                'Sujeta': {
                    'NoExenta': {
                        'TipoNoExenta': 'S1',
                        'DesgloseIGIC': {'DetalleIGIC': detalle_igic}
                    }
                }
            }
        else:
            entrega = {
                'NoSujeta': {
                    'ImporteTAIReglasLocalizacion': igic_values['importe_no_sujeto']
                }
            }
        tipo_desglose = {'DesgloseTipoOperacion': {'Entrega': entrega}}
    elif igic_values['inversion_sujeto_pasivo']:
        tipo_desglose = {
            'DesgloseTipoOperacion': {
                'Entrega': {
                    'Sujeta': {
                        'NoExenta': {
                            'TipoNoExenta': 'S2',
                            'DesgloseIGIC': {'DetalleIGIC': igic_values['inversion_sujeto_pasivo']}
                        }
                    }
                }
            }
        }
    else:
        desglose = {}
        detalle_igic_exento = igic_values['detalle_igic_exento']
        detalle_igic = igic_values['detalle_igic']
        importe_no_sujeto = igic_values['importe_no_sujeto']
        
        if igic_values['sujeta_a_igic']:
            desglose['Sujeta'] = {}
            if igic_values['igic_exento']:
                # DetalleExenta ha de ser un array d'elements
                desglose['Sujeta']['Exenta'] = {'DetalleExenta': [detalle_igic_exento]}
            if igic_values['igic_no_exento']:
                desglose['Sujeta']['NoExenta'] = {
                    'TipoNoExenta': 'S1',
                    'DesgloseIGIC': {'DetalleIGIC': detalle_igic}
                }
        if igic_values['no_sujeta_a_igic']:
            fp = invoice.fiscal_position
            if fp and 'islas canarias' in unidecode_str(fp.name.lower()):
                desglose['NoSujeta'] = {'ImporteTAIReglasLocalizacion': importe_no_sujeto}
            else:
                desglose['NoSujeta'] = {'ImportePorArticulos7_14_Otros': importe_no_sujeto}
        
        partner_vat = VAT.clean_vat(invoice.partner_id.vat)
        partner_vat_starts_with_n = (partner_vat and partner_vat.upper().startswith('N'))
        
        # sii_get_vat_type() pot retornar tupla (vat_type, auto_vat) o només vat_type
        vat_type_result = invoice.partner_id.sii_get_vat_type()
        if isinstance(vat_type_result, tuple):
            vat_type, _ = vat_type_result
        else:
            vat_type = vat_type_result
        
        has_id_otro = vat_type != '02'
        # Assegurar que sempre retornem un tipo_desglose vàlid
        if desglose:  # Si hi ha contingut al desglose
            if has_id_otro or partner_vat_starts_with_n:
                tipo_desglose = {'DesgloseTipoOperacion': {'PrestacionServicios': desglose}}
            else:
                tipo_desglose = {'DesgloseFactura': desglose}
        else:  # Si desglose està buit, crear estructura mínima vàlida
            # En cas que no hi hagi cap impost (anomalia), crear estructura amb Sujeta/NoExenta
            desglose_default = {
                'Sujeta': {
                    'NoExenta': {
                        'TipoNoExenta': 'S1',
                        'DesgloseIGIC': {
                            'DetalleIGIC': [{
                                'TipoImpositivo': 0.0,
                                'BaseImponible': 0.0,
                                'CuotaSoportada': 0.0
                            }]
                        }
                    }
                }
            }
            if has_id_otro or partner_vat_starts_with_n:
                tipo_desglose = {'DesgloseTipoOperacion': {'PrestacionServicios': desglose_default}}
            else:
                tipo_desglose = {'DesgloseFactura': desglose_default}
    return tipo_desglose


def get_fact_rect_sustitucion_fields(invoice, opcion=False):
    rectificativa_fields = {'TipoRectificativa': 'S'}
    if opcion == 1:
        rectified_invoice = invoice.rectifying_id
        base_rect = get_invoice_sign(rectified_invoice) * rectified_invoice.amount_untaxed
        cuota_rect = get_invoice_sign(rectified_invoice) * rectified_invoice.amount_tax
        rectificativa_fields['ImporteRectificacion'] = {
            'BaseRectificada': base_rect,
            'CuotaRectificada': cuota_rect
        }
    elif opcion == 2:
        rectificativa_fields['ImporteRectificacion'] = {
            'BaseRectificada': 0,
            'CuotaRectificada': 0
        }
    return rectificativa_fields


def get_factura_emitida(invoice, rect_sust_opc1=False, rect_sust_opc2=False):
    # IMPORTANT: Només R4 si és SUBSTITUCIÓ (rectificative_type='R' o 'RA')
    # Les abonadores 'A', 'B' o refunds simples són F1 (NO R4)
    rectificativa_sustitucion = rect_sust_opc1 or rect_sust_opc2
    
    importe_total = get_invoice_sign(invoice) * invoice.amount_total
    
    # Obtenir CRE específic per ATC des del cache info
    cre_atc = get_clave_regimen_especial_atc(invoice, is_out_invoice=True)
    
    factura_expedida = {
        'TipoFactura': 'R4' if rectificativa_sustitucion else 'F1',
        'ClaveRegimenEspecialOTrascendencia': cre_atc,
        'ImporteTotal': importe_total,
        'DescripcionOperacion': unidecode_str(invoice.sii_description)
    }
    tipo_desglose = get_factura_emitida_tipo_desglose(invoice)
    factura_expedida['TipoDesglose'] = tipo_desglose
    contraparte = get_partner_info(invoice.partner_id, in_invoice=False, nombre_razon=True)
    
    if rectificativa_sustitucion:
        opcion = 0
        if rect_sust_opc1:
            opcion = 1
        elif rect_sust_opc2:
            opcion = 2
        vals = get_fact_rect_sustitucion_fields(invoice, opcion=opcion)
        fact_rect = invoice.rectifying_id
        # Comprovar si la factura rectificada està registrada a l'ATC (no al SII AEAT)
        if fact_rect and hasattr(fact_rect, 'sii_atc_sent') and fact_rect.sii_atc_sent and \
           hasattr(fact_rect, 'sii_atc_state') and fact_rect.sii_atc_state == 'Correcto':
            vals['FacturasRectificadas'] = {
                'IDFacturaRectificada': [{
                    'NumSerieFacturaEmisor': fact_rect.number,
                    'FechaExpedicionFacturaEmisor': convert_date_to_atc_format(fact_rect.date_invoice)
                }]
            }
        factura_expedida.update(vals)
    return factura_expedida, contraparte


def get_factura_recibida(invoice, rect_sust_opc1=False, rect_sust_opc2=False):
    in_invoice = True
    
    # Obtenir CRE específic per ATC des del cache info
    cre_atc = get_clave_regimen_especial_atc(invoice, is_out_invoice=False)
    is_import = cre_atc == '13'
    
    igic_values = get_igic_values(invoice, in_invoice=in_invoice, is_import=is_import)
    cuota_deducible = 0
    importe_total = get_invoice_sign(invoice) * invoice.amount_total
    
    if igic_values['sujeta_a_igic'] and igic_values['igic_no_exento']:
        detalle_igic = igic_values['detalle_igic']
        desglose_factura = {'DesgloseIGIC': {'DetalleIGIC': detalle_igic}}
        for igic in detalle_igic:
            cuota_deducible += igic['CuotaSoportada']
    else:
        base_imponible_factura = invoice.amount_untaxed
        desglose_factura = {'DesgloseIGIC': {'DetalleIGIC': [{'BaseImponible': base_imponible_factura}]}}
    
    fecha_reg_contable = convert_date_to_atc_format(invoice.date_invoice)
    is_first_semester_2017 = cre_atc == '14'
    if is_first_semester_2017:
        fecha_reg_contable = convert_date_to_atc_format(date.today().strftime('%Y-%m-%d'))
        cuota_deducible = 0
    
    # IMPORTANT: Només R4 si és SUBSTITUCIÓ (rectificative_type='R' o 'RA')
    # Les abonadores 'A', 'B' o refunds simples són F1 (NO R4)
    rectificativa_sustitucion = rect_sust_opc1 or rect_sust_opc2
    
    factura_recibida = {
        'TipoFactura': 'R4' if rectificativa_sustitucion else 'F1',
        'ClaveRegimenEspecialOTrascendencia': cre_atc,
        'ImporteTotal': importe_total,
        'DescripcionOperacion': unidecode_str(invoice.sii_description),
        'DesgloseFactura': desglose_factura,
        'Contraparte': get_partner_info(invoice.partner_id, in_invoice=True, nombre_razon=True),
        'FechaRegContable': fecha_reg_contable,
        'CuotaDeducible': cuota_deducible
    }
    
    if rectificativa_sustitucion:
        opcion = 0
        if rect_sust_opc1:
            opcion = 1
        elif rect_sust_opc2:
            opcion = 2
        vals = get_fact_rect_sustitucion_fields(invoice, opcion=opcion)
        fact_rect = invoice.rectifying_id
        # Comprovar si la factura rectificada està registrada a l'ATC (no al SII AEAT)
        if fact_rect and hasattr(fact_rect, 'sii_atc_sent') and fact_rect.sii_atc_sent and \
           hasattr(fact_rect, 'sii_atc_state') and fact_rect.sii_atc_state == 'Correcto':
            vals['FacturasRectificadas'] = {
                'IDFacturaRectificada': [{
                    'NumSerieFacturaEmisor': fact_rect.origin,
                    'FechaExpedicionFacturaEmisor': convert_date_to_atc_format(fact_rect.origin_date_invoice)
                }]
            }
        factura_recibida.update(vals)
    return factura_recibida


def get_factura_emitida_dict(invoice, rect_sust_opc1=False, rect_sust_opc2=False):
    factura_expedida, contraparte = get_factura_emitida(invoice, rect_sust_opc1, rect_sust_opc2)
    # Contraparte va dins de FacturaExpedida segons l'exemple oficial
    if contraparte:
        factura_expedida['Contraparte'] = contraparte
    periodo, ejercicio = get_periodo_ejercicio(invoice)
    
    # Convertir data de format ISO (YYYY-MM-DD) a format ATC (DD-MM-YYYY)
    fecha_expedicion = invoice.date_invoice
    if fecha_expedicion and isinstance(fecha_expedicion, str):
        # Si està en format ISO (YYYY-MM-DD), convertir a DD-MM-YYYY
        if len(fecha_expedicion) == 10 and fecha_expedicion[4] == '-' and fecha_expedicion[7] == '-':
            from datetime import datetime
            try:
                date_obj = datetime.strptime(fecha_expedicion, '%Y-%m-%d')
                fecha_expedicion = date_obj.strftime('%d-%m-%Y')
            except ValueError:
                pass  # Si falla, deixar el valor original
    
    obj = {
        'SuministroLRFacturasEmitidas': {
            'Cabecera': get_header(invoice),
            'RegistroLRFacturasEmitidas': {
                'PeriodoLiquidacion': {
                    'Ejercicio': ejercicio,
                    'Periodo': periodo
                },
                'IDFactura': {
                    'IDEmisorFactura': {'NIF': VAT.clean_vat(invoice.company_id.partner_id.vat)},
                    'NumSerieFacturaEmisor': invoice.number,
                    'FechaExpedicionFacturaEmisor': fecha_expedicion
                },
                'FacturaExpedida': factura_expedida
            }
        }
    }
    return obj


def get_factura_recibida_dict(invoice, rect_sust_opc1=False, rect_sust_opc2=False):
    obj = {
        'SuministroLRFacturasRecibidas': {
            'Cabecera': get_header(invoice),
            'RegistroLRFacturasRecibidas': {
                'PeriodoLiquidacion': {
                    'Ejercicio': get_periodo_ejercicio(invoice)[1],
                    'Periodo': get_periodo_ejercicio(invoice)[0]
                },
                'IDFactura': {
                    'IDEmisorFactura': get_partner_info(invoice.partner_id, in_invoice=True),
                    'NumSerieFacturaEmisor': invoice.origin,
                    'FechaExpedicionFacturaEmisor': invoice.origin_date_invoice
                },
                'FacturaRecibida': get_factura_recibida(invoice, rect_sust_opc1, rect_sust_opc2)
            }
        }
    }
    return obj


def refactor_decimals(invoice):
    def transform(f):
        return Decimal(str(f))
    invoice.amount_total = transform(invoice.amount_total)
    invoice.amount_untaxed = transform(invoice.amount_untaxed)
    for inv_tax in invoice.tax_line:
        inv_tax.tax_amount = transform(inv_tax.tax_amount)
        inv_tax.base = transform(inv_tax.base)
        inv_tax.tax_id.amount = transform(inv_tax.tax_id.amount)
    if invoice.rectifying_id:
        rectified_invoice = invoice.rectifying_id
        rectified_invoice.amount_total = transform(rectified_invoice.amount_total)
        rectified_invoice.amount_untaxed = transform(rectified_invoice.amount_untaxed)
        for rect_inv_tax in rectified_invoice.tax_line:
            rect_inv_tax.tax_amount = transform(rect_inv_tax.tax_amount)
            rect_inv_tax.base = transform(rect_inv_tax.base)
            rect_inv_tax.tax_id.amount = transform(rect_inv_tax.tax_id.amount)


class SIIATC(object):
    """Classe SII per ATC - genera objectes per enviar al SII amb IGIC"""
    def __init__(self, invoice):
        self.invoice = invoice
        refactor_decimals(self.invoice)
        tipo_rectificativa = invoice.rectificative_type
        rectificativa_sustitucion_opcion_1 = tipo_rectificativa == 'RA'
        rectificativa_sustitucion_opcion_2 = tipo_rectificativa == 'R'
        if invoice.type.startswith('in'):
            self.invoice_model = invoices_record.SuministroLRFacturasRecibidas()
            self.full_dict = get_factura_recibida_dict(
                invoice=self.invoice,
                rect_sust_opc1=rectificativa_sustitucion_opcion_1,
                rect_sust_opc2=rectificativa_sustitucion_opcion_2
            )
            # Extreure el contingut interior per validació Marshmallow
            self.invoice_dict = self.full_dict.get('SuministroLRFacturasRecibidas', {})
        elif invoice.type.startswith('out'):
            self.invoice_model = invoices_record.SuministroLRFacturasEmitidas()
            self.full_dict = get_factura_emitida_dict(
                invoice=self.invoice,
                rect_sust_opc1=rectificativa_sustitucion_opcion_1,
                rect_sust_opc2=rectificativa_sustitucion_opcion_2
            )
            # Extreure el contingut interior per validació Marshmallow
            self.invoice_dict = self.full_dict.get('SuministroLRFacturasEmitidas', {})
        else:
            raise Exception('Tipus de factura no reconegut')
    def get_validation_errors_list(self, errors):
        error_messages = []

        for key, values in errors.items():
            if isinstance(values, dict):
                error_messages += self.get_validation_errors_list(values)
            else:
                error_messages += ['{}: {}'.format(key, val) for val in values]

        return error_messages

    def validate_invoice(self):

        res = {}
        print(self.invoice_dict)
        errors = self.invoice_model.validate(self.invoice_dict)

        res['successful'] = False if errors else True
        res['object_validated'] = self.invoice_dict
        if errors:
            errors_list = self.get_validation_errors_list(errors)
            res['errors'] = errors_list

        return res

    def generate_object(self):
        """Retorna el dict complet amb la clau exterior per compatibilitat amb tests"""
        return self.full_dict


class SIIATCDeregister(object):
    """Classe per donar de baixa factures del SII ATC"""
    def __init__(self, invoice):
        self.invoice = invoice

    def generate_deregister_object(self):
        if self.invoice.type.startswith('out'):
            return self.get_baja_factura_emitida()
        elif self.invoice.type.startswith('in'):
            return self.get_baja_factura_recibida()
        else:
            raise Exception('Tipus de factura no reconegut')

    def get_baja_factura_emitida(self):
        obj = {
            'BajaLRFacturasEmitidas': {
                'Cabecera': get_header(self.invoice),
                'RegistroLRBajaExpedidas': {
                    'PeriodoLiquidacion': {
                        'Ejercicio': get_periodo_ejercicio(self.invoice)[1],
                        'Periodo': get_periodo_ejercicio(self.invoice)[0]
                    },
                    'IDFactura': {
                        'IDEmisorFactura': {'NIF': VAT.clean_vat(self.invoice.company_id.partner_id.vat)},
                        'NumSerieFacturaEmisor': self.invoice.number,
                        'FechaExpedicionFacturaEmisor': convert_date_to_atc_format(self.invoice.date_invoice)
                    }
                }
            }
        }
        return obj

    def get_baja_factura_recibida(self):
        obj = {
            'BajaLRFacturasRecibidas': {
                'Cabecera': get_header(self.invoice),
                'RegistroLRBajaRecibidas': {
                    'PeriodoLiquidacion': {
                        'Ejercicio': get_periodo_ejercicio(self.invoice)[1],
                        'Periodo': get_periodo_ejercicio(self.invoice)[0]
                    },
                    'IDFactura': {
                        'IDEmisorFactura': get_partner_info(self.invoice.partner_id, in_invoice=True),
                        'NumSerieFacturaEmisor': self.invoice.origin,
                        'FechaExpedicionFacturaEmisor': convert_date_to_atc_format(self.invoice.origin_date_invoice)
                    }
                }
            }
        }
        return obj
