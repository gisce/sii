# coding=utf-8
import re
from unidecode import unidecode

from sii import __SII_VERSION__
from sii.models import invoices_record

SIGN = {'B': -1, 'A': -1, 'N': 1, 'R': 1}


def get_iva_values(invoice, in_invoice, is_export=False, is_import=False):
    vals = {
        'sujeta_a_iva': False,
        'detalle_iva': [],
        'no_sujeta_a_iva': False,
        'iva_exento': False,
        'iva_no_exento': False,
        'detalle_iva_exento': {'BaseImponible': 0},
        'importe_no_sujeto': 0
    }

    invoice_total = invoice.amount_total

    for inv_tax in invoice.tax_line:
        if 'iva' in inv_tax.name.lower():
            vals['sujeta_a_iva'] = True

            invoice_total -= (abs(inv_tax.tax_amount) + abs(inv_tax.base))

            is_iva_exento = (
                inv_tax.tax_id.amount == 0 and inv_tax.tax_id.type == 'percent'
            )
            if not is_export and not is_import and is_iva_exento:
                vals['iva_exento'] = True
                vals['detalle_iva_exento']['BaseImponible'] += inv_tax.base
            else:
                sign = SIGN[invoice.rectificative_type]
                iva = {
                    'BaseImponible': sign * abs(inv_tax.base),
                    'TipoImpositivo': inv_tax.tax_id.amount * 100
                }
                if in_invoice:
                    iva['CuotaSoportada'] = sign * abs(inv_tax.tax_amount)
                else:
                    iva['CuotaRepercutida'] = sign * abs(inv_tax.tax_amount)
                vals['iva_no_exento'] = True
                vals['detalle_iva'].append(iva)

    invoice_total = round(invoice_total, 2)
    if invoice_total > 0:
        vals['no_sujeta_a_iva'] = True
        vals['importe_no_sujeto'] = invoice_total

    return vals


def get_contraparte(partner, in_invoice):
    vat_type = partner.sii_get_vat_type()
    contraparte = {'NombreRazon': unidecode(partner.name)}

    partner_country = partner.country_id or partner.country

    if vat_type == '02':
        if not partner.aeat_registered and not in_invoice:
            contraparte['IDOtro'] = {
                'CodigoPais': partner_country.code,
                'IDType': '07',
                'ID': partner.vat
            }
        else:
            contraparte['NIF'] = partner.vat
    else:
        contraparte['IDOtro'] = {
            'CodigoPais': partner_country.code,
            'IDType': vat_type,
            'ID': partner.vat
        }

    return contraparte


def get_factura_emitida_tipo_desglose(invoice):

    if invoice.sii_out_clave_regimen_especial == '02':  # Exportación
        iva_values = get_iva_values(invoice, in_invoice=False, is_export=True)

        if iva_values['sujeta_a_iva']:
            entrega = {
                'Sujeta': {
                    'NoExenta': {
                        'TipoNoExenta': 'S1',
                        'DesgloseIVA': {
                            'DetalleIVA': iva_values['detalle_iva']
                        }
                    }
                }
            }
        else:
            entrega = {
                'Sujeta': {
                    'Exenta': iva_values['detalle_iva_exento']
                }
            }
            # Exenta por el artículo 21
            entrega['Sujeta']['Exenta']['CausaExencion'] = 'E2'

        tipo_desglose = {
            'DesgloseTipoOperacion': {
                'Entrega': entrega
            }
        }
    else:
        iva_values = get_iva_values(invoice, in_invoice=False)
        desglose = {}

        if iva_values['sujeta_a_iva']:
            desglose['Sujeta'] = {}
            if iva_values['iva_exento']:
                desglose['Sujeta']['Exenta'] = iva_values['detalle_iva_exento']
            if iva_values['iva_no_exento']:
                desglose['Sujeta']['NoExenta'] = {
                    'TipoNoExenta': 'S1',
                    'DesgloseIVA': {
                        'DetalleIVA': iva_values['detalle_iva']
                    }
                }
        if iva_values['no_sujeta_a_iva']:
            importe_no_sujeto = iva_values['importe_no_sujeto']

            fp = invoice.fiscal_position
            if fp and 'islas canarias' in unidecode(fp.name.lower()):
                desglose['NoSujeta'] = {
                    'ImporteTAIReglasLocalizacion': importe_no_sujeto
                }
            else:
                desglose['NoSujeta'] = {
                    'ImportePorArticulos7_14_Otros': importe_no_sujeto
                }

        partner_vat = invoice.partner_id.vat
        partner_vat_starts_with_n = (
            partner_vat and partner_vat.upper().startswith('N')
        )
        has_id_otro = invoice.partner_id.sii_get_vat_type() != '02'
        if has_id_otro or partner_vat_starts_with_n:
            tipo_desglose = {
                'DesgloseTipoOperacion': {
                    'PrestacionServicios': desglose
                }
            }
        else:
            tipo_desglose = {
                'DesgloseFactura': desglose
            }

    return tipo_desglose


