# -*- coding: UTF-8 -*-
"""
Serveis SOAP per al SII de l'Agència Tributària Canària (ATC)

Aquest mòdul implementa els clients SOAP per comunicar-se amb el SII ATC,
adaptant els serveis existents de l'AEAT per utilitzar els endpoints i
WSDLs de l'Agència Tributària Canària.
"""

from sii.atc.resource import SIIATC, SIIATCDeregister
from zeep import Client
from requests import Session
from zeep.exceptions import Fault
from zeep.transports import Transport
from zeep.helpers import serialize_object
import certifi
import os


def get_wsdl_path(filename):
    """
    Obté el path complet a un fitxer WSDL local
    
    :param filename: Nom del fitxer WSDL
    :return: Path absolut al fitxer WSDL
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    wsdl_dir = os.path.join(current_dir, '..', 'data', 'atc', 'wsdl')
    wsdl_path = os.path.join(wsdl_dir, filename)
    return 'file://{}'.format(os.path.abspath(wsdl_path))


class Service(object):
    """Classe base per serveis"""
    
    def __init__(self, certificate, key, url=None):
        self.certificate = certificate
        self.key = key
        self.url = url
        self.result = []


class SiiServiceATC(Service):
    """
    Servei SII per l'Agència Tributària Canària
    
    Equivalent a SiiService per AEAT, però adaptat per:
    - Endpoints de l'ATC (gobiernodecanarias.org)
    - WSDLs locals de l'ATC
    - Estructura IGIC en lloc d'IVA
    """
    
    def __init__(self, certificate, key, url=None, test_mode=False):
        """
        Inicialitza el servei SII ATC
        
        :param certificate: Path al certificat SSL
        :param key: Path a la clau privada
        :param url: URL base (opcional, per proxy SSL)
        :param test_mode: Si és mode de proves (1) o producció (0)
        """
        super(SiiServiceATC, self).__init__(certificate, key, url)
        self.test_mode = test_mode
        self.emitted_service = None
        self.received_service = None
        self.url = url
        self.invoice = None
    
    def send(self, invoice):
        """
        Envia una factura al SII ATC
        
        :param invoice: Factura d'OpenERP
        :return: Resposta del servei SOAP serialitzada
        """
        self.invoice = invoice
        if self.invoice.type.startswith('out_'):
            if self.emitted_service is None:
                self.emitted_service = self.create_service()
        else:
            if self.received_service is None:
                self.received_service = self.create_service()
        return self.send_invoice()
    
    def create_service(self):
        """
        Crea el client SOAP segons el tipus de factura
        
        DIFERÈNCIES amb AEAT:
        - WSDLs locals de l'ATC
        - Endpoints: gobiernodecanarias.org/tributos/atc
        - Namespace diferent
        """
        session = Session()
        session.cert = (self.certificate, self.key)
        session.verify = False if self.url else certifi.where()
        transport = Transport(session=session)
        
        if self.invoice.type.startswith('out_'):
            config = self.out_inv_config.copy()
        else:
            config = self.in_inv_config.copy()
        
        port_name = config['port_name']
        # Nota: L'ATC podria no tenir ports separats per proves
        # Ajustar segons la documentació oficial
        if self.test_mode:
            # TODO: Verificar si l'ATC té ports diferents per proves
            port_name += 'Pruebas'  # Ajustar segons documentació ATC
        
        client = Client(
            wsdl=config['wsdl'],
            port_name=port_name,
            transport=transport,
            service_name=config['service_name']
        )
        
        if not self.url:
            return client.service
        
        # Si hi ha URL (proxy), crear servei amb adreça personalitzada
        address = '{0}{1}'.format(self.url, config['type_address'])
        service = client.create_service(config['binding_name'], address)
        return service
    
    def send_invoice(self):
        """
        Envia la factura al servei SOAP
        
        Crida als mètodes SOAP:
        - SuministroLRFacturasEmitidas (factures emeses)
        - SuministroLRFacturasRecibidas (factures rebudes)
        
        :return: Resposta serialitzada
        """
        msg_header, msg_invoice = self.get_msg()
        try:
            if self.invoice.type.startswith('out_'):
                res = self.emitted_service.SuministroLRFacturasEmitidas(
                    msg_header, msg_invoice
                )
            elif self.invoice.type.startswith('in_'):
                res = self.received_service.SuministroLRFacturasRecibidas(
                    msg_header, msg_invoice
                )
            self.result = res
            return serialize_object(self.result)
        except Exception as fault:
            self.result = fault
            raise fault
    
    def get_msg(self):
        """
        Obté els missatges de capçalera i factura des de SIIATC
        
        DIFERÈNCIA: Utilitza SIIATC en lloc de SII
        """
        dict_from_marsh = SIIATC(self.invoice).generate_object()
        res_header = res_invoices = None
        
        if self.invoice.type.startswith('out_'):
            res_header = dict_from_marsh['Cabecera']
            res_invoices = dict_from_marsh['RegistroLRFacturasEmitidas']
        elif self.invoice.type.startswith('in_'):
            res_header = dict_from_marsh['Cabecera']
            res_invoices = dict_from_marsh['RegistroLRFacturasRecibidas']
        
        return res_header, res_invoices
    
    # Configuració per factures emeses
    # DIFERÈNCIES CLAU:
    # - WSDL local de l'ATC
    # - Endpoint: gobiernodecanarias.org/tributos/atc
    # - Namespace del binding diferent
    out_inv_config = {
        'wsdl': get_wsdl_path('SuministroFactEmitidas.wsdl'),
        'port_name': 'SuministroFactEmitidas',
        # TODO: Ajustar binding_name segons el namespace real del WSDL ATC
        # Cal revisar el WSDL per obtenir el namespace correcte
        'binding_name': '{https://www3.gobiernodecanarias.org/tributos/atc/sii/igic/ws/SuministroFactEmitidas.wsdl}siiBinding',
        # TODO: Verificar el type_address exacte amb la documentació ATC
        'type_address': '/tributos/atc/sii/fe/',
        'service_name': 'siiService'
    }
    
    # Configuració per factures rebudes
    in_inv_config = {
        'wsdl': get_wsdl_path('SuministroFactRecibidas.wsdl'),
        'port_name': 'SuministroFactRecibidas',
        # TODO: Ajustar binding_name segons el namespace real del WSDL ATC
        'binding_name': '{https://www3.gobiernodecanarias.org/tributos/atc/sii/igic/ws/SuministroFactRecibidas.wsdl}siiBinding',
        # TODO: Verificar el type_address exacte amb la documentació ATC
        'type_address': '/tributos/atc/sii/fr/',
        'service_name': 'siiService'
    }
    
    def get_production_url(self):
        """
        Retorna la URL de producció de l'ATC
        
        :return: URL base del servei de producció
        """
        return 'https://www3.gobiernodecanarias.org'
    
    def get_test_url(self):
        """
        Retorna la URL de proves de l'ATC
        
        TODO: Verificar si l'ATC té un entorn de proves separat
        
        :return: URL base del servei de proves
        """
        # Nota: L'ATC podria utilitzar la mateixa URL per proves
        # i diferenciar amb un paràmetre al XML
        return 'https://www3.gobiernodecanarias.org'


class SiiDeregisterServiceATC(SiiServiceATC):
    """
    Servei per donar de baixa factures del SII ATC
    
    Equivalent a SiiDeregisterService per AEAT
    """
    
    def get_deregister_msg(self):
        """
        Obté els missatges per donar de baixa una factura
        
        DIFERÈNCIA: Utilitza SIIATCDeregister en lloc de SIIDeregister
        """
        dict_from_marsh = SIIATCDeregister(self.invoice).generate_object()
        res_header = res_invoice = None
        
        if self.invoice.type.startswith('out_'):
            res_header = dict_from_marsh['Cabecera']
            res_invoice = dict_from_marsh['RegistroLRBajaExpedidas']
        elif self.invoice.type.startswith('in_'):
            res_header = dict_from_marsh['Cabecera']
            res_invoice = dict_from_marsh['RegistroLRBajaRecibidas']
        
        return res_header, res_invoice
    
    def deregister_invoice(self):
        """
        Dona de baixa la factura al servei SOAP
        
        Crida als mètodes SOAP:
        - AnulacionLRFacturasEmitidas (factures emeses)
        - AnulacionLRFacturasRecibidas (factures rebudes)
        """
        msg_header, msg_invoice = self.get_deregister_msg()
        try:
            if self.invoice.type.startswith('out_'):
                res = self.emitted_service.AnulacionLRFacturasEmitidas(
                    msg_header, msg_invoice
                )
            elif self.invoice.type.startswith('in_'):
                res = self.received_service.AnulacionLRFacturasRecibidas(
                    msg_header, msg_invoice
                )
            self.result = res
            return serialize_object(self.result)
        except Exception as fault:
            self.result = fault
            raise fault
    
    def deregister(self, invoice):
        """
        Dona de baixa una factura del SII ATC
        
        :param invoice: Factura d'OpenERP
        :return: Resposta del servei SOAP serialitzada
        """
        self.invoice = invoice
        if self.invoice.type.startswith('out_'):
            if self.emitted_service is None:
                self.emitted_service = self.create_service()
        else:
            if self.received_service is None:
                self.received_service = self.create_service()
        return self.deregister_invoice()
