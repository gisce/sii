# -*- coding: UTF-8 -*-

from sii.resource import SII
import zeep
from dicttoxml import dicttoxml
from lxml import etree, objectify


cabecera = {
    "SuministroLRFacturasEmitidas": {
        "Cabecera": {
            "IDVersionSii": "0.6",
            "Titular": {
                "NombreRazon": "Francisco García",
                "NIF": "12345678T"},
            "TipoComunicacion": "A0"
        }
    }
}

dict_to_xml = dicttoxml(cabecera)
import xml.dom.minidom
xml_pretty = xml.dom.minidom.parseString(dict_to_xml) # or xml.dom.minidom.parseString(xml_string)
pretty_xml_as_string = xml_pretty.toprettyxml()


with open('/home/miquel/codi/sii/sii/data/SuministroLR.xsd', 'r') as myfile:
    xsd_read = myfile.read().replace('\n', '')

with open('/home/miquel/codi/sii/sii/xml_examples/ejemplo_xml_alta_factura_emitida.xml', 'r') as myfile:
    xml_read = myfile.read().replace('\n', '')
    # from pprintpp import pprint
    # pprint(xml_da)

xmlschema = etree.XMLSchema(file='/home/miquel/codi/sii/sii/data/SuministroLR.xsd')

parser = objectify.makeparser(schema=xmlschema)
a = objectify.fromstring(xml_read, parser)

wsdl_out_invoice = 'http://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_06/SuministroFactEmitidas.wsdl'

client = zeep.Client(wsdl=wsdl_out_invoice)
