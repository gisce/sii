# -*- coding: UTF-8 -*-

from sii.resource import SII
from zeep import Client
from requests import Session
from zeep.wsse.signature import Signature
from zeep.transports import Transport
from utils import fix_ssl_verify
# from dicttoxml import dicttoxml
# from lxml import etree, objectify

wsdl_files = {
    'emitted_invoice': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_07/SuministroFactEmitidas.wsdl',
    'received_invoice': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_07/SuministroFactRecibidas.wsdl',
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
        self.result = {}

    def send(self, invoice):
        fix_ssl_verify()
        if invoice.type.startswith('out_'):
            if self.emitted_service is None:
                self.emitted_service = self.create_service(invoice.type)
            if invoice.type == 'out_invoice':
                self.send_invoice(invoice)
        else:
            if self.received_service is None:
                self.received_service = self.create_service(invoice.type)
            if invoice.type == 'in_invoice':
                self.received_service.send()

    def create_service(self, i_type):

        session = Session()
        # session.cert = (self.certificate, self.key)
        session.verify = False
        session.trust_env = False
        session.proxies = {'https': 'http://sii-proxy.gisce.net:4443'}
        transport = Transport(session=session)
        if i_type.startswith('out_'):
            wsdl = wsdl_files['emitted_invoice']
            port_name = 'SuministroFactEmitidasPruebas'
        else:
            wsdl = wsdl_files['received_invoice']
            port_name = 'SuministroFactRecibidasPruebas'

        client = Client(wsdl=wsdl, port_name=port_name, transport=transport,
                        service_name='siiService')
        # , wsse = Signature(self.key,self.certificate)
        # if self.test_mode:
        # port_name += 'Pruebas'
        # service = client.create_service('{https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroFactEmitidas.wsdl}siiBinding',
        #                                 'https://sii-proxy.gisce.net:4443')
        # serv = client.bind('siiService', port_name)
        return client

    def send_invoice(self, invoice):
        msg_header, msg_invoice = self.get_msg(invoice)
        try:
            if invoice.type == 'out_invoice':
                res = self.emitted_service.service.SuministroLRFacturasEmitidas(
                    msg_header, msg_invoice)
                if res['EstadoEnvio'] == 'Correcto':
                    self.result['sii_sent'] = True
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
        res_header = dict_from_marsh['SuministroLRFacturasEmitidas']['Cabecera']
        res_invoices = dict_from_marsh['SuministroLRFacturasEmitidas'][
            'RegistroLRFacturasEmitidas']
        # xml_from_dict = dicttoxml(dict_from_marsh, root=False, attr_type=False)

        return res_header, res_invoices
