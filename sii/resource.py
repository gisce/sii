# coding=utf-8
import re
from copy import deepcopy
from unidecode import unidecode
from decimal import Decimal, localcontext

from sii import __SII_VERSION__
from sii.models import invoices_record

SIGN = {'N': 1, 'R': 1, 'A': -1, 'B': -1, 'RA': 1, 'C': 1, 'G': 1}  # 'BRA': -1


def get_invoice_sign(invoice):
    if invoice.type.endswith('refund'):
        return -1
    return 1


def get_iva_values(invoice, in_invoice, is_export=False, is_import=False):
    """

    :param invoice:
    :param in_invoice: indica si es una factura recibida
    :type in_invoice: bool
    :param is_export: indica si es una exportación
    :type  is_export: bool
    :param is_import: indica si es una importación
    :type is_import: bool
    :return:
    """
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
    # iva_values es un diccionario que agrupa los valores del IVA por el tipo
    # impositivo. ejemplo:
    #
    # iva_values = {
    #     21.0: {
    #         'BaseImponible': ...,
    #         'TipoImpositivo': ...,
    #         'Cuota...': ...
    #     },
    #     18.0: {
    #         'BaseImponible': ...,
    #         'TipoImpositivo': ...,
    #         'Cuota...': ...
    #     }
    # }
    iva_values = {}

    for inv_tax in invoice.tax_line:
        if 'iva' in inv_tax.name.lower():
            vals['sujeta_a_iva'] = True

            if invoice_total < 0:
                invoice_total += (abs(inv_tax.tax_amount) + abs(inv_tax.base))
            else:
                invoice_total -= (abs(inv_tax.tax_amount) + abs(inv_tax.base))

            is_iva_exento = (
                inv_tax.tax_id.amount == 0 and inv_tax.tax_id.type == 'percent'
            )
            # IVA 0% Exportaciones y IVA 0% Importaciones tienen amount 0 y se
            # detectan como IVA exento
            if not is_export and not is_import and is_iva_exento:
                vals['iva_exento'] = True
                vals['detalle_iva_exento']['BaseImponible'] += inv_tax.base
            else:
                sign = get_invoice_sign(invoice)
                tipo_impositivo = inv_tax.tax_id.amount * 100
                base_imponible = sign * abs(inv_tax.base)
                if in_invoice:
                    cuota_key = 'CuotaSoportada'
                else:
                    cuota_key = 'CuotaRepercutida'
                cuota = sign * abs(inv_tax.tax_amount)
                if tipo_impositivo in iva_values:
                    aux = iva_values[tipo_impositivo]
                    aux['BaseImponible'] += base_imponible
                    aux[cuota_key] += cuota
                else:
                    iva = {
                        'BaseImponible': base_imponible,
                        'TipoImpositivo': tipo_impositivo,
                        cuota_key: cuota
                    }
                    iva_values[tipo_impositivo] = iva
                vals['iva_no_exento'] = True

    vals['detalle_iva'] = iva_values.values()

    invoice_total = round(invoice_total, 2)
    if invoice_total != 0:
        vals['no_sujeta_a_iva'] = True
        vals['importe_no_sujeto'] = invoice_total

    return vals


def get_rectified_iva_values(invoice, in_invoice=False,
                             is_export=False, is_import=False):
    """

    :param invoice:
    :param in_invoice: indica si es una factura recibida
    :type in_invoice: bool
    :param is_export: indica si es una exportación
    :type  is_export: bool
    :param is_import: indica si es una importación
    :type is_import: bool
    :return:
    """
    iva_values = get_iva_values(
        invoice, in_invoice=in_invoice,
        is_export=is_export, is_import=is_import
    )
    factura_rectificada = invoice.rectifying_id
    f_rect_iva = get_iva_values(
        factura_rectificada, in_invoice=in_invoice,
        is_export=is_export, is_import=is_import
    )

    aux_iva_values = {}

    cuota_key = 'CuotaSoportada' if in_invoice else 'CuotaRepercutida'

    for inv_iva in iva_values['detalle_iva']:
        tipo_impositivo = inv_iva['TipoImpositivo']
        base_imponible = inv_iva['BaseImponible']
        cuota = inv_iva[cuota_key]
        if tipo_impositivo in aux_iva_values:
            aux = aux_iva_values[tipo_impositivo]
            aux['BaseImponible'] += base_imponible
            aux[cuota_key] += cuota
        else:
            aux_iva_values[tipo_impositivo] = inv_iva.copy()

    for rect_iva in f_rect_iva['detalle_iva']:
        tipo_impositivo = rect_iva['TipoImpositivo']
        base_imponible = rect_iva['BaseImponible']
        cuota = rect_iva[cuota_key]
        if tipo_impositivo in aux_iva_values:
            aux = aux_iva_values[tipo_impositivo]
            aux['BaseImponible'] -= base_imponible
            aux[cuota_key] -= cuota
        else:
            aux_iva_values[tipo_impositivo] = {
                'TipoImpositivo': tipo_impositivo,
                'BaseImponible': -base_imponible,
                cuota_key: -cuota
            }

    return aux_iva_values.values()


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


