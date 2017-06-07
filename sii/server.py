# -*- coding: UTF-8 -*-

from sii.resource import SII
from zeep import Client
from requests import Session
from zeep.exceptions import Fault
from zeep.transports import Transport
from zeep.helpers import serialize_object

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
        self.result = []


class IDService(Service):
    def __init__(self, certificate, key, url=None):
        super(IDService, self).__init__(certificate, key, url)
        self.validator_service = None

    def ids_validate(self, partners, max_id_checks=MAX_ID_CHECKS):
        self.validator_service = self.create_validation_service(partners)

        res = []
        try:
            if isinstance(partners, list):
                partner_chunks = chunks(partners, max_id_checks)
                for chunk in partner_chunks:
                    res.extend(self.send_validate_chunk(chunk=chunk))
            else:
                partners['Nif'] = partners.pop('vat')
                partners['Nombre'] = partners.pop('name')
                res = self.validator_service.VNifV1(
                    partners['Nif'], partners['Nombre']
                )
            return serialize_object(res)
        except Fault as fault:
            self.result = fault
            if self.result.message != 'Codigo[-1].No identificado':
                raise fault

    def send_validate_chunk(self, chunk):
        for partner in chunk:
            partner['Nif'] = partner.pop('vat')
            partner['Nombre'] = partner.pop('name')
        return self.validator_service.VNifV2(chunk)

    def invalid_ids(self, partners, max_id_checks=MAX_ID_CHECKS):
        res = self.ids_validate(partners, max_id_checks)
        invalid_ids = []
        if isinstance(partners, list):
            for partner in res:
                if partner['Resultado'] == 'NO IDENTIFICADO':
                    invalid_ids.append(partner)
        else:
            if isinstance(res, Exception) and res.message == 'Codigo[-1].No identificado':
                return partners
        return serialize_object(invalid_ids)

    def create_validation_service(self, partners):
        port_name = 'VNifPort1'
        type_address = '/wlpl/BURT-JDIT/ws/VNifV1SOAP'
        binding_name = '{http://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/burt/jdit/ws/VNifV1.wsdl}VNifV1SoapBinding'
        service_name = 'VNifV1Service'
        wsdl = self.wsdl_files['ids_validator_v1']
        if isinstance(partners, list):
            type_address = '/wlpl/BURT-JDIT/ws/VNifV2SOAP'
            binding_name = '{http://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/burt/jdit/ws/VNifV2.wsdl}VNifV2SoapBinding'
            service_name = 'VNifV2Service'
            wsdl = self.wsdl_files['ids_validator_v2']
        session = Session()
        session.cert = (self.certificate, self.key)
        session.verify = False
        transport = Transport(session=session)

        client = Client(wsdl=wsdl, port_name=port_name, transport=transport,
                        service_name=service_name)
        if not self.url:
            return client.service
        address = '{0}{1}'.format(self.url, type_address)
        service = client.create_service(binding_name, address)
        return service

    wsdl_files = {
        'ids_validator_v1': 'https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/burt/jdit/ws/VNifV1.wsdl',
        'ids_validator_v2': 'https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/burt/jdit/ws/VNifV2.wsdl'
    }


class SiiService(Service):
    def __init__(self, certificate, key, url=None, test_mode=False):
        super(SiiService, self).__init__(certificate, key, url)
        self.test_mode = True  # Force now work in test mode
        self.emitted_service = None
        self.received_service = None
        self.url = url
        self.invoice = None

    def send(self, invoice):
        self.invoice = invoice
        if self.invoice.type.startswith('out_'):
            if self.emitted_service is None:
                self.emitted_service = self.create_service()
        else:
            if self.received_service is None:
                self.received_service = self.create_service()
        return self.send_invoice()

    def create_service(self):
        session = Session()
        session.cert = (self.certificate, self.key)
        session.verify = False
        transport = Transport(session=session)
        if self.invoice.type.startswith('out_'):
            config = self.out_inv_config.copy()
        else:
            config = self.in_inv_config.copy()
        port_name = config['port_name']
        if self.test_mode:
            port_name += 'Pruebas'

        client = Client(wsdl=config['wsdl'], port_name=port_name,
                        transport=transport, service_name=config['service_name']
                        )
        if not self.url:
            return client.service
        address = '{0}{1}'.format(self.url, config['type_address'])
        service = client.create_service(config['binding_name'], address)
        return service

    def send_invoice(self):
        msg_header, msg_invoice = self.get_msg()
        try:
            if self.invoice.type.startswith('out_'):
                res = self.emitted_service.SuministroLRFacturasEmitidas(
                    msg_header, msg_invoice)
            elif self.invoice.type.startswith('in_'):
                res = self.received_service.SuministroLRFacturasRecibidas(
                    msg_header, msg_invoice)
            self.result = res
            return serialize_object(self.result)
        except Exception as fault:
            self.result = fault
            raise fault

    # def list_invoice(self, invoice):
    #     msg_header, msg_invoice = self.get_msg(invoice)
    #     try:
    #         if invoice.type == 'in_invoice':
    #             res = self.received_service.ConsultaLRFacturasRecibidas(
    #                 msg_header, msg_invoice)
    #             if res['EstadoEnvio'] == 'Correcto':
    #                 self.result['sii_sent'] = True
    #             self.result['sii_return'] = res
    #     except Exception as fault:
    #         self.result['sii_return'] = fault

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

    out_inv_config = {
        'wsdl': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_07/SuministroFactEmitidas.wsdl',
        'port_name': 'SuministroFactEmitidas',
        'binding_name': '{https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroFactEmitidas.wsdl}siiBinding',
        'type_address': '/wlpl/SSII-FACT/ws/fe/SiiFactFEV1SOAP',
        'service_name': 'siiService'
    }

    in_inv_config = {
        'wsdl': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_07/SuministroFactRecibidas.wsdl',
        'port_name': 'SuministroFactRecibidas',
        'binding_name': '{https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroFactRecibidas.wsdl}siiBinding',
        'type_address': '/wlpl/SSII-FACT/ws/fr/SiiFactFRV1SOAP',
        'service_name': 'siiService'
    }
