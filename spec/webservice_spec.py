# -*- coding: UTF-8 -*-

from expects import *
from sii.server import *
from spec.testing_data import DataGenerator


with description("Los web services"):
    with before.all:
        data_gen = DataGenerator()
        self.in_invoice = data_gen.get_in_invoice()
        self.out_invoice = data_gen.get_out_invoice()

        # # xml_pretty = xml.dom.minidom.parseString(xml_from_dict)
        # # pretty_xml_as_string = xml_pretty.toprettyxml()
        #
        # print '\n'
        # print '============ RESULT FROM DICTTOXML ====================='
        # print(pretty_xml_as_string)
        # print '====================================================='

    with description("obtienen el mensaje a enviar"):
        with it("de un objeto invoice"):

            s = Service('/home/miquel/Documents/SII/client_ssl/client.crt',
                        '/home/miquel/Documents/SII/client_ssl/client.key')
            self.invoice = self.out_invoice
            s.send(self.invoice)