def get_factura_emitida_tipo_desglose(invoice, rect_diferencias=False):
    in_invoice = False
    is_export = invoice.sii_out_clave_regimen_especial == '02'  # Exportación
    iva_values = get_iva_values(
        invoice, in_invoice=in_invoice, is_export=is_export
    )

    if bool(is_export):
        if iva_values['sujeta_a_iva']:
            new_iva_values = iva_values['detalle_iva']

            if rect_diferencias:
                new_iva_values = get_rectified_iva_values(
                    invoice, in_invoice=in_invoice, is_export=is_export
                )

            entrega = {
                'Sujeta': {
                    'NoExenta': {
                        'TipoNoExenta': 'S1',
                        'DesgloseIVA': {
                            'DetalleIVA': new_iva_values
                        }
                    }
                }
            }
        else:
            detalle_iva_exento = iva_values['detalle_iva_exento']

            if rect_diferencias:
                factura_rectificada = invoice.rectifying_id
                f_rect_iva = get_iva_values(
                    factura_rectificada, in_invoice=in_invoice,
                    is_export=is_export
                )
                f_rect_detalle_iva_exento = f_rect_iva['detalle_iva_exento']
                if f_rect_detalle_iva_exento:
                    detalle_iva_exento['BaseImponible'] -= (
                        f_rect_detalle_iva_exento['BaseImponible']
                    )

            entrega = {
                'Sujeta': {
                    'Exenta': detalle_iva_exento
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
        desglose = {}
        detalle_iva_exento = iva_values['detalle_iva_exento']
        new_iva_values = iva_values['detalle_iva']
        importe_no_sujeto = iva_values['importe_no_sujeto']

        if rect_diferencias:
            new_iva_values = get_rectified_iva_values(
                invoice, in_invoice=in_invoice, is_export=is_export
            )

            factura_rectificada = invoice.rectifying_id
            f_rect_iva = get_iva_values(
                factura_rectificada, in_invoice=in_invoice,
                is_export=is_export
            )
            f_rect_detalle_iva_exento = f_rect_iva['detalle_iva_exento']
            if f_rect_detalle_iva_exento:
                detalle_iva_exento['BaseImponible'] -= (
                    f_rect_detalle_iva_exento['BaseImponible']
                )

            importe_no_sujeto -= f_rect_iva['importe_no_sujeto']

        if iva_values['sujeta_a_iva']:
            desglose['Sujeta'] = {}
            if iva_values['iva_exento']:
                desglose['Sujeta']['Exenta'] = detalle_iva_exento
            if iva_values['iva_no_exento']:
                desglose['Sujeta']['NoExenta'] = {
                    'TipoNoExenta': 'S1',
                    'DesgloseIVA': {
                        'DetalleIVA': new_iva_values
                    }
                }
        if iva_values['no_sujeta_a_iva']:
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


def get_factura_rectificativa_sustitucion_fields():
    rectificativa_fields = {
        'ImporteRectificacion': {
            'BaseRectificada': 0,
            'CuotaRectificada': 0
        }
    }

    return rectificativa_fields


def get_factura_emitida(invoice,
                        rect_sustitucion=False, rect_diferencias=False):

    factura_expedida = {
        'TipoFactura': 'R4' if invoice.rectificative_type == 'R' else 'F1',
        'ClaveRegimenEspecialOTrascendencia':
            invoice.sii_out_clave_regimen_especial,
        'ImporteTotal': get_invoice_sign(invoice) * invoice.amount_total,
        'DescripcionOperacion': invoice.sii_description,
        'Contraparte': get_contraparte(invoice.partner_id, in_invoice=False),
        'TipoDesglose': get_factura_emitida_tipo_desglose(
            invoice, rect_diferencias=rect_diferencias)
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

    if rect_sustitucion:
        vals = get_factura_rectificativa_sustitucion_fields()
        factura_expedida['TipoRectificativa'] = 'S'  # Por sustitución
        factura_expedida.update(vals)
    if rect_diferencias:
        factura_rectificada = invoice.rectifying_id

        importe_total = invoice.amount_total - factura_rectificada.amount_total
        factura_expedida.update({
            'ImporteTotal': importe_total,
            'TipoRectificativa': 'I'  # Por diferencias
        })

    return factura_expedida


def get_factura_recibida(invoice,
                         rect_sustitucion=False, rect_diferencias=False):
    in_invoice = True
    # Factura correspondiente a una importación (informada sin asociar a un DUA)
    is_import = invoice.sii_in_clave_regimen_especial == '13'
    iva_values = get_iva_values(
        invoice, in_invoice=in_invoice, is_import=is_import
    )

    cuota_deducible = 0
    importe_total = get_invoice_sign(invoice) * invoice.amount_total

    if iva_values['sujeta_a_iva'] and iva_values['iva_no_exento']:
        if rect_diferencias:
            new_iva_values = get_rectified_iva_values(
                invoice, in_invoice=in_invoice, is_import=is_import
            )
        else:
            new_iva_values = iva_values['detalle_iva']

        desglose_factura = {  # TODO to change
            # 'InversionSujetoPasivo': {
            #     'DetalleIVA': iva_values['detalle_iva']
            # },
            'DesgloseIVA': {
                'DetalleIVA': new_iva_values
            }
        }

        for detalle_iva in new_iva_values:
            cuota_deducible += detalle_iva['CuotaSoportada']
    else:
        base_imponible_factura = invoice.amount_untaxed

        if rect_diferencias:
            factura_rectificada = invoice.rectifying_id
            base_imponible_factura -= factura_rectificada.amount_untaxed

        desglose_factura = {
            'DesgloseIVA': {
                'DetalleIVA': [{
                    'BaseImponible': base_imponible_factura
                }]
            }
        }

    factura_recibida = {
        'TipoFactura': 'R4' if invoice.rectificative_type == 'R' else 'F1',
        'ClaveRegimenEspecialOTrascendencia':
            invoice.sii_in_clave_regimen_especial,
        'ImporteTotal': importe_total,
        'DescripcionOperacion': invoice.sii_description,
        'Contraparte': get_contraparte(
            invoice.partner_id, in_invoice=in_invoice),
        'DesgloseFactura': desglose_factura,
        'CuotaDeducible': cuota_deducible,
        'FechaRegContable': invoice.date_invoice
    }

    if rect_sustitucion:
        vals = get_factura_rectificativa_sustitucion_fields()
        factura_recibida['TipoRectificativa'] = 'S'  # Por sustitución
        factura_recibida.update(vals)
    if rect_diferencias:
        factura_rectificada = invoice.rectifying_id
        importe_total = invoice.amount_total - factura_rectificada.amount_total
        factura_recibida.update({
            'ImporteTotal': importe_total,
            'TipoRectificativa': 'I'  # Por diferencias
        })

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


def get_factura_emitida_dict(invoice,
                             rect_sustitucion=False, rect_diferencias=False):
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
                'FacturaExpedida': get_factura_emitida(
                    invoice, rect_sustitucion, rect_diferencias
                )
            }
        }
    }

    return obj


