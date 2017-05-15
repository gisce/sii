# -*- coding: UTF-8 -*-

from sii.resource import SII

from zeep import Client
from requests import Session
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin

from dicttoxml import dicttoxml
from lxml import etree, objectify

wsdl_files = {
    'emitted_invoice': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_06/SuministroFactEmitidas.wsdl',
    'received_invoice': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_06/SuministroFactRecibidas.wsdl',
}


def get_dict_data(invoice):
    return SII.generate_object(invoice)


class ServiceSII(object):

    class Service(object):
        def __init__(self, certificate, key, test_mode=False):
            self.certificate = certificate
            self.key = key
            self.test_mode = True  # Force now work in test mode
            self.emitted_service = None
            self.received_service = None

        def send(self, invoice):
            if invoice.type.startswith('out_'):
                if self.emitted_service is None:
                    self.emitted_service = self.create_service(invoice.type)
                self.send_invoice(invoice)
            else:
                if self.received_service is None:
                    self.received_service = self.create_service(invoice.type)
                self.received_service.send()

    def create_service(self, i_type):

        session = Session()
        session.cert = (self.certificate, self.key)
        transport = Transport(session=session)
        history = HistoryPlugin()

        if i_type.startswith('out_'):
            wsdl = wsdl_files['emitted_invoice']
            port_name = 'SuministroFactEmitidasPruebas'
        else:
            wsdl = wsdl_files['received_invoice']
            port_name = 'SuministroFactRecibidasPruebas'
        client = Client(wsdl=wsdl, transport=transport, plugins=[history])
        # if self.test_mode:
        # port_name += 'Pruebas'
        serv = client.bind('siiService', port_name)
        return serv

    def send_invoice(self, invoice):
        msg_header, msg_invoice = self._get_msg(invoice)
        try:
            if invoice.type == 'out_invoice':
                res = self.emitted_serice.SuministroLRFacturasEmitidas(
                    msg_header, msg_invoice)
                # or invoice.type == 'out_refund'
            elif invoice.type == 'in_invoice':
                res = self.received_service.SuministroLRFacturasRecibidas(
                    msg_header, msg_invoice)
                # or invoice.type == 'in_refund'
            if res['EstadoEnvio'] == 'Correcto':
                self.result['sii_sent'] = True
            self.result['sii_return'] = res
        except Exception as fault:
            self.result['sii_return'] = fault

    def list_invoice(self, invoice):
        msg_header, msg_invoice = self._get_msg(invoice)
        try:
            if invoice.type == 'out_invoice':
                res = self.emitted_serice.ConsultaLRFacturasRecibidas(
                    msg_header, msg_invoice)
                # or invoice.type == 'out_refund'
            elif invoice.type == 'in_invoice':
                res = self.received_service.ConsultaLRFacturasRecibidas(
                    msg_header, msg_invoice)
                # or invoice.type == 'in_refund'
            if res['EstadoEnvio'] == 'Correcto':
                self.result['sii_sent'] = True
            self.result['sii_return'] = res
        except Exception as fault:
            self.result['sii_return'] = fault

    @staticmethod
    def get_msg(invoice):
        dict_from_marsh = get_dict_data(invoice=invoice)
        res_header = dict_from_marsh['SuministroLRFacturasEmitidas']['Cabecera']
        res_invoices = dict_from_marsh['SuministroLRFacturasEmitidas'][
            'RegistroLRFacturasEmitidas']
        xml_from_dict = dicttoxml(dict_from_marsh, root=False, attr_type=False)
        from pprintpp import pprint
        print '=================HEADER==================='
        pprint(res_header)
        print '==================BODY===================='
        pprint(res_invoices)
        print '=========================================='
        return res_header, res_invoices

# Cache es guarda el fitxer wsdl i els xsd en memoria durant un temps per
# millorar el rendiment


# print(history.last_sent)
# print(history.last_received)
