# -*- coding: utf-8 -*-
"""
Plugin Persistència XML per SII ATC

Aquest plugin guarda els XMLs de petició i resposta SOAP a fitxers.

Ús:
    client = Client(
        wsdl=wsdl,
        plugins=[PersistXmlPlugin('/tmp/request.xml', '/tmp/response.xml')]
    )
"""
from __future__ import absolute_import, unicode_literals

from zeep import Plugin
from lxml import etree
import os


class PersistXmlPlugin(Plugin):
    """
    Plugin de Zeep per persistir XMLs de petició i resposta
    
    Guarda:
    - XML de petició (envelope sortint)
    - XML de resposta (envelope entrant)
    
    Útil per:
    - Debugging de peticions reals
    - Auditoria d'enviaments
    - Anàlisi post-mortem d'errors
    - Validació amb XSD offline
    """
    
    def __init__(self, request_file=None, response_file=None, create_dirs=True):
        """
        Inicialitza el plugin de persistència
        
        Args:
            request_file: Path per guardar XML de petició
            response_file: Path per guardar XML de resposta
            create_dirs: Si True, crea directoris si no existeixen
        """
        self.request_file = request_file
        self.response_file = response_file
        self.create_dirs = create_dirs
        
        # Crear directoris si cal
        if self.create_dirs:
            for filepath in [request_file, response_file]:
                if filepath:
                    dirpath = os.path.dirname(filepath)
                    if dirpath and not os.path.exists(dirpath):
                        try:
                            os.makedirs(dirpath)
                        except OSError:
                            pass  # Potser ja existeix (race condition)
    
    def egress(self, envelope, http_headers, operation, binding_options):
        """
        Intercepta la petició sortint (egress) i la guarda
        
        Args:
            envelope: Envelope SOAP (lxml Element)
            http_headers: Capçaleres HTTP
            operation: Operació SOAP
            binding_options: Opcions de binding
            
        Returns:
            Tuple (envelope, http_headers) sense modificar
        """
        if self.request_file:
            try:
                xml_str = etree.tostring(
                    envelope,
                    pretty_print=True,
                    encoding='unicode'
                )
                # Python 2/3 compatible: usar io.open
                import io
                with io.open(self.request_file, 'w', encoding='utf-8') as f:
                    f.write(xml_str)
            except Exception as e:
                # No volem que un error de persistència pari l'enviament
                print("WARNING: Error guardant request XML: {0}".format(e))
        
        return envelope, http_headers
    
    def ingress(self, envelope, http_headers, operation):
        """
        Intercepta la resposta entrant (ingress) i la guarda
        
        Args:
            envelope: Envelope SOAP de resposta (lxml Element)
            http_headers: Capçaleres HTTP
            operation: Operació SOAP
            
        Returns:
            Tuple (envelope, http_headers) sense modificar
        """
        if self.response_file:
            try:
                xml_str = etree.tostring(
                    envelope,
                    pretty_print=True,
                    encoding='unicode'
                )
                # Python 2/3 compatible: usar io.open
                import io
                with io.open(self.response_file, 'w', encoding='utf-8') as f:
                    f.write(xml_str)
            except Exception as e:
                # No volem que un error de persistència pari el processament
                print("WARNING: Error guardant response XML: {0}".format(e))
        
        return envelope, http_headers