def get_factura_recibida_dict(invoice,
                              rect_sustitucion=False, rect_diferencias=False):
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
                'FacturaRecibida': get_factura_recibida(
                    invoice, rect_sustitucion, rect_diferencias
                )
            }
        }
    }

    return obj


def refactor_nifs(invoice):
    for partner in (invoice.partner_id, invoice.company_id.partner_id):
        if partner.vat:
            # partner.vat = re.sub('^ES', '', partner.vat.upper())
            partner.vat = partner.vat[2:]


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

        rectified_invoice.amount_total = transform(
            rectified_invoice.amount_total)
        rectified_invoice.amount_untaxed = transform(
            rectified_invoice.amount_untaxed)

        for rect_inv_tax in rectified_invoice.tax_line:
            rect_inv_tax.tax_amount = transform(rect_inv_tax.tax_amount)
            rect_inv_tax.base = transform(rect_inv_tax.base)
            rect_inv_tax.tax_id.amount = transform(rect_inv_tax.tax_id.amount)


class SII(object):
    def __init__(self, invoice):
        self.invoice = invoice
        refactor_nifs(self.invoice)
        refactor_decimals(self.invoice)
        tipo_rectificativa = invoice.rectificative_type
        rectificativa_sustitucion = tipo_rectificativa == 'R'
        rectificativa_diferencias = tipo_rectificativa == 'RA'
        if invoice.type.startswith('in'):
            self.invoice_model = invoices_record.SuministroFacturasRecibidas()
            self.invoice_dict = get_factura_recibida_dict(
                invoice=self.invoice,
                rect_sustitucion=rectificativa_sustitucion,
                rect_diferencias=rectificativa_diferencias
            )
        elif invoice.type.startswith('out'):
            self.invoice_model = invoices_record.SuministroFacturasEmitidas()
            self.invoice_dict = get_factura_emitida_dict(
                invoice=self.invoice,
                rect_sustitucion=rectificativa_sustitucion,
                rect_diferencias=rectificativa_diferencias
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
        res['object_validated'] = self.invoice_dict
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
