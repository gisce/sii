# coding=utf-8

from marshmallow import Schema, fields


class Cabecera(Schema):
    nif = fields.String()
    apellidos_nombre = fields.String()
    tipo_comunicacion = fields.String()


class Factura(Schema):
    numero = fields.String()


class XMLEnviado(Schema):
    cabecera = fields.Nested(Cabecera)
    factura = fields.Nested(Factura)
