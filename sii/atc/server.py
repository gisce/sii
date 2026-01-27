# -*- coding: UTF-8 -*-
"""
Serveis SOAP per al SII de l'Agència Tributària Canària (ATC)

Aquest mòdul implementa els clients SOAP per comunicar-se amb el SII ATC,
adaptant els serveis existents de l'AEAT per utilitzar els endpoints i
WSDLs de l'Agència Tributària Canària.
"""

from sii.atc.resource import SIIATC, SIIATCDeregister
from sii.atc.plugins import DryRunPlugin, PersistXmlPlugin
from sii.atc.plugins.dry_run_plugin import DryRunException
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
    
    def __init__(self, certificate, key, url=None, test_mode=False,
                 dry_run=False, dry_run_verbose=False, persist_xml=None, use_local_wsdl=None):
        """
        Inicialitza el servei SII ATC
        
        :param certificate: Path al certificat SSL
        :param key: Path a la clau privada
        :param url: URL base (opcional, per proxy SSL)
        :param test_mode: Si és mode de proves (1) o producció (0)
        :param dry_run: Si True, NO envia peticions reals (mode debug)
        :param persist_xml: Dict amb {'request': path, 'response': path} per guardar XMLs
        :param use_local_wsdl: Si True, utilitza WSDLs locals. Si None, auto (local si dry_run)
        """
        super(SiiServiceATC, self).__init__(certificate, key, url)
        self.test_mode = test_mode
        self.dry_run = dry_run
        self.dry_run_verbose = dry_run_verbose
        self.persist_xml = persist_xml
        # Si use_local_wsdl no especificat, usar local quan dry_run activat
        if use_local_wsdl is None:
            self.use_local_wsdl = dry_run
        else:
            self.use_local_wsdl = use_local_wsdl
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
        - WSDLs remots (o locals si dry_run/tests)
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
        
        # Decidir si usar WSDL local o remot
        if self.use_local_wsdl:
            # WSDLs locals per tests/dry-run
            if self.invoice.type.startswith('out_'):
                wsdl_url = get_wsdl_path('SuministroFactEmitidas.wsdl')
            else:
                wsdl_url = get_wsdl_path('SuministroFactRecibidas.wsdl')
        else:
            # WSDLs remots per producció
            wsdl_url = config['wsdl']
            if self.test_mode:
                # Substituir middleware per middlewarecaut per entorn de proves
                wsdl_url = wsdl_url.replace('/middleware/', '/middlewarecaut/')
        
        port_name = config['port_name']
        # L'ATC utilitza ports diferents per proves (sufijo 'Pruebas')
        if self.test_mode:
            port_name += 'Pruebas'
        
        # Construir llista de plugins (per defecte buida)
        plugins = []
        
        # Afegir plugin de persistència si especificat
        if self.persist_xml:
            plugins.append(PersistXmlPlugin(
                request_file=self.persist_xml.get('request'),
                response_file=self.persist_xml.get('response')
            ))
        
        # Afegir plugin dry-run si activat
        if self.dry_run:
            plugins.append(DryRunPlugin(verbose=self.dry_run_verbose))
        
        client = Client(
            wsdl=wsdl_url,
            port_name=port_name,
            transport=transport,
            service_name=config['service_name'],
            plugins=plugins if plugins else None
        )
        
        if not self.url:
            return client.service
        
        # Si hi ha URL (proxy), crear servei amb adreça personalitzada
        # En mode test, utilitzar path middlewarecaut
        if self.test_mode:
            type_address = config['type_address'].replace('/middleware/', '/middlewarecaut/')
        else:
            type_address = config['type_address']
        
        address = '{0}{1}'.format(self.url, type_address)
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
        except DryRunException as dry_ex:
            # Mode dry-run: retornar resposta simulada
            # Python 2/3 compatible: evitar UnicodeEncodeError
            try:
                # Python 2: convertir a unicode i després a UTF-8
                msg = unicode(dry_ex).encode('utf-8') if hasattr(str, 'decode') else str(dry_ex)
            except (NameError, UnicodeDecodeError):
                # Python 3 o fallback
                msg = str(dry_ex)
            
            self.result = {
                'successful': True,
                'dry_run': True,
                'message': msg,
                'xml_generated': True
            }
            return self.result
        except Exception as e:
            # Python 2/3 compatible: simplement capturar i reraisar
            self.result = e
            raise
    
    def get_msg(self):
        """
        Obté els missatges de capçalera i factura des de SIIATC
        
        DIFERÈNCIA: Utilitza SIIATC en lloc de SII
        """
        dict_from_marsh = SIIATC(self.invoice).generate_object()
        res_header = res_invoices = None
        
        if self.invoice.type.startswith('out_'):
            suministro = dict_from_marsh['SuministroLRFacturasEmitidas']
            res_header = suministro['Cabecera']
            res_invoices = suministro['RegistroLRFacturasEmitidas']
        elif self.invoice.type.startswith('in_'):
            suministro = dict_from_marsh['SuministroLRFacturasRecibidas']
            res_header = suministro['Cabecera']
            res_invoices = suministro['RegistroLRFacturasRecibidas']
        
        return res_header, res_invoices
    
    # Configuració per factures emeses
    # URLs remotes ATC (producció/proves reals):
    # - Producció: https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/
    # - Proves: https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/
    # 
    # NOTA: Si dry_run=True, s'utilitzen WSDLs locals automàticament (no cal connexió)
    out_inv_config = {
        'wsdl': 'https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactFEV1SOAP?wsdl',
        'port_name': 'SuministroFactEmitidas',
        'binding_name': '{https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/igic/ws/SuministroFactEmitidas.wsdl}siiBinding',
        'type_address': '/tributos/middleware/services/sii/SiiFactFEV1SOAP',
        'service_name': 'siiService'
    }
    
    # Configuració per factures rebudes
    in_inv_config = {
        'wsdl': 'https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactFRV1SOAP?wsdl',
        'port_name': 'SuministroFactRecibidas',
        'binding_name': '{https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/igic/ws/SuministroFactRecibidas.wsdl}siiBinding',
        'type_address': '/tributos/middleware/services/sii/SiiFactFRV1SOAP',
        'service_name': 'siiService'
    }
    
    def get_production_url(self):
        """
        Retorna la URL de producció de l'ATC
        
        URL oficial: https://sede.gobiernodecanarias.org
        Path: /tributos/middleware/services/sii/
        
        :return: URL base del servei de producció
        """
        return 'https://sede.gobiernodecanarias.org'
    
    def get_test_url(self):
        """
        Retorna la URL de proves de l'ATC (Preproducció)
        
        URL oficial: https://sede.gobiernodecanarias.org
        Path: /tributos/middlewarecaut/services/sii/
        
        Nota: Mateix host però path diferent (middlewarecaut vs middleware)
        
        :return: URL base del servei de proves
        """
        return 'https://sede.gobiernodecanarias.org'


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
