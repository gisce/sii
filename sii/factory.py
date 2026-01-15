# -*- coding: utf-8 -*-
"""
Factory Pattern per crear serveis SII (AEAT o ATC)

Aquest mòdul proporciona una interfície unificada per crear serveis SII,
permetent seleccionar dinàmicament entre AEAT i ATC sense canviar el codi client.

Exemple d'ús:
    from sii.factory import SiiServiceFactory
    
    # Crear servei AEAT
    service_aeat = SiiServiceFactory.create_service(
        SiiServiceFactory.AEAT,
        certificate='/path/cert.pem',
        key='/path/key.pem',
        test_mode=True
    )
    
    # Crear servei ATC
    service_atc = SiiServiceFactory.create_service(
        SiiServiceFactory.ATC,
        certificate='/path/cert.pem',
        key='/path/key.pem',
        test_mode=True
    )
"""

from sii.server import SiiService, SiiDeregisterService
from sii.atc.server import SiiServiceATC, SiiDeregisterServiceATC


class SiiServiceFactory(object):
    """
    Factory per crear serveis SII segons el tipus
    
    Proporciona mètodes estàtics per crear instàncies de serveis
    SII per AEAT o ATC de forma dinàmica.
    
    Constants:
        AEAT: Codi per l'Agència Tributària Espanyola
        ATC: Codi per l'Agència Tributària Canària
    """
    
    # Constants per identificar tipus de servei
    AEAT = 'aeat'
    ATC = 'atc'
    
    @classmethod
    def create_service(cls, service_type, certificate, key, url=None, test_mode=False):
        """
        Crea un servei SII segons el tipus especificat
        
        Aquest mètode és el punt d'entrada principal del factory.
        Retorna una instància del servei apropiat segons el service_type.
        
        :param service_type: Tipus de servei ('aeat' o 'atc')
        :type service_type: str
        :param certificate: Path al certificat SSL
        :type certificate: str
        :param key: Path a la clau privada
        :type key: str
        :param url: URL base del servei (opcional, per proxy SSL)
        :type url: str or None
        :param test_mode: Si és mode de proves (True) o producció (False)
        :type test_mode: bool
        :return: Instància de SiiService o SiiServiceATC
        :rtype: SiiService or SiiServiceATC
        :raises ValueError: Si service_type no és vàlid
        
        Exemple:
            >>> service = SiiServiceFactory.create_service(
            ...     SiiServiceFactory.AEAT,
            ...     certificate='/path/cert.pem',
            ...     key='/path/key.pem',
            ...     test_mode=True
            ... )
            >>> result = service.send(invoice)
        """
        if service_type == cls.AEAT:
            return SiiService(
                certificate=certificate,
                key=key,
                url=url,
                test_mode=test_mode
            )
        elif service_type == cls.ATC:
            return SiiServiceATC(
                certificate=certificate,
                key=key,
                url=url,
                test_mode=test_mode
            )
        else:
            raise ValueError(
                "service_type must be '{}' or '{}', got: '{}'".format(
                    cls.AEAT, cls.ATC, service_type
                )
            )
    
    @classmethod
    def create_deregister_service(cls, service_type, certificate, key, url=None, test_mode=False):
        """
        Crea un servei de baixa segons el tipus especificat
        
        Similar a create_service, però retorna serveis per donar de baixa
        factures en lloc d'enviar-les.
        
        :param service_type: Tipus de servei ('aeat' o 'atc')
        :type service_type: str
        :param certificate: Path al certificat SSL
        :type certificate: str
        :param key: Path a la clau privada
        :type key: str
        :param url: URL base del servei (opcional, per proxy SSL)
        :type url: str or None
        :param test_mode: Si és mode de proves (True) o producció (False)
        :type test_mode: bool
        :return: Instància de SiiDeregisterService o SiiDeregisterServiceATC
        :rtype: SiiDeregisterService or SiiDeregisterServiceATC
        :raises ValueError: Si service_type no és vàlid
        
        Exemple:
            >>> service = SiiServiceFactory.create_deregister_service(
            ...     SiiServiceFactory.ATC,
            ...     certificate='/path/cert.pem',
            ...     key='/path/key.pem',
            ...     test_mode=True
            ... )
            >>> result = service.deregister(invoice)
        """
        if service_type == cls.AEAT:
            return SiiDeregisterService(
                certificate=certificate,
                key=key,
                url=url,
                test_mode=test_mode
            )
        elif service_type == cls.ATC:
            return SiiDeregisterServiceATC(
                certificate=certificate,
                key=key,
                url=url,
                test_mode=test_mode
            )
        else:
            raise ValueError(
                "service_type must be '{}' or '{}', got: '{}'".format(
                    cls.AEAT, cls.ATC, service_type
                )
            )
    
    @classmethod
    def get_available_services(cls):
        """
        Retorna la llista de serveis disponibles
        
        :return: Llista amb els codis dels serveis disponibles
        :rtype: list
        
        Exemple:
            >>> SiiServiceFactory.get_available_services()
            ['aeat', 'atc']
        """
        return [cls.AEAT, cls.ATC]
    
    @classmethod
    def is_valid_service_type(cls, service_type):
        """
        Comprova si un tipus de servei és vàlid
        
        :param service_type: Tipus de servei a validar
        :type service_type: str
        :return: True si és vàlid, False altrament
        :rtype: bool
        
        Exemple:
            >>> SiiServiceFactory.is_valid_service_type('aeat')
            True
            >>> SiiServiceFactory.is_valid_service_type('invalid')
            False
        """
        return service_type in cls.get_available_services()
