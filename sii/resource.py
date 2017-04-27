# coding=utf-8
from sii import models, __SII_VERSION__


class FacturasEmitidasDictGenerator(models.SuministroFacturasEmitidas):

    def dump(self, invoice, many=None, update_fields=True, **kwargs):
        base_imponible = ''
        for tax in invoice.tax_line:
            if 'IVA' in tax.name:
                base_imponible = tax.base
                break
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
                    'NoSujeta': {

                    }
                }
            }

        factura_expedida = {
            'TipoFactura': '',
            'ClaveRegimenEspecialOTrascendencia': '',
            'ImporteTotal': '',
            'DescripcionOperacion': '',
            'Contraparte': {
                'NombreRazon': '',
                'NIF': ''
            },
            'TipoDesglose': {
                'DesgloseFactura': {
                    'Sujeta': ''
                }
            }
        }

        new_obj = {
            'SuministroLRFacturasEmitidas': {
                'Cabecera': {
                    'IDVersionSii': __SII_VERSION__,
                    'Titular': {
                        'NombreRazon': invoice.partner_id.name,
                        'NIF': invoice.partner_id.nif
                    },
                    'TipoComunicacion': 'A0'
                },
                'RegistroLRFacturasEmitidas': {
                    'PeriodoImpositivo': {
                        'Ejercicio': '',
                        'Periodo': ''
                    },
                    'IDFactura': {
                        'IDEmisorFactura': {
                            'NIF': ''
                        },
                        'NumSerieFacturaEmisor': invoice.number,
                        'FechaExpedicionFacturaEmisor': ''
                    },
                    # 'FacturaExpedida': factura_expedida
                }
            }
        }

        object_generated = self.load(new_obj)
        errors = object_generated.errors
        if errors:
            raise Exception(
                'Errors were found while trying to generate the dump', errors)

        res = super(models.SuministroFacturasEmitidas, self).dump(
            new_obj, many, update_fields, **kwargs)

        return res


class SII(object):
    @staticmethod
    def generate_object(invoice):

        if invoice.type == 'in_invoice':
            invoice_model = models.SuministroFacturasRecibidas()
        elif invoice.type == 'out_invoice':
            invoice_model = FacturasEmitidasDictGenerator()
        else:
            raise Exception('Error in invoice.type')

        res = invoice_model.dump(invoice).data
        return res
