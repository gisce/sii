# -*- coding: UTF-8 -*-

from sii.server import *
from spec.testing_data import DataGenerator

data_gen = DataGenerator()
in_invoice = data_gen.get_in_invoice()
out_invoice = data_gen.get_out_invoice()
s = Service('/home/miquel/Documents/SII/client_ssl/client.crt',
            '/home/miquel/Documents/SII/client_ssl/client.key')
invoice = out_invoice
s.send(invoice)

print s.result