def get_factura_emitida(invoice):

    factura_expedida = {
        'TipoFactura': 'R4' if invoice.rectificative_type == 'R' else 'F1',
        'ClaveRegimenEspecialOTrascendencia':
            invoice.sii_out_clave_regimen_especial,
        'ImporteTotal': SIGN[invoice.rectificative_type] * invoice.amount_total,
        'DescripcionOperacion':
            invoice.journal_id.sii_description or invoice.journal_id.name,
        'Contraparte': get_contraparte(invoice.partner_id, in_invoice=False),
        'TipoDesglose': get_factura_emitida_tipo_desglose(invoice)
    }

    # Si la factura es una operación de arrendamiento
    # de local de negocio (alquiler)
    if invoice.sii_out_clave_regimen_especial in ['12', '13']:
        detalle_inmueble = {}

        codigo_comunidad_autonoma = \
            invoice.address_contact_id.state_id.comunitat_autonoma.codi

        # '01', '02', ..., '19': Comunidades autónomas de España
        if codigo_comunidad_autonoma in [str(s).zfill(2) for s in range(1, 20)]:
            ref_catastral = invoice.address_contact_id.ref_catastral
            if ref_catastral:
                detalle_inmueble['ReferenciaCatastral'] = ref_catastral

                # '15': Comunidad Foral de Navarra
                # '16': País Vasco
                if codigo_comunidad_autonoma not in ['15', '16']:
                    situacion_inmueble = '1'
                else:
                    situacion_inmueble = '2'
            else:
                situacion_inmueble = '3'
        else:
            situacion_inmueble = '4'

        detalle_inmueble['SituacionInmueble'] = situacion_inmueble

        factura_expedida['DatosInmueble'] = {
            'DetalleInmueble': detalle_inmueble
        }

    return factura_expedida


def get_factura_recibida(invoice):
    cuota_deducible = 0

    # Factura correspondiente a una importación (informada sin asociar a un DUA
    if invoice.sii_in_clave_regimen_especial == '13':
        iva_values = get_iva_values(invoice, in_invoice=True, is_import=True)
    else:
        iva_values = get_iva_values(invoice, in_invoice=True)

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
                'DetalleIVA': [{
                    'BaseImponible': invoice.amount_untaxed
                }]
            }
        }

    factura_recibida = {
        'TipoFactura': 'R4' if invoice.rectificative_type == 'R' else 'F1',
        'ClaveRegimenEspecialOTrascendencia':
            invoice.sii_in_clave_regimen_especial,
        'ImporteTotal': SIGN[invoice.rectificative_type] * invoice.amount_total,
        'DescripcionOperacion':
            invoice.journal_id.sii_description or invoice.journal_id.name,
        'Contraparte': get_contraparte(invoice.partner_id, in_invoice=True),
        'DesgloseFactura': desglose_factura,
        'CuotaDeducible': cuota_deducible,
        'FechaRegContable': invoice.date_invoice
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
                    'FechaExpedicionFacturaEmisor': invoice.origin_date_invoice
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
        if partner.vat:
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
            raise AttributeError(
                'Valor desconocido en el tipo de factura: {}'.format(
                    invoice.type
                )
            )

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

        errors = self.invoice_model.validate(self.invoice_dict)

        res['successful'] = False if errors else True
        if errors:
            errors_list = self.get_validation_errors_list(errors)
            res['errors'] = errors_list

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
