# coding=utf-8
from sii import models, __SII_VERSION__


class FacturasEmitidasDictGenerator(models.SuministroFacturasEmitidas):

    def generate_object(self, invoice, many=None, update_fields=True, **kwargs):
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

        return super(models.SuministroFacturasEmitidas, self).dump(
            new_obj, many, update_fields, **kwargs)


class SII(object):
    @staticmethod
    def generate_object(invoice):

        if invoice.type == 'in_invoice':
            invoice_model = models.SuministroFacturasRecibidas()
        elif invoice.type == 'out_invoice':
            invoice_model = FacturasEmitidasDictGenerator()
        else:
            raise Exception('Error in invoice.type')

        return invoice_model.generate_object(invoice).data
