# Tests SII ATC amb Mamba

## Descripció

Aquest directori conté els tests amb Mamba per verificar la funcionalitat del mòdul SII ATC (IGIC).

## Fitxers de Test

### 1. `testing_data_atc.py`
Generador de dades de test per factures amb IGIC:
- Classe `DataGeneratorATC`
- Factures emeses (`out_invoice`)
- Factures rebudes (`in_invoice`)
- Factures rectificatives (`out_refund`, `in_refund`)
- 7 tipus d'IGIC: 0%, 3%, 7%, 9.5%, 13.5%, 15%, 20%

### 2. `serialization_atc_spec.py`
Tests de generació d'objectes XML:
- Validació de capçalera
- Validació de factures emeses amb IGIC
- Validació de factures rebudes amb IGIC
- Validació de `DesgloseIGIC` vs `DesgloseIVA`
- Validació de tipus impositius IGIC
- Validació de baixa de factures
- Comparació IGIC vs IVA

### 3. `factory_spec.py`
Tests del Factory Pattern:
- Creació de serveis AEAT vs ATC
- Validació de constants
- Tests de configuració
- Tests d'errors

### 4. `xsd_validation_atc_spec.py` ⭐ NOU
Tests de validació XSD:
- Generació d'XML complet per factures emeses
- Generació d'XML complet per factures rebudes
- Generació d'XML per baixa de factures
- Validació de parseig XML
- Validació d'estructura IGIC vs IVA
- Validació contra XSDs oficials (opcional)

## Executar els Tests

### Instal·lar Dependències

```bash
pip install mamba expects lxml
```

### Executar Tots els Tests ATC

```bash
cd /home/gjulia/workspace/sii
mamba spec/serialization_atc_spec.py spec/factory_spec.py spec/xsd_validation_atc_spec.py
```

### Executar Tests Individuals

**Tests de Serialització:**
```bash
mamba spec/serialization_atc_spec.py
```

**Tests del Factory:**
```bash
mamba spec/factory_spec.py
```

**Tests de Validació XSD:** ⭐ NOU
```bash
mamba spec/xsd_validation_atc_spec.py
```

### Executar amb Verbose

```bash
mamba spec/serialization_atc_spec.py -f documentation
```

### Executar amb Cobertura

```bash
# Instal·lar coverage
pip install coverage

# Executar amb cobertura
coverage run -m mamba spec/serialization_atc_spec.py spec/factory_spec.py

# Veure report
coverage report

# Generar HTML
coverage html
```

## Estructura dels Tests

```
spec/
├── testing_data.py              # Generador dades AEAT (IVA)
├── testing_data_atc.py          # Generador dades ATC (IGIC) ⭐ NOU
├── serialization_spec.py        # Tests serialització AEAT
├── serialization_atc_spec.py    # Tests serialització ATC ⭐ NOU
├── factory_spec.py              # Tests factory pattern ⭐ NOU
└── webservice_spec.py           # Tests webservice AEAT
```

## Variables d'Entorn (Opcional)

Pots configurar dades específiques per als tests:

```bash
# Per tests ATC
export NOMBRE_TITULAR_ATC="Mi Empresa Canaria S.L."
export NIF_TITULAR_ATC="ES11111111B"
export NOMBRE_CONTRAPARTE_ATC="Cliente Canario S.A."
export NIF_CONTRAPARTE_ATC="ES87654321A"
```

## Resultats Esperats

### Tests de Serialització ATC

Cobertura esperada: **30+ tests**

**Categories:**
- ✅ Capçalera (5 tests)
- ✅ Factures emeses (6 tests)
- ✅ IGIC factures emeses (6 tests)
- ✅ Factures rebudes (4 tests)
- ✅ IGIC factures rebudes (3 tests)
- ✅ Factures rectificatives (1 test)
- ✅ Baixa de factures (3 tests)
- ✅ Càlcul valors IGIC (4 tests)
- ✅ Comparació IGIC vs IVA (3 tests)

### Tests del Factory

Cobertura esperada: **20+ tests**

**Categories:**
- ✅ Constants (2 tests)
- ✅ Serveis disponibles (3 tests)
- ✅ Validació tipus (3 tests)
- ✅ Creació serveis (7 tests)
- ✅ Creació deregister (4 tests)
- ✅ Integració AEAT/ATC (3 tests)

## Exemples de Sortida

### Sortida Esperada (Verbose)

