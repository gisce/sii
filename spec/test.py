# -*- coding: UTF-8 -*-
import logging

logging.basicConfig(level=logging.DEBUG)

from sii.server import *
from spec.testing_data import DataGenerator

data_gen = DataGenerator()
in_invoice = data_gen.get_in_invoice()
out_invoice = data_gen.get_out_invoice()
in_refund = data_gen.get_in_refund_invoice()
out_refund = data_gen.get_out_refund_invoice()
s = Service('/home/miquel/Documents/SII/client_ssl/client.crt',
            '/home/miquel/Documents/SII/client_ssl/client.key')
invoice = out_refund
s.send(invoice)

print s.result
