# coding=utf-8
"""
Tests de serialització per SII ATC (IGIC)

Aquest fitxer conté els tests amb Mamba per verificar que la generació
d'objectes XML per l'ATC funciona correctament amb IGIC.
"""

from sii.atc.resource import SIIATC, SIIATCDeregister
from sii.atc.constants import TIPO_IMPOSITIVO_IGIC_VALUES, CLAVE_REGIMEN_ESPECIAL_VALUES
from sii.utils import unidecode_str, VAT
from expects import *
from datetime import datetime
from spec.testing_data_atc import DataGeneratorATC
from mamba import *
import os


def group_by_tax_rate(igic_values):
    """Agrupa valors d'IGIC per tipus impositiu"""
    aux_igic_values = {}

    for igic in igic_values:
        tipo_impositivo = igic['TipoImpositivo']
        base_imponible = igic['BaseImponible']
        cuota_key = (
            'CuotaSoportada'
            if 'CuotaSoportada' in igic.keys()
            else 'CuotaRepercutida'
        )
        cuota = igic[cuota_key]
        if tipo_impositivo in aux_igic_values:
            aux = aux_igic_values[tipo_impositivo]
            aux['BaseImponible'] += base_imponible
            aux[cuota_key] += cuota
        else:
            aux_igic_values[tipo_impositivo] = igic.copy()

    return aux_igic_values


