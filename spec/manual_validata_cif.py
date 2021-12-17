import os
from sii.server import IDService

certificate_path = os.environ['CERTIFICATE_PATH']
key_path = os.environ['KEY_PATH']
service = IDService(
            certificate_path,
            key_path,
            None,  # PROXY
        )
name = raw_input('Name: ')
vat = raw_input('vat: ')

partner = {'name': name, 'vat': vat}
print service.ids_validate([partner])
