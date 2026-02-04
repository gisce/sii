# WSDL Endpoints - ATC (Agencia Tributaria Canaria)

## Estructura WSDL

Els fitxers WSDL de l'ATC contenen **DOS ports** en el mateix servei:
- **Port de Producció**: Per enviaments reals
- **Port de Proves**: Per testing (Preproducció)

### Exemple d'estructura WSDL

```xml
<wsdl:service name="siiService">
    <!-- Entorno de PRODUCCION -->
    <wsdl:port name="SuministroFactEmitidas" binding="siiWdsl:siiBinding">
        <soap:address location="https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactFEV1SOAP"/>
    </wsdl:port>
    
    <!-- Entorno de PRUEBAS -->
    <wsdl:port name="SuministroFactEmitidasPruebas" binding="siiWdsl:siiBinding">
        <soap:address location="https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactFEV1SOAP"/>
    </wsdl:port>
</wsdl:service>
```

## URLs dels WSDL

### Facturas Emitidas

| Entorn | Port Name | URL |
|--------|-----------|-----|
| **Producción** | `SuministroFactEmitidas` | `https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactFEV1SOAP` |
| **Pruebas** | `SuministroFactEmitidasPruebas` | `https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactFEV1SOAP` |

### Facturas Recibidas

| Entorn | Port Name | URL |
|--------|-----------|-----|
| **Producción** | `SuministroFactRecibidas` | `https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactFRV1SOAP` |
| **Pruebas** | `SuministroFactRecibidasPruebas` | `https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactFRV1SOAP` |

### Bienes de Inversión

| Entorn | Port Name | URL |
|--------|-----------|-----|
| **Producción** | `SuministroBienesInversion` | `https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactBIV1SOAP` |
| **Pruebas** | `SuministroBienesInversionPruebas` | `https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactBIV1SOAP` |

### Inmuebles Adicionales

| Entorn | Port Name | URL |
|--------|-----------|-----|
| **Producción** | `SuministroInmueblesAdicionales` | `https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactINMV1SOAP` |
| **Pruebas** | `SuministroInmueblesAdicionalesPruebas` | `https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactINMV1SOAP` |

### Cobros Emitidas

| Entorn | Port Name | URL |
|--------|-----------|-----|
| **Producción** | `SuministroCobrosEmitidas` | `https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactCOBV1SOAP` |
| **Pruebas** | `SuministroCobrosEmitidasPruebas` | `https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactCOBV1SOAP` |

### Operaciones con Trascendencia Tributaria

| Entorn | Port Name | URL |
|--------|-----------|-----|
| **Producción** | `SuministroOpTrascendTribu` | `https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactCMV1SOAP` |
| **Pruebas** | `SuministroOpTrascendTribuPruebas` | `https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactCMV1SOAP` |

### Pagos Recibidas

| Entorn | Port Name | URL |
|--------|-----------|-----|
| **Producción** | `SuministroPagosRecibidas` | `https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactPAGV1SOAP` |
| **Pruebas** | `SuministroPagosRecibidasPruebas` | `https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactPAGV1SOAP` |

## Diferencias entre Entornos

| Característica | Producción | Pruebas |
|----------------|------------|---------|
| **Path** | `/tributos/middleware/` | `/tributos/middlewarecaut/` |
| **Port Suffix** | Sin sufijo | `Pruebas` |
| **Certificado** | Tipo SELLO producción | Tipo SELLO pruebas |
| **Datos** | Reales | Testing |

## Uso con Zeep

Para seleccionar el entorno correcto al crear el cliente Zeep:

```python
from zeep import Client
from zeep.transports import Transport

# Para PRODUCCIÓN
wsdl_url = "https://sede.gobiernodecanarias.org/tributos/middleware/services/sii/SiiFactFEV1SOAP?wsdl"
client = Client(wsdl_url, transport=transport)
service = client.bind('siiService', 'SuministroFactEmitidas')

# Para PRUEBAS
wsdl_url = "https://sede.gobiernodecanarias.org/tributos/middlewarecaut/services/sii/SiiFactFEV1SOAP?wsdl"
client = Client(wsdl_url, transport=transport)
service = client.bind('siiService', 'SuministroFactEmitidasPruebas')
```

## Notas Importantes

1. **Mismo WSDL, diferentes ports**: El mismo fichero WSDL contiene definiciones para ambos entornos
2. **Certificados diferentes**: Producción y pruebas requieren certificados diferentes (ambos tipo SELLO)
3. **Port naming**: Los ports de pruebas siempre terminan en `Pruebas`
4. **URL pattern**: 
   - Producción: `middleware/services/sii/`
   - Pruebas: `middlewarecaut/services/sii/`

## Referencias

- Documentación oficial: https://www3.gobiernodecanarias.org/tributos/atc/w/suministro-inmediato-de-informacion-del-igic-sii-1
- Portal de pruebas: https://sede.gobiernodecanarias.org/tributos/ov/seguro/sii-pruebas/inicio.jsp
- Portal de producción: https://sede.gobiernodecanarias.org/tributos/ov/seguro/sii/inicio.jsp
