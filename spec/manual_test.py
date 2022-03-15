# -*- coding: UTF-8 -*-

from sii.server import SiiService, SiiDeregisterService
from sii.resource import SII, SIIDeregister
from spec.testing_data import DataGenerator
from datetime import date
import random
import os
from pprintpp import pprint, pformat
import logging

# logging.basicConfig(level=logging.DEBUG)

certificate_path = os.environ['CERTIFICATE_PATH']
key_path = os.environ['KEY_PATH']
current_date = date.strftime(date.today(), '%Y-%m-%d')

data_gen = DataGenerator(
    contraparte_registered=False,
    invoice_registered=True
)
data_gen.invoice_number = '-{}'.format(current_date)
out_invoice = data_gen.get_out_invoice()
in_invoice = data_gen.get_in_invoice()

# CONFIGURATION VARIABLES
invoice = in_invoice
invoice.partner_id.country_id.code = os.environ['COUNTRY_CODE']
invoice.partner_id.country_id.is_eu_member = False
register_invoice = True
deregister_invoice = True

if register_invoice:
    validate_register = SII(invoice).validate_invoice()
    s_reg = SiiService(
        certificate=certificate_path, key=key_path, test_mode=True
    )
    res_register = s_reg.send(invoice)

if deregister_invoice:
    validate_deregister = SIIDeregister(invoice).validate_deregister_invoice()
    s_desreg = SiiDeregisterService(
        certificate=certificate_path, key=key_path, test_mode=True
    )
    res_deregister = s_desreg.deregister(invoice)

print 'Done!'
