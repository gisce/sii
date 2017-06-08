# -*- coding: UTF-8 -*-

from sii.resource import SII
from zeep import Client
from requests import Session
from zeep.exceptions import Fault
from zeep.transports import Transport
from zeep.helpers import serialize_object

from sii import __SII_VERSION__

MAX_ID_CHECKS = 9999


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class Service(object):
    def __init__(self, certificate, key, url=None):
        self.certificate = certificate
        self.key = key
        self.url = url

    def create_service(self, config):
        session = Session()
        session.cert = (self.certificate, self.key)
        session.verify = False
        transport = Transport(session=session)

        client = Client(wsdl=config['wsdl'], port_name=config['port_name'],
                        transport=transport, service_name=config['service_name']
                        )
        if not self.url:
            return client.service
        address = '{0}{1}'.format(self.url, config['type_address'])
        service = client.create_service(config['binding_name'], address)
        return service


class IDService(Service):
    def __init__(self, certificate, key, url=None):
        super(IDService, self).__init__(certificate, key, url)
        self.validator_service = None

    def ids_validate(self, partners, max_id_checks=MAX_ID_CHECKS):
        self.validator_service = self.create_validation_service()

        res = []
        try:
            partner_chunks = chunks(partners, max_id_checks)
            for chunk in partner_chunks:
                res.extend(self.send_validate_chunk(chunk=chunk))
            return serialize_object(res)
        except Fault as fault:
            raise fault

    def send_validate_chunk(self, chunk):
        for partner in chunk:
            partner['Nif'] = partner.pop('vat')
            partner['Nombre'] = partner.pop('name')
        return self.validator_service.VNifV2(chunk)

    def invalid_ids(self, partners, max_id_checks=MAX_ID_CHECKS):
        res = self.ids_validate(partners, max_id_checks)
        invalid_ids = []
        for partner in res:
            if partner['Resultado'] == 'NO IDENTIFICADO':
                invalid_ids.append(partner)
        return serialize_object(invalid_ids)

    def create_validation_service(self):
        config = self.configs['ids_validator_v2'].copy()
        return super(IDService, self).create_service(config)

    configs = {
        'ids_validator_v2': {
            'wsdl': 'https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/burt/jdit/ws/VNifV2.wsdl',
            'port_name': 'VNifPort1',
            'binding_name': '{http://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/burt/jdit/ws/VNifV2.wsdl}VNifV2SoapBinding',
            'type_address': '/wlpl/BURT-JDIT/ws/VNifV2SOAP',
            'service_name': 'VNifV2Service'
        }
    }


class SiiService(Service):
    def __init__(self, certificate, key, url=None, test_mode=False):
        super(SiiService, self).__init__(certificate, key, url)
        self.test_mode = True  # Force now work in test mode
        self.emitted_service = None
        self.received_service = None
        self.url = url
        self.invoice = None
        self.query = None
        self.type = None

    def send_invoice(self, invoice):
        self.type = 'invoice'
        self.invoice = invoice
        if self.invoice.type.startswith('out_'):
            if self.emitted_service is None:
                config = self.configs['out_inv_config'].copy()
                self.emitted_service = self.create_service(config)
        else:
            if self.received_service is None:
                config = self.configs['in_inv_config'].copy()
                self.received_service = self.create_service(config)
        return self.send()

    def query_invoice(self, inv_type, nif_titular, name_titular, ejercicio,
                      periodo, nif_contraparte=None, name_contraparte=None,
                      num_invoice=None, date_invoice=None):
        self.type = 'query'
        self.query = {
            'type': inv_type,
            'query': {
                'ConsultaLRFacturasEmitidas': {
                    'Cabecera': {
                        'IDVersionSii': __SII_VERSION__,
                        'Titular': {
                            'NombreRazon': name_titular,
                            'NIF': nif_titular
                        },
                    },
                    'FiltroConsulta': {
                        'PeriodoImpositivo': {
                            'Ejercicio': ejercicio,
                            'Periodo': periodo
                        }
                    }
                }
            }
        }
        if self.query['type'].startswith('out_'):
            if self.emitted_service is None:
                config = self.configs['out_inv_config'].copy()
                self.emitted_service = self.create_service(config)
        else:
            if self.received_service is None:
                config = self.configs['in_inv_config'].copy()
                self.received_service = self.create_service(config)
        return self.send()

    def create_service(self, config):
        if self.test_mode:
            config['port_name'] += 'Pruebas'
        return super(SiiService, self).create_service(config)

    def send(self):
        msg_header, msg_invoice = self.get_msg()
        try:
            if self.type == 'query':
                if self.query['type'].startswith('out_'):
                    res = self.emitted_service.ConsultaLRFacturasEmitidas(
                        msg_header, msg_invoice)
                elif self.query['type'].startswith('in_'):
                    res = self.received_service.ConsultaLRFacturasRecibidas(
                        msg_header, msg_invoice)
            else:
                if self.invoice.type.startswith('out_'):
                    res = self.emitted_service.SuministroLRFacturasEmitidas(
                        msg_header, msg_invoice)
                elif self.invoice.type.startswith('in_'):
                    res = self.received_service.SuministroLRFacturasRecibidas(
                        msg_header, msg_invoice)

            return serialize_object(res)
        except Exception as fault:
            raise fault

    def get_msg(self):
        dict_from_marsh = SII(self.invoice).generate_object()
        res_header = res_invoices = None
        if self.invoice.type.startswith('out_'):
            res_header = dict_from_marsh['SuministroLRFacturasEmitidas'][
                'Cabecera']
            res_invoices = dict_from_marsh['SuministroLRFacturasEmitidas'][
                'RegistroLRFacturasEmitidas']
        elif self.invoice.type.startswith('in_'):
            res_header = dict_from_marsh['SuministroLRFacturasRecibidas'][
                'Cabecera']
            res_invoices = dict_from_marsh['SuministroLRFacturasRecibidas'][
                'RegistroLRFacturasRecibidas']

        return res_header, res_invoices

    configs = {
        'out_inv_config': {
            'wsdl': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_07/SuministroFactEmitidas.wsdl',
            'port_name': 'SuministroFactEmitidas',
            'binding_name': '{https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroFactEmitidas.wsdl}siiBinding',
            'type_address': '/wlpl/SSII-FACT/ws/fe/SiiFactFEV1SOAP',
            'service_name': 'siiService'
        },
        'in_inv_config': {
            'wsdl': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_07/SuministroFactRecibidas.wsdl',
            'port_name': 'SuministroFactRecibidas',
            'binding_name': '{https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroFactRecibidas.wsdl}siiBinding',
            'type_address': '/wlpl/SSII-FACT/ws/fr/SiiFactFRV1SOAP',
            'service_name': 'siiService'
        }
    }
