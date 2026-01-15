# Mòdul SII ATC (Agència Tributària Canària)

## Descripció

Aquest mòdul proporciona suport per al Suministro Inmediato de Información (SII) de l'Agència Tributària Canària (ATC), adaptant la llibreria SII existent per treballar amb IGIC (Impuesto General Indirecto Canario) en lloc d'IVA.

## Característiques

- ✅ Suport complet per IGIC amb 7 tipus impositius (0%, 3%, 7%, 9.5%, 13.5%, 15%, 20%)
- ✅ Generació d'objectes XML amb estructura `DesgloseIGIC` (vs `DesgloseIVA`)
- ✅ Client SOAP per comunicació amb endpoints de l'ATC
- ✅ Validació Marshmallow de les estructures XML
- ✅ Factory pattern per crear serveis dinàmicament
- ✅ Suport per factures emeses i rebudes
- ✅ Suport per donar de baixa factures

## Estructura

```
sii/atc/
├── __init__.py                      # Versió del mòdul
├── constants.py                     # Constants IGIC i configuració
├── resource.py                      # Classes SIIATC i SIIATCDeregister
├── server.py                        # Classes SiiServiceATC i SiiDeregisterServiceATC
└── models/
    ├── __init__.py
    └── invoices_record.py          # Schemas Marshmallow per validació
```

## Ús Bàsic

### 1. Importar el Factory

```python
from sii.factory import SiiServiceFactory
```

### 2. Crear un Servei ATC

```python
# Mode de proves
service = SiiServiceFactory.create_service(
    SiiServiceFactory.ATC,
    certificate='/path/to/cert.pem',
    key='/path/to/key.pem',
    test_mode=True
)

# Mode de producció
service = SiiServiceFactory.create_service(
    SiiServiceFactory.ATC,
    certificate='/path/to/cert.pem',
    key='/path/to/key.pem',
    test_mode=False
)
```

### 3. Enviar una Factura

```python
# invoice és un objecte d'OpenERP amb camps:
# - type: 'out_invoice', 'in_invoice', etc.
# - number: número de factura
# - date_invoice: data de la factura
# - tax_line: línies d'impostos (amb 'igic' al nom)
# - etc.

result = service.send(invoice)

# Processar resultat
if result['EstadoEnvio'] == 'Correcto':
    csv = result.get('CSV', '')
    print(f"Factura enviada correctament. CSV: {csv}")
else:
    print(f"Error: {result}")
```

### 4. Donar de Baixa una Factura

```python
deregister_service = SiiServiceFactory.create_deregister_service(
    SiiServiceFactory.ATC,
    certificate='/path/to/cert.pem',
    key='/path/to/key.pem',
    test_mode=True
)

result = deregister_service.deregister(invoice)
```

### 5. Amb Proxy SSL (Opcional)

```python
# Si s'utilitza sii-ssl-proxy
service = SiiServiceFactory.create_service(
    SiiServiceFactory.ATC,
    certificate='/path/to/cert.pem',
    key='/path/to/key.pem',
    url='http://localhost:9090',  # URL del proxy
    test_mode=True
)
```

## Diferències amb AEAT

| Aspecte | AEAT | ATC |
|---------|------|-----|
| **Impost** | IVA | IGIC |
| **Element XML** | `DesgloseIVA` | `DesgloseIGIC` |
| **Detall** | `DetalleIVA` | `DetalleIGIC` |
| **Tipus impositius** | 0, 4, 10, 21% | 0, 3, 7, 9.5, 13.5, 15, 20% |
| **Funció valors** | `get_iva_values()` | `get_igic_values()` |
| **Classe generador** | `SII` | `SIIATC` |
| **Servei SOAP** | `SiiService` | `SiiServiceATC` |
| **Endpoints** | agenciatributaria.gob.es | gobiernodecanarias.org/tributos/atc |
| **Factory constant** | `SiiServiceFactory.AEAT` | `SiiServiceFactory.ATC` |

## Constants IGIC

