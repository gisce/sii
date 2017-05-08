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


class ServiceSII():

    @staticmethod
    def send_emitted_invoice(invoice):
        dict_from_marsh = get_dict_data(invoice=invoice)
        header = dict_from_marsh['SuministroLRFacturasEmitidas']['Cabecera']
        invoices = dict_from_marsh['SuministroLRFacturasEmitidas'][
            'RegistroLRFacturasEmitidas']
        xml_from_dict = dicttoxml(dict_from_marsh, root=False, attr_type=False)
        from pprintpp import pprint
        print '=========================================='
        pprint(header)
        print '=========================================='
        pprint(invoices)
        print '=========================================='
        # session = Session()
        # transport = Transport(session=session, cache=SqliteCache())
        # history = HistoryPlugin()
        # client = Client(wsdl=wsdl_out_invoice, transport=transport,
        #                 plugins=[history])

ServiceSII()
# session = Session()
# session.cert = (publicCrt, privateKey)
# Cache es guarda el fitxer wsdl i els xsd en memoria durant un temps per
# millorar el rendiment
# transport = Transport(session=session, cache=SqliteCache())
# history = HistoryPlugin()
# client = Client(wsdl=wsdl_out_invoice, transport=transport, plugins=[history])
# client = Client(wsdl=wsdl_out_invoice, transport=transport, plugins=[history])
# port_name = 'SuministroFactEmitidasPruebas'
# serv = client.bind('siiService', port_name)
# res = serv.SuministroLRFacturasEmitidas(header, invoices)

# print(history.last_sent)
# print(history.last_received)
