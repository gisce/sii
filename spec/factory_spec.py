# coding=utf-8
"""
Tests per SiiServiceFactory

Aquest fitxer conté els tests amb Mamba per verificar que el Factory
pattern funciona correctament per crear serveis AEAT i ATC.
"""

from sii.factory import SiiServiceFactory
from sii.server import SiiService, SiiDeregisterService
from sii.atc.server import SiiServiceATC, SiiDeregisterServiceATC
from expects import *
from mamba import *


with description('SiiServiceFactory'):
    
    with description('constants'):
        with it('té constant AEAT'):
            expect(SiiServiceFactory.AEAT).to(equal('aeat'))
        
        with it('té constant ATC'):
            expect(SiiServiceFactory.ATC).to(equal('atc'))
    
    with description('get_available_services'):
        with it('retorna una llista'):
            services = SiiServiceFactory.get_available_services()
            expect(services).to(be_a(list))
        
        with it('conté aeat i atc'):
            services = SiiServiceFactory.get_available_services()
            expect(services).to(contain('aeat'))
            expect(services).to(contain('atc'))
        
        with it('té exactament 2 serveis'):
            services = SiiServiceFactory.get_available_services()
            expect(len(services)).to(equal(2))
    
    with description('is_valid_service_type'):
        with it('retorna True per "aeat"'):
            expect(SiiServiceFactory.is_valid_service_type('aeat')).to(be_true)
        
        with it('retorna True per "atc"'):
            expect(SiiServiceFactory.is_valid_service_type('atc')).to(be_true)
        
        with it('retorna False per tipus invàlid'):
            expect(SiiServiceFactory.is_valid_service_type('invalid')).to(be_false)
        
        with it('retorna False per None'):
            expect(SiiServiceFactory.is_valid_service_type(None)).to(be_false)
    
    with description('create_service'):
        with before.all:
            self.certificate = '/fake/path/cert.pem'
            self.key = '/fake/path/key.pem'
        
        with it('crea un SiiService per AEAT'):
            service = SiiServiceFactory.create_service(
                SiiServiceFactory.AEAT,
                certificate=self.certificate,
                key=self.key
            )
            expect(service).to(be_a(SiiService))
        
        with it('crea un SiiServiceATC per ATC'):
            service = SiiServiceFactory.create_service(
                SiiServiceFactory.ATC,
                certificate=self.certificate,
                key=self.key
            )
            expect(service).to(be_a(SiiServiceATC))
        
        with it('configura correctament el certificat'):
            service = SiiServiceFactory.create_service(
                SiiServiceFactory.AEAT,
                certificate=self.certificate,
                key=self.key
            )
            expect(service.certificate).to(equal(self.certificate))
        
        with it('configura correctament la clau'):
            service = SiiServiceFactory.create_service(
                SiiServiceFactory.AEAT,
                certificate=self.certificate,
                key=self.key
            )
            expect(service.key).to(equal(self.key))
        
        with it('configura correctament test_mode'):
            service = SiiServiceFactory.create_service(
                SiiServiceFactory.ATC,
                certificate=self.certificate,
                key=self.key,
                test_mode=True
            )
            expect(service.test_mode).to(be_true)
        
        with it('configura correctament la URL'):
            url = 'http://localhost:9090'
            service = SiiServiceFactory.create_service(
                SiiServiceFactory.ATC,
                certificate=self.certificate,
                key=self.key,
                url=url
            )
            expect(service.url).to(equal(url))
        
        with it('llança ValueError per tipus invàlid'):
            def create_invalid():
                SiiServiceFactory.create_service(
                    'invalid',
                    certificate=self.certificate,
                    key=self.key
                )
            expect(create_invalid).to(raise_error(ValueError))
    
    with description('create_deregister_service'):
        with before.all:
            self.certificate = '/fake/path/cert.pem'
            self.key = '/fake/path/key.pem'
        
        with it('crea un SiiDeregisterService per AEAT'):
            service = SiiServiceFactory.create_deregister_service(
                SiiServiceFactory.AEAT,
                certificate=self.certificate,
                key=self.key
            )
            expect(service).to(be_a(SiiDeregisterService))
        
        with it('crea un SiiDeregisterServiceATC per ATC'):
            service = SiiServiceFactory.create_deregister_service(
                SiiServiceFactory.ATC,
                certificate=self.certificate,
                key=self.key
            )
            expect(service).to(be_a(SiiDeregisterServiceATC))
        
        with it('configura correctament el certificat'):
            service = SiiServiceFactory.create_deregister_service(
                SiiServiceFactory.ATC,
                certificate=self.certificate,
                key=self.key
            )
            expect(service.certificate).to(equal(self.certificate))
        
        with it('llança ValueError per tipus invàlid'):
            def create_invalid():
                SiiServiceFactory.create_deregister_service(
                    'invalid',
                    certificate=self.certificate,
                    key=self.key
                )
            expect(create_invalid).to(raise_error(ValueError))
    
    with description('integració AEAT vs ATC'):
        with before.all:
            self.certificate = '/fake/path/cert.pem'
            self.key = '/fake/path/key.pem'
        
        with it('els serveis AEAT i ATC són diferents classes'):
            service_aeat = SiiServiceFactory.create_service(
                SiiServiceFactory.AEAT,
                certificate=self.certificate,
                key=self.key
            )
            service_atc = SiiServiceFactory.create_service(
                SiiServiceFactory.ATC,
                certificate=self.certificate,
                key=self.key
            )
            expect(type(service_aeat)).not_to(equal(type(service_atc)))
        
        with it('ambdós serveis tenen mètode send'):
            service_aeat = SiiServiceFactory.create_service(
                SiiServiceFactory.AEAT,
                certificate=self.certificate,
                key=self.key
            )
            service_atc = SiiServiceFactory.create_service(
                SiiServiceFactory.ATC,
                certificate=self.certificate,
                key=self.key
            )
            expect(service_aeat).to(have_property('send'))
            expect(service_atc).to(have_property('send'))
        
        with it('ambdós serveis deregister tenen mètode deregister'):
            service_aeat = SiiServiceFactory.create_deregister_service(
                SiiServiceFactory.AEAT,
                certificate=self.certificate,
                key=self.key
            )
            service_atc = SiiServiceFactory.create_deregister_service(
                SiiServiceFactory.ATC,
                certificate=self.certificate,
                key=self.key
            )
            expect(service_aeat).to(have_property('deregister'))
            expect(service_atc).to(have_property('deregister'))