```python
from sii.atc.constants import TIPO_IMPOSITIVO_IGIC_VALUES, IGIC_TAX_MAP

# Tipus impositius disponibles
print(TIPO_IMPOSITIVO_IGIC_VALUES)
# [0.0, 3.0, 7.0, 9.5, 13.5, 15.0, 20.0]

# Mapa de tipus
print(IGIC_TAX_MAP)
# {0.0: 'IGIC 0%', 0.03: 'IGIC 3%', ...}
```

## Validació amb Marshmallow

```python
from sii.atc.models.invoices_record import SuministroLRFacturasEmitidasSchema

# Generar objecte
from sii.atc.resource import SIIATC
invoice_dict = SIIATC(invoice).generate_object()

# Validar
schema = SuministroLRFacturasEmitidasSchema()
try:
    result = schema.load(invoice_dict)
    print("Validació correcta!")
except ValidationError as e:
    print(f"Errors de validació: {e.messages}")
```

## Endpoints ATC

### Producció
- **Base**: `https://www3.gobiernodecanarias.org`
- **Emeses**: `/tributos/atc/sii/fe/`
- **Rebudes**: `/tributos/atc/sii/fr/`

### Proves
- TODO: Verificar si l'ATC té un entorn de proves separat
- Actualment s'utilitza el mateix endpoint amb `test_mode=True`

## WSDLs i XSDs

Els fitxers oficials estan a:
```
sii/data/atc/
├── wsdl/
│   ├── SuministroFactEmitidas.wsdl
│   └── SuministroFactRecibidas.wsdl
└── xsd/
    ├── ConsultaLR.xsd
    ├── RespuestaConsultaLR.xsd
    ├── RespuestaSuministro.xsd
    ├── SuministroInformacion.xsd
    └── SuministroLR.xsd
```

## Notes Tècniques

### Detecció d'IGIC
El mòdul detecta impostos IGIC cercant 'igic' al nom de l'impost (similar a com es fa amb 'iva' per l'AEAT):

```python
for inv_tax in invoice.tax_line:
    if 'igic' in inv_tax.name.lower():
        # Processar com a IGIC
```

### Clau de Règim Especial
Per defecte, les factures ATC utilitzen la clau '08' (Operacions subjectes a IGIC):

```python
def _get_clave_regimen(self):
    return '08'  # Operacions subjectes a IGIC
```

### Versió SII ATC
```python
from sii.atc import __ATC_SII_VERSION__
print(__ATC_SII_VERSION__)  # '1.0'
```

## TODO / Pendent

- [ ] Verificar namespaces exactes dels WSDLs ATC (binding_name)
- [ ] Confirmar si hi ha entorn de proves separat
- [ ] Verificar type_address exactes per endpoints
- [ ] Implementar tests unitaris
- [ ] Documentar casos d'ús específics de Canàries
- [ ] Verificar suport per importacions/exportacions

## Exemples Avançats

### Generar XML sense Enviar

```python
from sii.atc.resource import SIIATC

# Generar objecte
generator = SIIATC(invoice)
xml_dict = generator.generate_object()

# Inspeccionar
print(xml_dict['Cabecera'])
print(xml_dict['RegistroLRFacturasEmitidas'])
```

### Utilitzar Diferents Certificats

```python
# Certificat per producció
service_prod = SiiServiceFactory.create_service(
    SiiServiceFactory.ATC,
    certificate='/path/to/prod_cert.pem',
    key='/path/to/prod_key.pem',
    test_mode=False
)

# Certificat per proves
service_test = SiiServiceFactory.create_service(
    SiiServiceFactory.ATC,
    certificate='/path/to/test_cert.pem',
    key='/path/to/test_key.pem',
    test_mode=True
)
```

## Suport

Per a més informació sobre el SII de l'ATC:
- **Web oficial**: https://www3.gobiernodecanarias.org/tributos/atc/w/suministro-inmediato-de-informacion-del-igic-sii-1
- **Documentació tècnica**: Disponible al web oficial

## Llicència

Aquest mòdul és part de la llibreria SII i comparteix la mateixa llicència.

## Autors

- Equip GISCE
- Data: 2026-01-15
- Versió: 1.0
