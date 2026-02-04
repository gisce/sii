# -*- coding: utf-8 -*-
"""
Test de validació d'una factura ATC real contra l'especificació oficial
Utilitzant fixtures reals
"""
from expects import *
from mamba import description, context, it, before
from decimal import Decimal
from lxml import etree
import os

from sii.models.basic_models import *
from sii.atc.resource import SIIATC


def dict_to_xml(tag, d, nsmap=None):
    """
    Converteix un diccionari a XML recursivament

    :param tag: Tag principal
    :param d: Diccionari amb les dades
    :param nsmap: Mapa de namespaces
    """
    elem = etree.Element(tag, nsmap=nsmap)
    for key, val in d.items():
        if isinstance(val, dict):
            child = dict_to_xml(key, val)
            elem.append(child)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    child = dict_to_xml(key, item)
                    elem.append(child)
                else:
                    child = etree.Element(key)
                    child.text = str(item)
                    elem.append(child)
        else:
            child = etree.Element(key)
            child.text = str(val)
            elem.append(child)
    return elem


def validate_against_xsd(xml_string, xsd_path):
    """
    Valida un XML contra un XSD

    :param xml_string: String amb el contingut XML
    :param xsd_path: Path al fitxer XSD
    :return: (is_valid, error_log)
    """
    try:
        # Parseja el XML
        xml_doc = etree.fromstring(xml_string)

        # Carrega l'XSD
        with open(xsd_path, 'r') as f:
            xsd_doc = etree.parse(f)

        # Crea el validador
        xsd_schema = etree.XMLSchema(xsd_doc)

        # Valida
        is_valid = xsd_schema.validate(xml_doc)
        error_log = xsd_schema.error_log if not is_valid else None

        return is_valid, error_log
    except Exception as e:
        return False, str(e)