with description('El XML Generado per ATC'):
    with before.all:
        self.data_gen = DataGeneratorATC()

    with description('en la capçalera'):
        with before.all:
            # Factura d'exemple per comprovar camps comuns
            self.invoice = self.data_gen.get_out_invoice()
            self.invoice_obj = SIIATC(self.invoice).generate_object()
            self.cabecera = (
                self.invoice_obj['SuministroLRFacturasEmitidas']['Cabecera']
            )

        with it('la versió és "1.0"'):
            expect(self.cabecera['IDVersionSii']).to(equal('1.0'))

        with it('el titular té NIF'):
            expect(self.cabecera['Titular']).to(have_key('NIF'))

        with it('el titular té NombreRazon'):
            expect(self.cabecera['Titular']).to(have_key('NombreRazon'))

        with it('el tipus de comunicació és A0 (alta)'):
            expect(self.cabecera['TipoComunicacion']).to(equal('A0'))

    with description('en factures emeses'):
        with before.all:
            self.invoice = self.data_gen.get_out_invoice()
            self.invoice_obj = SIIATC(self.invoice).generate_object()
            self.factura_emitida = (
                self.invoice_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']
            )

        with it('conté PeriodoLiquidacion'):
            expect(self.factura_emitida).to(have_key('PeriodoLiquidacion'))

        with it('conté IDFactura'):
            expect(self.factura_emitida).to(have_key('IDFactura'))

        with it('conté FacturaExpedida'):
            expect(self.factura_emitida).to(have_key('FacturaExpedida'))

        with it('conté Contraparte'):
            expect(self.factura_emitida['FacturaExpedida']).to(have_key('Contraparte'))

        with it('la ClaveRegimenEspecialOTrascendencia és "08" (IGIC)'):
            clave = self.factura_emitida['FacturaExpedida']['ClaveRegimenEspecialOTrascendencia']
            expect(clave).to(equal('08'))

        with it('el TipoFactura és vàlid'):
            tipo = self.factura_emitida['FacturaExpedida']['TipoFactura']
            valid_tipos = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'R1', 'R2', 'R3', 'R4', 'R5']
            expect(tipo in valid_tipos).to(be_true)

    with description('amb IGIC en factures emeses'):
        with before.all:
            self.invoice = self.data_gen.get_out_invoice()
            self.invoice_obj = SIIATC(self.invoice).generate_object()
            self.factura_expedida = (
                self.invoice_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']['FacturaExpedida']
            )
            # Accedim al desglose correcte segons l'estructura
            tipo_desglose = self.factura_expedida['TipoDesglose']
            if 'DesgloseFactura' in tipo_desglose:
                self.desglose_igic = tipo_desglose['DesgloseFactura']['Sujeta']['NoExenta']['DesgloseIGIC']
            else:
                # DesgloseTipoOperacion
                if 'PrestacionServicios' in tipo_desglose['DesgloseTipoOperacion']:
                    self.desglose_igic = tipo_desglose['DesgloseTipoOperacion']['PrestacionServicios']['Sujeta']['NoExenta']['DesgloseIGIC']
                else:
                    self.desglose_igic = tipo_desglose['DesgloseTipoOperacion']['Entrega']['Sujeta']['NoExenta']['DesgloseIGIC']

        with it('conté TipoDesglose'):
            expect(self.factura_expedida).to(have_key('TipoDesglose'))

        with it('el TipoDesglose conté DesgloseIGIC (no DesgloseIVA)'):
            # Verificar que no hi ha DesgloseIVA enlloc
            tipo_desg_str = str(self.factura_expedida['TipoDesglose'])
            expect('DesgloseIVA' in tipo_desg_str).to(be_false)
            expect('DesgloseIGIC' in tipo_desg_str).to(be_true)

        with it('DesgloseIGIC conté DetalleIGIC'):
            expect(self.desglose_igic).to(have_key('DetalleIGIC'))

        with it('cada DetalleIGIC té BaseImponible'):
            detalles = self.desglose_igic['DetalleIGIC']
            for detalle in detalles:
                expect(detalle).to(have_key('BaseImponible'))

        with it('cada DetalleIGIC té TipoImpositivo vàlid'):
            detalles = self.desglose_igic['DetalleIGIC']
            from sii.atc.constants import get_valid_igic_rates
            # Utilitzar la data de la factura de test (2016)
            valid_rates = get_valid_igic_rates('2016-12-31')
            for detalle in detalles:
                expect(detalle).to(have_key('TipoImpositivo'))
                tipo_imp = float(detalle['TipoImpositivo'])
                expect(tipo_imp in valid_rates).to(be_true)

        with it('cada DetalleIGIC té CuotaRepercutida'):
            detalles = self.desglose_igic['DetalleIGIC']
            for detalle in detalles:
                expect(detalle).to(have_key('CuotaRepercutida'))

    with description('en factures rebudes'):
        with before.all:
            self.invoice = self.data_gen.get_in_invoice()
            self.invoice_obj = SIIATC(self.invoice).generate_object()
            self.factura_recibida = (
                self.invoice_obj['SuministroLRFacturasRecibidas']['RegistroLRFacturasRecibidas']
            )

        with it('conté PeriodoLiquidacion'):
            expect(self.factura_recibida).to(have_key('PeriodoLiquidacion'))

        with it('conté IDFactura'):
            expect(self.factura_recibida).to(have_key('IDFactura'))

        with it('conté FacturaRecibida'):
            expect(self.factura_recibida).to(have_key('FacturaRecibida'))

        with it('la ClaveRegimenEspecialOTrascendencia és "08" (IGIC)'):
            clave = self.factura_recibida['FacturaRecibida']['ClaveRegimenEspecialOTrascendencia']
            expect(clave).to(equal('08'))

    with description('amb IGIC en factures rebudes'):
        with before.all:
            self.invoice = self.data_gen.get_in_invoice()
            self.invoice_obj = SIIATC(self.invoice).generate_object()
            self.factura_recibida = (
                self.invoice_obj['SuministroLRFacturasRecibidas']['RegistroLRFacturasRecibidas']['FacturaRecibida']
            )

        with it('conté DesgloseFactura'):
            expect(self.factura_recibida).to(have_key('DesgloseFactura'))

        with it('DesgloseFactura conté DesgloseIGIC (no DesgloseIVA)'):
            expect(self.factura_recibida['DesgloseFactura']).to(have_key('DesgloseIGIC'))
            expect(self.factura_recibida['DesgloseFactura']).not_to(have_key('DesgloseIVA'))

        with it('cada DetalleIGIC té CuotaSoportada'):
            detalles = self.factura_recibida['DesgloseFactura']['DesgloseIGIC']['DetalleIGIC']
            for detalle in detalles:
                expect(detalle).to(have_key('CuotaSoportada'))

    with description('en factures rectificatives'):
        with before.all:
            self.invoice = self.data_gen.get_out_refund()
            self.invoice_obj = SIIATC(self.invoice).generate_object()
            self.factura_expedida = (
                self.invoice_obj['SuministroLRFacturasEmitidas']['RegistroLRFacturasEmitidas']['FacturaExpedida']
            )

        with it('el TipoFactura comença per R (rectificativa)'):
            tipo = self.factura_expedida['TipoFactura']
            expect(tipo).to(start_with('R'))

    with description('en baixa de factures'):
        with before.all:
            self.invoice = self.data_gen.get_out_invoice()
            self.deregister_obj = SIIATCDeregister(self.invoice).generate_deregister_object()

        with it('conté Cabecera'):
            expect(self.deregister_obj['BajaLRFacturasEmitidas']).to(have_key('Cabecera'))

        with it('conté RegistroLRBajaExpedidas'):
            expect(self.deregister_obj['BajaLRFacturasEmitidas']).to(have_key('RegistroLRBajaExpedidas'))

        with it('RegistroLRBajaExpedidas conté PeriodoLiquidacion'):
            expect(self.deregister_obj['BajaLRFacturasEmitidas']['RegistroLRBajaExpedidas']).to(
                have_key('PeriodoLiquidacion')
            )

        with it('RegistroLRBajaExpedidas conté IDFactura'):
            expect(self.deregister_obj['BajaLRFacturasEmitidas']['RegistroLRBajaExpedidas']).to(
                have_key('IDFactura')
            )

    with description('càlcul de valors IGIC'):
        with before.all:
            from sii.atc.resource import get_igic_values
            self.invoice = self.data_gen.get_out_invoice()
            self.igic_values = get_igic_values(self.invoice, in_invoice=False)

        with it('detecta que està subjecta a IGIC'):
            expect(self.igic_values['sujeta_a_igic']).to(be_true)

        with it('conté detalle_igic'):
            expect(self.igic_values).to(have_key('detalle_igic'))

        with it('detalle_igic és una llista'):
            expect(self.igic_values['detalle_igic']).to(be_a(list))

        with it('cada detall té BaseImponible, TipoImpositivo i Cuota'):
            for detalle in self.igic_values['detalle_igic']:
                expect(detalle).to(have_key('BaseImponible'))
                expect(detalle).to(have_key('TipoImpositivo'))
                # Factura emesa: té CuotaRepercutida
                expect(detalle).to(have_key('CuotaRepercutida'))

    with description('comparació IGIC vs IVA'):
        with it('IGIC té 7 tipus impositius vs 4 d\'IVA'):
            expect(len(TIPO_IMPOSITIVO_IGIC_VALUES)).to(equal(7))

        with it('IGIC inclou 9.5% i 13.5% (no presents a IVA)'):
            # 9.5% és un tipus actual sempre vàlid
            expect(9.5 in TIPO_IMPOSITIVO_IGIC_VALUES).to(be_true)
            # 13.5% només és vàlid entre 2012-2019
            from sii.atc.constants import get_valid_igic_rates
            rates_2016 = get_valid_igic_rates('2016-12-31')
            expect(13.5 in rates_2016).to(be_true)
            # Però no està als tipus actuals (>2019)
            expect(13.5 not in TIPO_IMPOSITIVO_IGIC_VALUES).to(be_true)

        with it('la clau de règim "08" és vàlida per IGIC'):
            expect('08' in CLAVE_REGIMEN_ESPECIAL_VALUES).to(be_true)
