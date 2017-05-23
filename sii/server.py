# -*- coding: UTF-8 -*-

from sii.resource import SII
from zeep import Client
from requests import Session
from zeep.transports import Transport

wsdl_files = {
    'emitted_invoice': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_07/SuministroFactEmitidas.wsdl',
    'received_invoice': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_07/SuministroFactRecibidas.wsdl',
    'ids_validator': 'https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/burt/jdit/ws/VNifV1.wsdl',
}


def get_dict_data(invoice):
    return SII.generate_object(invoice)


class Service(object):
    def __init__(self, certificate, key, test_mode=False):
        self.certificate = certificate
        self.key = key
        self.test_mode = True  # Force now work in test mode
        self.emitted_service = None
        self.received_service = None
        self.validator_service = None
        self.result = {}

    def send(self, invoice):
        if self.ids_validate(invoice):
            if invoice.type.startswith('out_'):
                if self.emitted_service is None:
                    self.emitted_service = self.create_service(invoice.type)
            else:
                if self.received_service is None:
                    self.received_service = self.create_service(invoice.type)
            self.send_invoice(invoice)

    def ids_validate(self, invoice):
        owner = {'Nif': invoice.company_id.partner_id.vat,
                 'Nombre': invoice.company_id.partner_id.name}
        receiver = {'Nif': invoice.partner_id.vat,
                    'Nombre': invoice.partner_id.name}
        self.validator_service = self.create_validation_service()
        try:
            owner_res = self.validator_service.VNifV1(owner['Nif'],
                                                        owner['Nombre'])
            receiver_res = self.validator_service.VNifV1(receiver['Nif'],
                                                         receiver['Nombre'])
            return owner['Nif'] == owner_res['Nif'] and receiver['Nif'] == \
                                                        receiver_res['Nif']
        except Exception as fault:
            self.result['validator_return'] = fault

    def create_validation_service(self):
        proxy_address = 'https://sii-proxy.gisce.net:4443/nifs'
        type_address = '/wlpl/BURT-JDIT/ws/VNifV1SOAP'
        session = Session()
        session.cert = (self.certificate, self.key)
        session.verify = False
        transport = Transport(session=session)
        wsdl = wsdl_files['ids_validator']
        binding_name = '{http://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/burt/jdit/ws/VNifV1.wsdl}VNifV1SoapBinding'
        port_name = 'VNifPort1'
        service_name = 'VNifV1Service'
        client = Client(wsdl=wsdl, port_name=port_name, transport=transport,
                        service_name=service_name)
        address = '{0}{1}'.format(proxy_address, type_address)
        service = client.create_service(binding_name, address)
        return service

    def create_service(self, i_type):
        proxy_address = 'https://sii-proxy.gisce.net:4443'
        session = Session()
        session.cert = (self.certificate, self.key)
        session.verify = False
        transport = Transport(session=session)
        if i_type.startswith('out_'):
            wsdl = wsdl_files['emitted_invoice']
            port_name = 'SuministroFactEmitidas'
            binding_name = '{https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroFactEmitidas.wsdl}siiBinding'
            type_address = '/wlpl/SSII-FACT/ws/fe/SiiFactFEV1SOAP'
        else:
            wsdl = wsdl_files['received_invoice']
            port_name = 'SuministroFactRecibidas'
            binding_name = '{https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroFactRecibidas.wsdl}siiBinding'
            type_address = '/wlpl/SSII-FACT/ws/fr/SiiFactFRV1SOAP'
        if self.test_mode:
            port_name += 'Pruebas'

        client = Client(wsdl=wsdl, port_name=port_name, transport=transport,
                        service_name='siiService')
        address = '{0}{1}'.format(proxy_address, type_address)
        service = client.create_service(binding_name, address)
        return service

    def send_invoice(self, invoice):
        msg_header, msg_invoice = self.get_msg(invoice)
        try:
            if invoice.type.startswith('out_'):
                res = self.emitted_service.SuministroLRFacturasEmitidas(
                    msg_header, msg_invoice)
            elif invoice.type.startswith('in_'):
                res = self.received_service.SuministroLRFacturasRecibidas(
                    msg_header, msg_invoice)
            self.result['sii_sent'] = res['EstadoEnvio'] == 'Correcto'
            self.result['sii_return'] = res
        except Exception as fault:
            self.result['sii_return'] = fault

    def list_invoice(self, invoice):
        msg_header, msg_invoice = self.get_msg(invoice)
        try:
            if invoice.type == 'in_invoice':
                res = self.received_service.ConsultaLRFacturasRecibidas(
                    msg_header, msg_invoice)
                if res['EstadoEnvio'] == 'Correcto':
                    self.result['sii_sent'] = True
                self.result['sii_return'] = res
        except Exception as fault:
            self.result['sii_return'] = fault

    def get_msg(self, invoice):
        dict_from_marsh = get_dict_data(invoice=invoice)
        res_header = res_invoices = None
        if invoice.type.startswith('out_'):
            res_header = dict_from_marsh['SuministroLRFacturasEmitidas'][
                'Cabecera']
            res_invoices = dict_from_marsh['SuministroLRFacturasEmitidas'][
                'RegistroLRFacturasEmitidas']
        elif invoice.type.startswith('in_'):
            res_header = dict_from_marsh['SuministroLRFacturasRecibidas'][
                'Cabecera']
            res_invoices = dict_from_marsh['SuministroLRFacturasRecibidas'][
                'RegistroLRFacturasRecibidas']

        return res_header, res_invoices