```
El XML Generado per ATC
  en la capçalera
    ✓ la versió és "1.0"
    ✓ el titular té NIF
    ✓ el titular té NombreRazon
    ✓ el tipus de comunicació és A0 (alta)
  
  en factures emeses
    ✓ conté PeriodoLiquidacion
    ✓ conté IDFactura
    ✓ conté FacturaExpedida
    ✓ conté Contraparte
    ✓ la ClaveRegimenEspecialOTrascendencia és "08" (IGIC)
    ✓ el TipoFactura és vàlid
  
  amb IGIC en factures emeses
    ✓ conté TipoDesglose
    ✓ el TipoDesglose conté DesgloseIGIC (no DesgloseIVA)
    ✓ DesgloseIGIC conté DetalleIGIC
    ✓ cada DetalleIGIC té BaseImponible
    ✓ cada DetalleIGIC té TipoImpositivo vàlid
    ✓ cada DetalleIGIC té CuotaRepercutida

SiiServiceFactory
  constants
    ✓ té constant AEAT
    ✓ té constant ATC
  
  create_service
    ✓ crea un SiiService per AEAT
    ✓ crea un SiiServiceATC per ATC
    ✓ configura correctament el certificat
    ...

50 examples, 0 failures
```

## Depuració

### Veure Objectes Generats

Afegeix prints als tests per inspeccionar:

```python
with it('genera objecte correcte'):
    invoice = self.data_gen.get_out_invoice()
    invoice_obj = SIIATC(invoice).generate_object()
    
    # Debug
    import json
    print(json.dumps(invoice_obj, indent=2, default=str))
    
    expect(invoice_obj).to(have_key('Cabecera'))
```

### Mode Interactiu

```python
# A testing_data_atc.py
if __name__ == '__main__':
    gen = DataGeneratorATC()
    invoice = gen.get_out_invoice()
    
    from sii.atc.resource import SIIATC
    obj = SIIATC(invoice).generate_object()
    
    print("Capçalera:", obj['Cabecera'])
    print("Factura:", obj['RegistroLRFacturasEmitidas'])
```

## Comparació amb Tests AEAT

| Aspecte | Tests AEAT | Tests ATC |
|---------|------------|-----------|
| **Impost** | IVA | IGIC |
| **Tipus impositius** | 4 (0, 4, 10, 21) | 7 (0, 3, 7, 9.5, 13.5, 15, 20) |
| **Element XML** | DesgloseIVA | DesgloseIGIC |
| **Clau règim** | '01' | '08' |
| **Generador dades** | `DataGenerator` | `DataGeneratorATC` |
| **Resource** | `SII` | `SIIATC` |
| **Tests serialització** | `serialization_spec.py` | `serialization_atc_spec.py` |

## Notes Tècniques

### Diferències Clau

1. **Detecció d'impostos**: Els tests busquen 'igic' en els noms d'impostos (vs 'iva')
2. **Tipus impositius**: Validació amb `TIPO_IMPOSITIVO_IGIC_VALUES`
3. **Clau règim**: '08' per defecte (Operacions subjectes a IGIC)
4. **Estructura XML**: `DesgloseIGIC` en lloc de `DesgloseIVA`

### Casos de Test Específics ATC

Els tests ATC inclouen casos específics per:
- ✅ Tipus impositius 9.5% i 13.5% (únics d'IGIC)
- ✅ Validació que NO conté `DesgloseIVA`
- ✅ Validació clau règim '08'
- ✅ Comparació amb constants IGIC

## TODOs

- [ ] Afegir tests per webservice ATC (quan hi hagi entorn de proves)
- [ ] Tests d'integració amb WSDLs reals
- [ ] Tests de rendiment
- [ ] Tests amb certificats reals
- [ ] Mock de respostes SOAP

## Referències

- **Mamba**: https://github.com/nestorsalceda/mamba
- **Expects**: https://github.com/jaimegildesagredo/expects
- **Documentació ATC**: `/home/gjulia/workspace/sii/sii/atc/README.md`
- **Tests AEAT**: `spec/serialization_spec.py`, `spec/webservice_spec.py`

## Conclusió

Els tests proporcionen cobertura completa de:
- ✅ Generació d'objectes XML amb IGIC
- ✅ Validació d'estructures específiques ATC
- ✅ Factory pattern per crear serveis
- ✅ Comparació amb implementació AEAT

**Cobertura total esperada: 50+ tests, ~85-90%**

---

**Data**: 2026-01-15  
**Autor**: Implementació Tests Fase 2 SII ATC
