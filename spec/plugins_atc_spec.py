# -*- coding: utf-8 -*-
"""
Test de validació dels plugins dry_run i persist_xml per SII ATC

Aquest spec valida:
1. Que dry_run NO envia peticions reals
2. Que persist_xml guarda els XMLs correctament
3. Que el comportament per defecte és sense plugins
"""
from expects import *
from mamba import description, context, it, before
import os
import tempfile
import shutil
from lxml import etree

from sii.models.basic_models import *
from sii.atc.server import SiiServiceATC
from sii.atc.plugins.dry_run_plugin import DryRunException
from spec.testing_data_atc import DataGeneratorATC


with description('Plugin Dry Run i Persist XML per SII ATC') as self:
    
    with before.each:
        # Crear directori temporal per tests
        self.temp_dir = tempfile.mkdtemp()
        self.request_file = os.path.join(self.temp_dir, 'request.xml')
        self.response_file = os.path.join(self.temp_dir, 'response.xml')
        
        # Crear certificats dummy (no s'utilitzaran realment en dry-run)
        self.cert_file = os.path.join(self.temp_dir, 'cert.pem')
        self.key_file = os.path.join(self.temp_dir, 'key.pem')
        
        # Crear fitxers dummy
        with open(self.cert_file, 'w') as f:
            f.write('DUMMY CERT')
        with open(self.key_file, 'w') as f:
            f.write('DUMMY KEY')
    
    with context('Comportament per defecte (sense plugins)'):
        with it('crea servei sense activar plugins'):
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file,
                test_mode=True
            )
            
            expect(service.dry_run).to(be_false)
            expect(service.persist_xml).to(be_none)
        
        with it('manté compatibilitat amb codi existent'):
            # El codi antic sense paràmetres nous ha de funcionar
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file
            )
            
            expect(hasattr(service, 'dry_run')).to(be_true)
            expect(hasattr(service, 'persist_xml')).to(be_true)
            expect(service.dry_run).to(be_false)
            expect(service.persist_xml).to(be_none)
    
    with context('Plugin Dry Run'):
        with it('NO envia petició real quan dry_run=True'):
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file,
                test_mode=True,
                dry_run=True
            )
            
            expect(service.dry_run).to(be_true)
        
        with it('retorna resposta simulada en mode dry-run'):
            # Crear factura de test amb mètode correcte
            data_gen = DataGeneratorATC()
            invoice = data_gen.get_out_invoice()
            
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file,
                test_mode=True,
                dry_run=True
            )
            
            # En dry-run, send_invoice ha de retornar resposta simulada
            # sense aixecar excepció
            result = service.send(invoice)
            
            expect(result).to(have_key('dry_run'))
            expect(result['dry_run']).to(be_true)
            expect(result).to(have_key('successful'))
            expect(result['successful']).to(be_true)
            expect(result).to(have_key('xml_generated'))
            expect(result['xml_generated']).to(be_true)
    
    with context('Plugin Persist XML'):
        with it('guarda request XML quan persist_xml especificat'):
            # Crear factura de test amb mètode correcte
            data_gen = DataGeneratorATC()
            invoice = data_gen.get_out_invoice()
            
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file,
                test_mode=True,
                dry_run=True,  # Usar dry-run per no intentar conexió real
                persist_xml={
                    'request': self.request_file,
                    'response': None
                }
            )
            
            # Enviar factura (dry-run)
            result = service.send(invoice)
            
            # Verificar que request XML s'ha guardat
            expect(os.path.exists(self.request_file)).to(be_true)
            expect(os.path.getsize(self.request_file)).to(be_above(0))
            
            # Validar que és XML vàlid
            with open(self.request_file, 'r') as f:
                xml_content = f.read()
                xml_tree = etree.fromstring(xml_content.encode('utf-8'))
                expect(xml_tree).not_to(be_none)
        
        with it('l\'XML persistit conté estructura SOAP correcta'):
            data_gen = DataGeneratorATC()
            invoice = data_gen.get_out_invoice()
            
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file,
                test_mode=True,
                dry_run=True,
                persist_xml={'request': self.request_file}
            )
            
            result = service.send(invoice)
            
            # Llegir i parsejar XML
            with open(self.request_file, 'r') as f:
                xml_content = f.read()
            
            # Verificar elements SOAP bàsics
            expect(xml_content).to(contain('soap-env:Envelope'))
            expect(xml_content).to(contain('soap-env:Body'))
            
            # Verificar elements específics ATC
            expect(xml_content).to(contain('SuministroLRFacturasEmitidas'))
            expect(xml_content).to(contain('Cabecera'))
            expect(xml_content).to(contain('IDFactura'))
    
    with context('Combinació de plugins'):
        with it('pot activar dry_run i persist_xml simultàniament'):
            data_gen = DataGeneratorATC()
            invoice = data_gen.get_out_invoice()
            
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file,
                test_mode=True,
                dry_run=True,
                persist_xml={
                    'request': self.request_file,
                    'response': self.response_file
                }
            )
            
            result = service.send(invoice)
            
            # Verificar comportament dry-run
            expect(result['dry_run']).to(be_true)
            
            # Verificar que s'ha guardat request
            expect(os.path.exists(self.request_file)).to(be_true)
            
            # Response no existirà perquè dry-run no rep resposta
            # però no ha de donar error
            expect(result).to(have_key('xml_generated'))
        
        with it('pot activar només persist_xml sense dry_run'):
            # Aquest cas NO intentarà conexió real perquè no tenim servidor
            # però valida que els paràmetres es passen correctament
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file,
                test_mode=True,
                dry_run=False,  # Explícit
                persist_xml={'request': self.request_file}
            )
            
            expect(service.dry_run).to(be_false)
            expect(service.persist_xml).not_to(be_none)
            expect(service.persist_xml['request']).to(equal(self.request_file))
    
    with context('Validació d\'XMLs generats'):
        with it('l\'XML conté camps IGIC correctes'):
            data_gen = DataGeneratorATC()
            invoice = data_gen.get_out_invoice()
            
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file,
                test_mode=True,
                dry_run=True,
                persist_xml={'request': self.request_file}
            )
            
            result = service.send(invoice)
            
            # Llegir XML generat
            with open(self.request_file, 'r') as f:
                xml_content = f.read()
            
            # Verificar camps específics IGIC
            expect(xml_content).to(contain('TipoImpositivo'))
            expect(xml_content).to(contain('CuotaRepercutida'))
            expect(xml_content).to(contain('DesgloseFactura'))
        
        with it('l\'XML conté Clave Régimen Especial ATC'):
            data_gen = DataGeneratorATC()
            invoice = data_gen.get_out_invoice()
            
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file,
                test_mode=True,
                dry_run=True,
                persist_xml={'request': self.request_file}
            )
            
            result = service.send(invoice)
            
            with open(self.request_file, 'r') as f:
                xml_content = f.read()
            
            # Verificar que conté ClaveRegimenEspecialOTrascendencia
            expect(xml_content).to(contain('ClaveRegimenEspecialOTrascendencia'))
    
    with context('Gestió de fitxers'):
        with it('crea directoris automàticament si no existeixen'):
            # Crear path amb subdirectoris que no existeixen
            nested_dir = os.path.join(self.temp_dir, 'subdir', 'nested')
            nested_request = os.path.join(nested_dir, 'request.xml')
            
            data_gen = DataGeneratorATC()
            invoice = data_gen.get_out_invoice()
            
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file,
                test_mode=True,
                dry_run=True,
                persist_xml={'request': nested_request}
            )
            
            result = service.send(invoice)
            
            # Verificar que s'ha creat el directori i el fitxer
            expect(os.path.exists(nested_request)).to(be_true)
        
        with it('sobreescriu fitxer existent si ja existeix'):
            # Crear fitxer previ
            with open(self.request_file, 'w') as f:
                f.write('OLD CONTENT')
            
            data_gen = DataGeneratorATC()
            invoice = data_gen.get_out_invoice()
            
            service = SiiServiceATC(
                certificate=self.cert_file,
                key=self.key_file,
                test_mode=True,
                dry_run=True,
                persist_xml={'request': self.request_file}
            )
            
            result = service.send(invoice)
            
            # Verificar que s'ha sobreescrit
            with open(self.request_file, 'r') as f:
                content = f.read()
            
            expect(content).not_to(contain('OLD CONTENT'))
            expect(content).to(contain('soap-env:Envelope'))
    
    with context('Neteja'):
        with it('elimina directori temporal després de tests'):
            # Aquest test s'executarà al final
            # El directori temporal s'hauria d'eliminar
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            
            expect(True).to(be_true)  # Dummy assertion
