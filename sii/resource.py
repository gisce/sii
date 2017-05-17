# coding=utf-8
from sii import __SII_VERSION__
from sii.models import invoices_record


def get_iva_values(tax_line, in_invoice):
    vals = {
        'sujeta_a_iva': False,
        'detalle_iva': []
    }
    for tax in tax_line:
        if 'IVA' in tax.name:
            iva = {
                'BaseImponible': tax.base,
                'TipoImpositivo': tax.tax_id.amount * 100
            }
            if in_invoice:
                iva.update({'CuotaRepercutida': tax.tax_amount})
            else:
                iva.update({'CuotaSoportada': tax.tax_amount})
            vals['sujeta_a_iva'] = True
            vals['detalle_iva'].append(iva)
    return vals


def get_factura_emitida(invoice):
    vals = get_iva_values(invoice.tax_line, in_invoice=True)

    if vals['sujeta_a_iva']:
        tipo_desglose = {
            'DesgloseFactura': {
                'Sujeta': {
                    'NoExenta': {  # TODO Exenta o no exenta??
                        'TipoNoExenta': 'S1',
                        'DesgloseIVA': {
                            'DetalleIVA': vals['detalle_iva']
                        }
                    }
                }
            }
        }
    else:
        tipo_desglose = {
            'DesgloseFactura': {
                'NoSujeta': ''
            }
        }

    factura_expedida = {
        'TipoFactura': 'F1',
        'ClaveRegimenEspecialOTrascendencia': '01',  # TODO
        'ImporteTotal': invoice.amount_total,
        'DescripcionOperacion': invoice.name,
        'Contraparte': {
            'NombreRazon': invoice.partner_id.name,
            'NIF': invoice.partner_id.vat
        },
        'TipoDesglose': tipo_desglose
    }

    return factura_expedida


def get_factura_recibida(invoice):
    vals = get_iva_values(invoice.tax_line, in_invoice=False)

    if vals['sujeta_a_iva']:
        tipo_desglose = {  # TODO to change
            'InversionSujetoPasivo': {
                'DetalleIVA': vals['detalle_iva']
            },
            'DesgloseIVA': {
                'DetalleIVA': vals['detalle_iva']
            }
        }
    else:
        raise Exception("Missing 'IVA' in invoice.tax_line")

    factura_recibida = {
        'TipoFactura': 'F1',
        'ClaveRegimenEspecialOTrascendencia': '01',  # TODO
        'ImporteTotal': invoice.amount_total,
        'DescripcionOperacion': invoice.name,
        'Contraparte': {
            'NombreRazon': invoice.partner_id.name,
            'NIF': invoice.partner_id.vat
        },
        'DesgloseFactura': tipo_desglose,
        'CuotaDeducible': vals['cuota_repercutida'],
        'FechaRegContable': ''  # TODO to change
    }

    return factura_recibida


def get_header(invoice):
    cabecera = {
        'IDVersionSii': __SII_VERSION__,
        'Titular': {
            'NombreRazon': invoice.company_id.partner_id.name,
            'NIF': invoice.company_id.partner_id.vat
        },
        'TipoComunicacion': 'A0'
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

        obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']['FacturaExpedida'].update(vals)

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
                    'NumSerieFacturaEmisor': invoice.number,
                    'FechaExpedicionFacturaEmisor': invoice.date_invoice
                },
                'FacturaRecibida': get_factura_recibida(invoice)
            }
        }
    }

    if rectificativa:
        vals = get_factura_rectificativa_fields()

        obj['SuministroLRFacturasRecibidas']['RegistroLRFacturasRecibidas']['FacturaRecibida'].update(vals)

    return obj


class SII(object):
    @staticmethod
    def generate_object(invoice):

        if invoice.type == 'in_invoice':
            invoice_model = invoices_record.SuministroFacturasRecibidas()
            invoice_dict = get_factura_recibida_dict(invoice)
        elif invoice.type == 'out_invoice':
            invoice_model = invoices_record.SuministroFacturasEmitidas()
            invoice_dict = get_factura_emitida_dict(invoice)
        elif invoice.type == 'in_refund':
            invoice_model = invoices_record.SuministroFacturasRecibidas()
            invoice_dict = get_factura_recibida_dict(invoice, rectificativa=True)
        elif invoice.type == 'out_refund':
            invoice_model = invoices_record.SuministroFacturasEmitidas()
            invoice_dict = get_factura_emitida_dict(invoice, rectificativa=True)
        else:
            raise Exception('Error in invoice.type')

        errors = invoice_model.validate(invoice_dict)
        if errors:
            raise Exception(
                'Errors were found while trying to generate the dump:', errors)

        res = invoice_model.dump(invoice_dict).data
        return res
