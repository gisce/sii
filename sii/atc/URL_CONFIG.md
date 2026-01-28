# Configuració URLs ATC (Agencia Tributaria Canaria)

## URLs Oficials

### Base URLs

| Entorn | Host | Base Path |
|--------|------|-----------|
| **Producción** | `sede.gobiernodecanarias.org` | `/tributos/middleware/services/sii/` |
| **Pruebas** | `sede.gobiernodecanarias.org` | `/tributos/middlewarecaut/services/sii/` |

### Endpoints Complerts

#### PRODUCCIÓN

```
https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactFEV1SOAP
https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactFRV1SOAP
https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactBIV1SOAP
https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactINMV1SOAP
https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactCOBV1SOAP
https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactCMV1SOAP
https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactPAGV1SOAP
```

#### PRUEBAS (Preproducción)

```
https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactFEV1SOAP
https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactFRV1SOAP
https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactBIV1SOAP
https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactINMV1SOAP
https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactCOBV1SOAP
https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactCMV1SOAP
https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactPAGV1SOAP
```

## Configuració al Codi

### Producció

```python
base_url = 'https://sede.gobiernodecanarias.org'
path = '/tributos/middleware/services/sii/'
port_name = 'SuministroFactEmitidas'  # Sin sufijo
```

### Proves

```python
base_url = 'https://sede.gobiernodecanarias.org'
path = '/tributos/middlewarecaut/services/sii/'  # middlewareCAUT
port_name = 'SuministroFactEmitidasPruebas'  # CON sufijo 'Pruebas'
```

## Diferències Clau

### Path

- **Producción**: `/tributos/middleware/`
- **Pruebas**: `/tributos/middlewarecaut/` (afegeix "caut")

### Port Names (dins el WSDL)

- **Producción**: `SuministroFactEmitidas`
- **Pruebas**: `SuministroFactEmitidasPruebas`

### Host

**ATENCIÓ**: Mateix host per ambdós entorns!
- NO és `www3.gobiernodecanarias.org`
- SÍ és `sede.gobiernodecanarias.org`

## Configuració Zeep

### Exemple Producció

```python
from zeep import Client

wsdl_url = "https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactFEV1SOAP?wsdl"
client = Client(wsdl_url, transport=transport)
service = client.bind('siiService', 'SuministroFactEmitidas')
```

### Exemple Proves

```python
from zeep import Client

wsdl_url = "https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactFEV1SOAP?wsdl"
client = Client(wsdl_url, transport=transport)
service = client.bind('siiService', 'SuministroFactEmitidasPruebas')
```

## Configuració amb Proxy

Si s'utilitza un proxy SSL (per exemple nginx):

### Producció

```python
proxy_url = 'https://mi-proxy.example.com'
type_address = '/tributos/middleware/services/sii/SiiFactFEV1SOAP'
full_address = proxy_url + type_address
```

### Proves

```python
proxy_url = 'https://mi-proxy.example.com'
type_address = '/tributos/middlewarecaut/services/sii/SiiFactFEV1SOAP'
full_address = proxy_url + type_address
```

## Verificació

Comprovar que els WSDLs són accessibles:

```bash
# Producció
curl -v https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactFEV1SOAP?wsdl

# Proves
curl -v https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactFEV1SOAP?wsdl
```

## Certificats

Ambdós entorns requereixen:
- **Tipus**: Certificat SELLO (certificat d'entitat)
- **Format**: PEM (certificat + clau privada)
- **Diferència**: Utilitzar certificat de proves per `middlewarecaut`

## Referències

- Documentació oficial: https://www3.gobiernodecanarias.org/tributos/atc/w/suministro-inmediato-de-informacion-del-igic-sii-1
- Portal producció: https://sede.gobiernodecanarias.org/tributos/ov/seguro/sii/inicio.jsp
- Portal proves: https://sede.gobiernodecanarias.org/tributos/ov/seguro/sii-pruebas/inicio.jsp
- WSDL_ENDPOINTS.md: Detalls complets de tots els serveis i ports
