# coding=utf-8
import re
from unidecode import unidecode

from sii import __SII_VERSION__
from sii.models import invoices_record

SIGN = {'B': -1, 'A': -1, 'N': 1, 'R': 1}


def get_importe_no_sujeto_a_iva(invoice):
    importe_no_sujeto = 0

    for line in invoice.invoice_line:
        no_iva = True
        for tax in line.invoice_line_tax_id:
            if 'iva' in tax.name.lower():
                no_iva = False
                break
        if no_iva:
            importe_no_sujeto += line.price_subtotal

    return importe_no_sujeto


def get_iva_values(invoice, in_invoice):
    vals = {
        'sujeta_a_iva': False,
        'detalle_iva': [],
        'no_sujeta_a_iva': False,
        'iva_exento': False,
        'iva_no_exento': False,
        'detalle_iva_exento': {'BaseImponible': 0}
    }
    for inv_tax in invoice.tax_line:
        if 'iva' in inv_tax.name.lower():
            vals['sujeta_a_iva'] = True
            if inv_tax.tax_id.amount == 0 and inv_tax.tax_id.type == 'percent':
                vals['iva_exento'] = True
                vals['detalle_iva_exento']['BaseImponible'] += inv_tax.base
            else:
                sign = SIGN[invoice.rectificative_type]
                iva = {
                    'BaseImponible': sign * inv_tax.base,
                    'TipoImpositivo': inv_tax.tax_id.amount * 100
                }
                if in_invoice:
                    iva['CuotaRepercutida'] = sign * inv_tax.tax_amount
                else:
                    iva['CuotaSoportada'] = sign * inv_tax.tax_amount
                vals['iva_no_exento'] = True
                vals['detalle_iva'].append(iva)
        else:
            vals['no_sujeta_a_iva'] = True
    return vals


def get_factura_emitida(invoice):
    iva_values = get_iva_values(invoice, in_invoice=True)
    desglose_factura = {}

    if iva_values['sujeta_a_iva']:
        desglose_factura['Sujeta'] = {}
        if iva_values['iva_exento']:
            desglose_factura['Sujeta']['Exenta'] = \
                iva_values['detalle_iva_exento']
        if iva_values['iva_no_exento']:
            desglose_factura['Sujeta']['NoExenta'] = {
                'TipoNoExenta': 'S2',
                'DesgloseIVA': {
                    'DetalleIVA': iva_values['detalle_iva']
                }
            }
    if iva_values['no_sujeta_a_iva']:
        importe_no_sujeto = get_importe_no_sujeto_a_iva(invoice)

        fp = invoice.fiscal_position
        if fp and 'islas canarias' in unidecode(fp.name.lower()):
            desglose_factura['NoSujeta'] = {
                'ImporteTAIReglasLocalizacion': importe_no_sujeto
            }
        else:
            desglose_factura['NoSujeta'] = {
                'ImportePorArticulos7_14_Otros': importe_no_sujeto
            }

    if invoice.partner_id.aeat_registered:
        contraparte = {
            'NombreRazon': invoice.partner_id.name,
            'NIF': invoice.partner_id.vat
        }
    else:
        contraparte = {
            'NombreRazon': invoice.partner_id.name,
            'IDOtro': {
                'CodigoPais': 'ES',
                'IDType': '07',
                'ID': invoice.partner_id.vat
            }
        }

    if invoice.fiscal_position:
        clave_regimen_escpecial = \
            invoice.fiscal_position.sii_out_clave_regimen_especial
    elif invoice.partner_id.property_account_position:
        clave_regimen_escpecial = \
            invoice.partner_id.property_account_position.sii_out_clave_regimen_especial
    elif invoice.journal_id:
        clave_regimen_escpecial = \
            invoice.journal_id.sii_out_clave_regimen_especial
    else:
        raise AttributeError('La Factura no tiene Clave de Régimen Especial')

    factura_expedida = {
        'TipoFactura': 'R4' if invoice.rectificative_type == 'R' else 'F1',
        'ClaveRegimenEspecialOTrascendencia': clave_regimen_escpecial,
        'ImporteTotal': SIGN[invoice.rectificative_type] * invoice.amount_total,
        'DescripcionOperacion': invoice.journal_id.name,
        'Contraparte': contraparte,
        'TipoDesglose': {
            'DesgloseFactura': desglose_factura
        }
    }

    return factura_expedida