with description('Validació factura real ATC'):
    
    with before.all:
        # Crear partner
        country = Country(code='ES', is_eu_member=False)
        self.partner = Partner(
            name='Angulo Carmona, Milagrosa',
            nif='11111111H',
            country=country
        )
        
        # Crear company
        company_partner = Partner(
            name=u'Comercializadora Energia Canarias SL',
            nif='B12345678',
            country=country
        )
        self.company = Company(company_partner)
        
        # Crear taxes
        tax_igic_7 = Tax('IGIC 7%', 0.07, 'percent')
        tax_igic_exento = Tax('IGIC Exento', 0.0, 'percent')
        
        # Línies de factura
        lines = [
            InvoiceLine(
                price_subtotal=Decimal('4.7'),
                invoice_line_tax_id=[tax_igic_7]
            ),
            InvoiceLine(
                price_subtotal=Decimal('40.56'),
                invoice_line_tax_id=[tax_igic_exento]
            ),
            InvoiceLine(
                price_subtotal=Decimal('17.89'),
                invoice_line_tax_id=[]
            )
        ]
        
        # Taxes agregades
        tax_lines = [
            InvoiceTax(
                name='IGIC 7%',
                base=Decimal('4.7'),
                tax_amount=Decimal('0.33'),
                tax_id=tax_igic_7
            ),
            InvoiceTax(
                name='IGIC Exento',
                base=Decimal('40.56'),
                tax_amount=Decimal('0.0'),
                tax_id=tax_igic_exento
            )
        ]
        
        # Període i journal
        period = Period('12/2025')
        journal = Journal('Ventas')
        fiscal_position = FiscalPosition('Canarias')
        
        # Address amb comunitat canària
        canarias = ComunidadAutonoma('05', 'Canarias')
        state = State(canarias)
        address = ResPartnerAddress(state)
        
        # Crear factura
        self.invoice = Invoice(
            journal_id=journal,
            number='E25OR0000637008',
            invoice_type='out_invoice',
            partner_id=self.partner,
            address_contact_id=address,
            company_id=self.company,
            amount_total=Decimal('66.45'),
            amount_untaxed=Decimal('63.15'),
            amount_tax=Decimal('3.30'),
            period_id=period,
            date_invoice='2025-12-11',
            tax_line=tax_lines,
            sii_registered=False,
            rectificative_type=False,
            fiscal_position=fiscal_position,
            invoice_line=lines,
            sii_description='Venta Suministro de Energía',
            sii_out_clave_regimen_especial='01',
            sii_out_clave_regimen_especial_atc='01'
        )
        
        # Generar SII
        sii = SIIATC(self.invoice)
        self.sii_obj = sii.generate_object()
        print(self.sii_obj)
        #self.xml_string = sii.generate_xml()

        # Defineix namespaces
        nsmap = {
            None: 'https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/igic/ws/SuministroLR.xsd',
            'sii': 'https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/igic/ws/SuministroInformacion.xsd'
        }

        # Converteix a XML amb namespaces
        root = dict_to_xml('SuministroLRFacturasEmitidas',
                           self.sii_obj['SuministroLRFacturasEmitidas'],
                           nsmap=nsmap)
        self.xml_string = etree.tostring(root, encoding='UTF-8', xml_declaration=True,
                       pretty_print=True)
        # Guardar XML
        try:
            os.makedirs('/tmp/atc')
        except OSError:
            pass
        with open('/tmp/atc/factura_real_completa.xml', 'w') as f:
            f.write(self.xml_string)
    
    with context('Estructura bàsica'):
        with it('genera objecte SII vàlid'):
            expect(self.sii_obj).to(have_key('SuministroLRFacturasEmitidas'))
        
        with it('conté Cabecera'):
            cabecera = self.sii_obj['SuministroLRFacturasEmitidas']['Cabecera']
            expect(cabecera).to(have_keys('IDVersionSii', 'Titular', 'TipoComunicacion'))
        
        with it('la versió és 1.0'):
            cabecera = self.sii_obj['SuministroLRFacturasEmitidas']['Cabecera']
            expect(cabecera['IDVersionSii']).to(equal('1.0'))
        
        with it('el tipus de comunicació és A0'):
            cabecera = self.sii_obj['SuministroLRFacturasEmitidas']['Cabecera']
            expect(cabecera['TipoComunicacion']).to(equal('A0'))
    
    with context('Dades del titular'):
        with it('conté el NIF correcte'):
            cabecera = self.sii_obj['SuministroLRFacturasEmitidas']['Cabecera']
            expect(cabecera['Titular']['NIF']).to(equal('B12345678'))
        
        with it('conté el nom de la companyia'):
            cabecera = self.sii_obj['SuministroLRFacturasEmitidas']['Cabecera']
            expect(cabecera['Titular']['NombreRazon']).to(equal(u'Comercializadora Energia Canarias SL'))
    
    with context('Dades de la factura'):
        with it('conté RegistroLRFacturasEmitidas'):
            expect(self.sii_obj['SuministroLRFacturasEmitidas']).to(have_key('RegistroLRFacturasEmitidas'))
        
        with it('el número de factura és correcte'):
            registro = self.sii_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            expect(registro['IDFactura']['NumSerieFacturaEmisor']).to(equal('E25OR0000637008'))
        
        with it('conté el període correcte'):
            registro = self.sii_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            expect(registro['PeriodoLiquidacion']['Ejercicio']).to(equal('2025'))
            expect(registro['PeriodoLiquidacion']['Periodo']).to(equal('12'))
        
        with it('el tipus de factura és F1'):
            registro = self.sii_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            expect(registro['FacturaExpedida']['TipoFactura']).to(equal('F1'))
        
        with it('la clau de règim és 01'):
            registro = self.sii_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            expect(registro['FacturaExpedida']['ClaveRegimenEspecialOTrascendencia']).to(equal('01'))
        
        with it('conté Contraparte'):
            registro = self.sii_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            expect(registro['FacturaExpedida']).to(have_key('Contraparte'))
            expect(registro['FacturaExpedida']['Contraparte']['NIF']).to(equal('11111111H'))
    
    with context('Desglose IGIC'):
        with it('conté TipoDesglose'):
            registro = self.sii_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            expect(registro['FacturaExpedida']).to(have_key('TipoDesglose'))
        
        with it('conté DesgloseFactura'):
            registro = self.sii_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            expect(registro['FacturaExpedida']['TipoDesglose']).to(have_key('DesgloseFactura'))
        
        with it('utilitza DesgloseIGIC (no IVA)'):
            registro = self.sii_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            desglose = registro['FacturaExpedida']['TipoDesglose']['DesgloseFactura']
            expect(desglose['Sujeta']['NoExenta']).to(have_key('DesgloseIGIC'))
            expect(desglose['Sujeta']['NoExenta']).not_to(have_key('DesgloseIVA'))
        
        with it('conté detalls IGIC'):
            registro = self.sii_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            desglose_igic = registro['FacturaExpedida']['TipoDesglose']['DesgloseFactura']['Sujeta']['NoExenta']['DesgloseIGIC']
            expect(desglose_igic).to(have_key('DetalleIGIC'))
        
        with it('el tipus impositiu és vàlid (7%)'):
            registro = self.sii_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            detalles = registro['FacturaExpedida']['TipoDesglose']['DesgloseFactura']['Sujeta']['NoExenta']['DesgloseIGIC']['DetalleIGIC']
            if not isinstance(detalles, list):
                detalles = [detalles]
            # Buscar el detall amb IGIC 7%
            tipus_trobat = any(
                Decimal(str(d['TipoImpositivo'])) == Decimal('7.0') or 
                float(d['TipoImpositivo']) == 7.0 
                for d in detalles
            )
            expect(tipus_trobat).to(be_true)
        
        with it('conté operacions exentes'):
            registro = self.sii_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            desglose = registro['FacturaExpedida']['TipoDesglose']['DesgloseFactura']
            expect(desglose['Sujeta']).to(have_key('Exenta'))
    
    with context('XML generat'):
        with it('és ben format'):
            xml_bytes = self.xml_string.encode('utf-8')
            root = etree.fromstring(xml_bytes)
            expect(root).not_to(be_none)
        
        with it('conté els namespaces IGIC'):
            expect(self.xml_string).to(contain('igic/ws/'))
            expect(self.xml_string).not_to(contain('iva/ws/'))
        
        with it('es guarda a /tmp/atc/'):
            expect(os.path.exists('/tmp/atc/factura_real_completa.xml')).to(be_true)
