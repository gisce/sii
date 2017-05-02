# -*- coding: UTF-8 -*-

from sii.resource import SII
from requests import Session
from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin

from lxml import etree, objectify

with open('/home/miquel/codi/sii/sii/xml_examples/ejemplo_xml_alta_factura_emitida.xml', 'r') as myfile:
    xml_read = myfile.read().replace('\n', '')
    # from pprintpp import pprint
    # pprint(xml_da)

# def get_xsd_path(self):
#     return "{}/giscedata_switching_cnmc_reports/xml/{}".format(
#         config['addons_path'], self.xsd_file
#     )

xmlschema = etree.XMLSchema(file='/home/miquel/codi/sii/sii/data/SuministroLR.xsd')

parser = objectify.makeparser(schema=xmlschema)
a = objectify.fromstring(xml_read, parser)

wsdl_out_invoice = 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_06/SuministroFactEmitidas.wsdl'

session = Session()
# session.cert = (publicCrt, privateKey)
transport = Transport(session=session)
history = HistoryPlugin()
# client = Client(wsdl=wsdl_out_invoice, transport=transport, plugins=[history])
client = Client(wsdl=wsdl_out_invoice, transport=transport)

port_name = 'SuministroFactEmitidasPruebas'
serv = client.bind('siiService', port_name)

res = serv.SuministroLRFacturasEmitidas(header, invoices)

