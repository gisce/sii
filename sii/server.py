# -*- coding: UTF-8 -*-

from sii.resource import SII

from zeep import Client
from requests import Session
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin

from dicttoxml import dicttoxml
from lxml import etree, objectify

wsdl_files = {'emited_invoice': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_06/SuministroFactEmitidas.wsdl',
              'received_invoice': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_06/SuministroFactRecibidas.wsdl',
              'cobros_emitidas': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_06/SuministroCobrosEmitidas.wsdl',
              'pagos_recibidas': 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_06/SuministroPagosRecibidas.wsdl',
              }


def get_dict_data(invoice):
    return SII.generate_object(invoice)


class ServiceSII(object):

    def __init__(self):
        self.result = {}

    @staticmethod
    def _connect_sii(wsdl, publicCrt, privateKey):

        public_crt = publicCrt
        priv_key = privateKey

        session = Session()
        session.cert = (public_crt, priv_key)
        transport = Transport(session=session)

        history = HistoryPlugin()
        client = Client(wsdl=wsdl, transport=transport, plugins=[history])
        return client

    @staticmethod
    def _get_msg(invoice):
        dict_from_marsh = get_dict_data(invoice=invoice)
        res_header = dict_from_marsh['SuministroLRFacturasEmitidas']['Cabecera']
        res_invoices = dict_from_marsh['SuministroLRFacturasEmitidas'][
            'RegistroLRFacturasEmitidas']
        xml_from_dict = dicttoxml(dict_from_marsh, root=False, attr_type=False)
        from pprintpp import pprint
        print '=========================================='
        pprint(res_header)
        print '=========================================='
        pprint(res_invoices)
        print '=========================================='
        return res_header, res_invoices

    def send_emitted_invoice(self, invoice):
        if invoice.type == 'out_invoice' or invoice.type == 'out_refund':
            wsdl = wsdl_files['emited_invoice']
            client = self._connect_sii(wsdl, 'a', 'b')
            port_name = 'SuministroFactEmitidas'
            port_name += 'Pruebas'
        elif invoice.type == 'in_invoice' or invoice.type == 'in_refund':
            wsdl = wsdl_files['received_invoice']
            client = self._connect_sii(wsdl, 'a', 'b')
            port_name = 'SuministroFactRecibidas'
            port_name += 'Pruebas'
        serv = client.bind('siiService', port_name)

        msg_header, msg_invoice = self._get_msg(invoice)
        try:
            if invoice.type == 'out_invoice' or invoice.type == 'out_refund':
                res = serv.SuministroLRFacturasEmitidas(msg_header, msg_invoice)
            elif invoice.type == 'in_invoice' or invoice.type == 'in_refund':
                res = serv.SuministroLRFacturasRecibidas(msg_header, msg_invoice)
            if res['EstadoEnvio'] == 'Correcto':
                self.result['sii_sent'] = True
            self.result['sii_return'] = res
        except Exception as fault:
            self.result['sii_return'] = fault

ServiceSII()

# Cache es guarda el fitxer wsdl i els xsd en memoria durant un temps per
# millorar el rendiment


# print(history.last_sent)
# print(history.last_received)
