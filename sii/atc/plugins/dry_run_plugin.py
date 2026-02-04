# -*- coding: utf-8 -*-
"""
Plugin Dry Run per SII ATC

Aquest plugin intercepta les peticions SOAP i:
1. Imprimeix l'XML generat
2. Opcionalment el guarda a fitxer
3. Evita l'enviament real aixecant una excepció controlada

Ús:
    client = Client(wsdl=wsdl, plugins=[DryRunPlugin(output_file='/tmp/request.xml')])
"""
from __future__ import absolute_import, unicode_literals

from zeep import Plugin
from lxml import etree


class DryRunPlugin(Plugin):
    """
    Plugin de Zeep per mode dry-run (sense enviar peticions reals)
    
    En mode dry-run:
    - Genera l'XML SOAP complet
    - Mostra/guarda l'XML
    - NO envia la petició al servidor
    
    Útil per:
    - Debugging d'estructures XML
    - Validació de format abans d'enviar
    - Tests sense impacte al servidor
    """
    
    def __init__(self, output_file=None, verbose=True, output_buffer=None):
        """
        Inicialitza el plugin dry-run
        
        Args:
            output_file: Path opcional per guardar l'XML de petició
            verbose: Si True, imprimeix l'XML per consola
            output_buffer: Buffer IO opcional (StringIO/BytesIO) per guardar XML en memòria
        """
        self.output_file = output_file
        self.verbose = verbose
        self.output_buffer = output_buffer
        self.last_request_xml = None
    
    def egress(self, envelope, http_headers, operation, binding_options):
        """
        Intercepta la petició sortint (egress)
        
        Args:
            envelope: Envelope SOAP (lxml Element)
            http_headers: Capçaleres HTTP
            operation: Operació SOAP
            binding_options: Opcions de binding
            
        Returns:
            No retorna (aixeca excepció per evitar enviament)
        """
        # Convertir envelope a string XML
        xml_str = etree.tostring(envelope, pretty_print=True, encoding='unicode')
        self.last_request_xml = xml_str
        
        # Mostrar per consola si verbose
        if self.verbose:
            print("\n" + "="*80)
            # Python 2/3 compatible: evitar problemes amb accents
            try:
                # Python 2: imprimir amb encode
                print(u"DRY RUN - XML Peticio SOAP (NO enviat)".encode('utf-8') if hasattr(str, 'decode') else "DRY RUN - XML Peticio SOAP (NO enviat)")
            except:
                print("DRY RUN - XML Peticio SOAP (NO enviat)")
            print("="*80)
            try:
                # Python 2: convertir unicode a str
                print_str = xml_str.encode('utf-8') if isinstance(xml_str, unicode) else xml_str
                print(print_str)
            except NameError:
                # Python 3: no existeix unicode
                print(xml_str)
            except UnicodeEncodeError:
                # Fallback: imprimir sense accents
                print(xml_str.encode('ascii', 'ignore'))
            print("="*80 + "\n")
        
        # Guardar a fitxer si especificat
        if self.output_file:
            try:
                # Python 2/3 compatible: usar io.open
                import io
                with io.open(self.output_file, 'w', encoding='utf-8') as f:
                    f.write(xml_str)
                if self.verbose:
                    print("XML guardat a: {0}".format(self.output_file))
            except Exception as e:
                print("ERROR guardant XML a fitxer: {0}".format(e))
        
        # Guardar a buffer si especificat
        if self.output_buffer:
            try:
                self.output_buffer.write(xml_str)
                if self.verbose:
                    print("XML guardat a buffer en memòria")
            except Exception as e:
                print("ERROR guardant XML a buffer: {0}".format(e))
        
        # Aixecar excepció per evitar enviament real
        # Aquesta excepció s'ha de capturar al codi que crida
        raise DryRunException("Dry run activat: petició NO enviada al servidor")
        
        # No s'executarà mai (per completesa del mètode)
        return envelope, http_headers


class DryRunException(Exception):
    """
    Excepció específica per indicar que és un dry-run
    
    Permet distingir entre errors reals i interrupcions de dry-run
    """
    pass