def get_factura_recibida(invoice):
    iva_values = get_iva_values(invoice, in_invoice=False)
    cuota_deducible = 0

    if iva_values['sujeta_a_iva'] and iva_values['iva_no_exento']:
        desglose_factura = {  # TODO to change
            # 'InversionSujetoPasivo': {
            #     'DetalleIVA': iva_values['detalle_iva']
            # },
            'DesgloseIVA': {
                'DetalleIVA': iva_values['detalle_iva']
            }
        }

        for detalle_iva in iva_values['detalle_iva']:
            cuota_deducible += detalle_iva['CuotaSoportada']
    else:
        desglose_factura = {
            'DesgloseIVA': {
                'DetalleIVA': {
                    'BaseImponible': 0  # TODO deixem de moment 0 perquè no tindrem inversio sujeto pasivo
                }
            }
        }

    if invoice.fiscal_position:
        clave_regimen_escpecial = \
            invoice.fiscal_position.sii_in_clave_regimen_especial
    else:
        clave_regimen_escpecial = \
            invoice.journal_id.sii_in_clave_regimen_especial

    factura_recibida = {
        'TipoFactura': 'R4' if invoice.rectificative_type == 'R' else 'F1',
        'ClaveRegimenEspecialOTrascendencia': clave_regimen_escpecial,
        'ImporteTotal': SIGN[invoice.rectificative_type] * invoice.amount_total,
        'DescripcionOperacion': invoice.journal_id.name,
        'Contraparte': {
            'NombreRazon': invoice.partner_id.name,
            'NIF': invoice.partner_id.vat
        },
        'DesgloseFactura': desglose_factura,
        'CuotaDeducible': cuota_deducible,
        'FechaRegContable': '2017-12-31'  # TODO to change
    }

    return factura_recibida


def get_header(invoice):
    cabecera = {
        'IDVersionSii': __SII_VERSION__,
        'Titular': {
            'NombreRazon': invoice.company_id.partner_id.name,
            'NIF': invoice.company_id.partner_id.vat
        },
        'TipoComunicacion': 'A0' if not invoice.sii_registered else 'A1'
    }

    return cabecera


def get_factura_rectificativa_fields():
    rectificativa_fields = {
        'TipoRectificativa': 'S',  # Por sustitución
        'ImporteRectificacion': {
            'BaseRectificada': 0,
            'CuotaRectificada': 0
        }
    }

    return rectificativa_fields


def get_factura_emitida_dict(invoice, rectificativa=False):
    obj = {
        'SuministroLRFacturasEmitidas': {
            'Cabecera': get_header(invoice),
            'RegistroLRFacturasEmitidas': {
                'PeriodoImpositivo': {
                    'Ejercicio': invoice.period_id.name[3:7],
                    'Periodo': invoice.period_id.name[0:2]
                },
                'IDFactura': {
                    'IDEmisorFactura': {
                        'NIF': invoice.company_id.partner_id.vat
                    },
                    'NumSerieFacturaEmisor': invoice.number,
                    'FechaExpedicionFacturaEmisor': invoice.date_invoice
                },
                'FacturaExpedida': get_factura_emitida(invoice)
            }
        }
    }

    if rectificativa:
        vals = get_factura_rectificativa_fields()

        (
            obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            ['FacturaExpedida']
        ).update(vals)

    return obj


def get_factura_recibida_dict(invoice, rectificativa=False):
    obj = {
        'SuministroLRFacturasRecibidas': {
            'Cabecera': get_header(invoice),
            'RegistroLRFacturasRecibidas': {
                'PeriodoImpositivo': {
                    'Ejercicio': invoice.period_id.name[3:7],
                    'Periodo': invoice.period_id.name[0:2]
                },
                'IDFactura': {
                    'IDEmisorFactura': {
                        'NIF': invoice.partner_id.vat
                    },
                    'NumSerieFacturaEmisor': invoice.origin,
                    'FechaExpedicionFacturaEmisor': invoice.date_invoice
                },
                'FacturaRecibida': get_factura_recibida(invoice)
            }
        }
    }

    if rectificativa:
        vals = get_factura_rectificativa_fields()

        (
            obj['SuministroLRFacturasRecibidas']['RegistroLRFacturasRecibidas']
            ['FacturaRecibida']
        ).update(vals)

    return obj


def refactor_nifs(invoice):
    for partner in (invoice.partner_id, invoice.company_id.partner_id):
        partner.vat = re.sub('^ES', '', partner.vat.upper())


class SII(object):
    def __init__(self, invoice):
        self.invoice = invoice
        refactor_nifs(self.invoice)
        rectificativa = invoice.rectificative_type == 'R'
        if invoice.type.startswith('in'):
            self.invoice_model = invoices_record.SuministroFacturasRecibidas()
            self.invoice_dict = get_factura_recibida_dict(
                self.invoice, rectificativa=rectificativa
            )
        elif invoice.type.startswith('out'):
            self.invoice_model = invoices_record.SuministroFacturasEmitidas()
            self.invoice_dict = get_factura_emitida_dict(
                self.invoice, rectificativa=rectificativa
            )
        else:
            raise AttributeError('Unknown value in invoice.type')

    def validate_invoice(self):

        errors = self.invoice_model.validate(self.invoice_dict)

        res = {
            'successful': False if errors else True,
            'errors': errors
        }

        return res

    def generate_object(self):

        validation_values = self.validate_invoice()
        if not validation_values['successful']:
            raise Exception(
                'Errors were found while trying to validate the data:',
                validation_values['errors']
            )

        res = self.invoice_model.dump(self.invoice_dict)
        if res.errors:
            raise Exception(
                'Errors were found while trying to generate the dump:',
                res.errors
            )

        return res.data
