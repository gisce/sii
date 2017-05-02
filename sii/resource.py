# coding=utf-8
from sii import models, __SII_VERSION__
from datetime import datetime


def get_base_imponible_iva(tax_line):
    for tax in tax_line:
        if 'IVA' in tax.name:
            return tax.base
    return ''


def get_factura_expedida(invoice):

    base_imponible = get_base_imponible_iva(invoice.tax_line)

    if base_imponible:
        tipo_desglose = {
            'DesgloseFactura': {
                'Sujeta': {
                    'NoExenta': {  # TODO Exenta o no exenta??
                        'TipoNoExenta': 'S1',  # TODO to change
                        'DesgloseIVA': {
                            'DetalleIVA': {
                                'TipoImpositivo': '',
                                'BaseImponible': base_imponible,
                                'CuotaRepercutida': '0'  # TODO
                            }
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
        'ClaveRegimenEspecialOTrascendencia': '',
        'ImporteTotal': invoice.amount_total,
        'DescripcionOperacion': '',
        'Contraparte': {
            'NombreRazon': '',
            'NIF': ''
        },
        'TipoDesglose': tipo_desglose
    }

    return factura_expedida


def get_factura_recibida(invoice):

    base_imponible = get_base_imponible_iva(invoice.tax_line)

    if base_imponible:
        tipo_desglose = {
            'DesgloseFactura': {
                'Sujeta': {
                    'NoExenta': {  # TODO Exenta o no exenta??
                        'TipoNoExenta': 'S1',  # TODO to change
                        'DesgloseIVA': {
                            'DetalleIVA': {
                                'TipoImpositivo': '',
                                'BaseImponible': base_imponible,
                                'CuotaRepercutida': '0'  # TODO
                            }
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

    factura_recibida = {
        'TipoFactura': 'F1',
        'ClaveRegimenEspecialOTrascendencia': '',
        'ImporteTotal': invoice.amount_total,
        'DescripcionOperacion': '',
        'Contraparte': {
            'NombreRazon': '',
            'NIF': ''
        },
        'TipoDesglose': tipo_desglose
    }

    return factura_recibida


def get_header(invoice):
    cabecera = {
        'IDVersionSii': __SII_VERSION__,
        'Titular': {
            'NombreRazon': invoice.partner_id.name,
            'NIF': invoice.partner_id.nif
        },
        'TipoComunicacion': 'A0'
    }

    return cabecera


def get_factura_emitida_dict(invoice):

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
                        'NIF': ''
                    },
                    'NumSerieFacturaEmisor': invoice.number,
                    'FechaExpedicionFacturaEmisor': datetime.strptime(
                        invoice.date_invoice, '%Y-%m-%d'
                    ).strftime('%d-%m-%Y')
                },
                'FacturaExpedida': get_factura_expedida(invoice)
            }
        }
    }

    return obj


def get_factura_recibida_dict(invoice):

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
                        'NIF': ''
                    },
                    'NumSerieFacturaEmisor': invoice.number,
                    'FechaExpedicionFacturaEmisor': datetime.strptime(
                        invoice.date_invoice, '%Y-%m-%d'
                    ).strftime('%d-%m-%Y')
                },
                'FacturaRecibida': get_factura_recibida(invoice)
            }
        }
    }

    return obj


class SII(object):
    @staticmethod
    def generate_object(invoice):

        if invoice.type == 'in_invoice':
            invoice_model = models.SuministroFacturasRecibidas()
            invoice_dict = get_factura_recibida_dict(invoice)
        elif invoice.type == 'out_invoice':
            invoice_model = models.SuministroFacturasEmitidas()
            invoice_dict = get_factura_emitida_dict(invoice)
        else:
            raise Exception('Error in invoice.type')

        errors = invoice_model.validate(invoice_dict)
        if errors:
            raise Exception(
                'Errors were found while trying to generate the dump:', errors)

        res = invoice_model.dump(invoice_dict).data
        return res
