# coding=utf-8
from sii import models


class SII(object):
    @staticmethod
    def generate_xml(invoice):
        xml = models.XMLEnviado()

        tipo_comunicacion = 'A0'
        obj = {
            'cabecera': {
                'nif': 'NIF DE PRUEBA 1',
                'apellidos_nombre': 'APELLIDOS PRUEBA 1',
                'tipo_comunicacion': tipo_comunicacion
            },
            'factura': {
                'numero': invoice.number
            }
        }

        return xml.dump(obj).data
