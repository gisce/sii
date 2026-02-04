# SII CANARIAS – ANEXO (VERSIÓN MARKDOWN ESTRUCTURADA)

> Documento LLM-friendly.
> Contenido original del Anexo SII Canarias.
> Las tablas se representan en Markdown estándar.

---

# ANEXO – ESPECIFICACIONES TÉCNICAS DEL CONTENIDO DE LOS LIBROS REGISTRO DE IGIC

> Copia íntegra del PDF original convertida a Markdown, sin traducción ni reinterpretación.

---


## Página 1

ANEXO  
ESPECIFICACIONES TÉCNICAS DEL CONTENIDO DE LOS LIBROS REGISTRO DE IGIC LLEVADOS A TRAVÉS DE LA SEDE 
ELECTRÓNICA DE LA AGENCIA TRIBUTARIA CANARIA  
 
Leyenda  Rojo=  Campo obligatorio    
  Negro=  Campo opcional    
    Campo de Selección    
 Fondo amarillo  = Modificaciones con efectos 1 de octubre  2025   
 
I. CAMPOS DE REGISTRO Y ESPECIFICACIONES FUNCIONALES DE LOS MENSAJES DE ALTA Y MODIFICACION.  
La información a suministrar  se remitirá asociada a alguno de los tipos de libros registro que se citan a continuación o, en su caso, si se califica como una 
operación con trascendencia tributaria.  
1. Libro de registro de Facturas expedidas  
2. Libro de registro de Facturas Recibidas  
3. Libro de registro de Bienes de Inversión  
4. Suministro de otras Operaciones de trascendencia tributaria con carácter anual.  
4.1. Operaciones en metálico (Importes superiores a 6.000 euros que se hubieran percibido en metálico durante el ejercicio de una misma persona 
o entidad)  
4.2. Agencias de viajes. (Prestaciones de servicios en cuya realización intervienen actuando como mediadoras en nombre y por cuent a ajena a las 
que se refiere el apartado 7.b) de la disposición adicional cuarta del Real Decreto 1619/2012, de 30 de noviembre)  
A continuación, se incluye una descripción de cada uno de los campos de registro integrados en los mensajes informáticos en q ue se concreta el contenido de 
los libros registro del Impuesto General Indirecto Canario llevados a través de la Sede electrónica de la Agencia Tributaria Canaria para operaciones de alta y 
modificación. En el caso de operaciones de baja de facturas, la petición se realizará mediante un mensaje informático específ ico para bajas, que contendrá una


## Página 2

cabecera común y la relación de todas las facturas que se quieran dar de baja en un mismo envío, con la identificación de cad a factura y del ejercicio y periodo 
de la baja de cada factura:  
 
1. Libro de registro de Facturas expedidas  
 
BLOQ
UE DATOS/  
AGRUPA
CIÓN  DATOS/  
AGRUPA
CIÓN  DATOS/  
AGRUPA
CIÓN  DATOS/  
AGRUPA
CIÓN  DAT
OS/ 
AGR
UPAC
IÓN DATOS/  
AGRUP
ACIÓN  DATOS    DESCRIPCIÓN  FORMATO  
LONGITUD  
LISTA  
Cabecer
a IDVersion
Sii     
    Identificación de la 
versión del esquema 
utilizado para el 
intercambio de 
información  Alfanumérico(3)  
L19 
Titular  NombreRa
zon 
    
    Nombre -razón social 
del Titular del libro de 
registro de facturas 
expedidas  Alfanumérico( 1
20) 
NIFRepres
entante     
    NIF del representante 
del titular del libro de 
registro  FormatoNIF(9)  
NIF        NIF asociado al titular 
del libro de registro  FormatoNIF(9)


## Página 3

TipoComu
nicacion      
    Tipo de operación 
(alta, modificación)  Alfanumérico(2)  
L0 
Registro
LRfactu
rasEmiti
das PeriodoLi
quidacion  Ejercicio         Ejercicio  Numérico(4)  
Periodo     
    
Periodo Liquidación  Alfanumérico(2)  
L1 
IDFactura  IDEmisorF
actura  NIF       NIF asociado al 
emisor de la factura.  FormatoNIF(9)  
NumSerieF
acturaEmis
or    
    Nº Serie+Nº Factura  
que identifica a la 
factura emitida  (en su 
caso primera factura 
del asiento resumen)  Alfanumérico(6
0) 
NumSerieF
acturaEmis
orResumen
Fin    
    Nº Serie+Nº Factura  
que identifica a la 
última factura cuando 
el Tipo de Factura es 
un asiento resumen de 
facturas  Alfanumérico(6
0) 
FechaExpe
dicionFact
uraEmisor         Fecha de expedición 
de la factura  Fecha(dd -mm-
yyyy)  
FacturaEx
pedida  TipoFactur
a        Especificación del tipo 
de factura: factura 
completa, factura 
simplificada, factura 
emitida en sustitución 
de facturas 
simplificadas, asiento Alfanumérico(2)  
L2_EMI


## Página 4

resumen o factura 
rectificativa.  
TipoRectifi
cativa         Campo que identifica 
si el tipo de factura 
rectificativa es por 
sustitución o por 
diferencia  Alfanumérico(1)  
L5 
FacturasAg
rupadas  IDFacturaA
grupada  NumSerieF
acturaEmis
or      Nº Serie+Nº Factura 
que identifica a la 
factura emitida  Alfanumérico(6
0) 
  FechaExpe
dicionFactu
raEmisor       Fecha de expedición 
de la factura  Fecha(dd -mm-
yyyy)  
FacturasRe
ctificadas  IDFacturaR
ectificada  NumSerieF
acturaEmis
or      Nº Serie+Nº Factura 
que identifica a la 
factura emitida  Alfanumérico(6
0) 
FechaExpe
dicionFactu
raEmisor       Fecha de expedición 
de la factura  Fecha(dd -mm-
yyyy)  
ImporteRe
ctificacion  Base 
Rectificada        Base imponible de la 
factura/facturas 
sustituidas  Decimal(12,2)  
Cuota 
Rectificada        Cuota repercutida o 
soportada de la 
factura/facturas 
sustituidas  Decimal(12,2)  
 FechaOper
acion        Fecha en la que se ha 
realizado la operación 
siempre que sea Fecha(dd -mm-
yyyy)


## Página 5

diferente a la fecha de 
expedición  
 ClaveRegi
menEspeci
alOTrascen
dencia         Clave que identificará 
el tipo de régimen del 
IGIC  o una operación 
con trascendencia 
tributaria  Alfanumérico(2)  
L3.1 
 ClaveRegi
menEspeci
alOTrascen
denciaAdic
ional1         Clave adicional que 
identificará el tipo de 
régimen del IGIC o 
una operación con 
trascendencia 
tributaria  Alfanumérico(2)  
L3.1 
 ClaveRegi
menEspeci
alOTrascen
denciaAdic
ional2         Clave adicional que 
identificará el tipo de 
operación o el régimen 
especial con 
trascendencia 
tributaria  Alfanumérico(2)  
L3.1 
 
NumRegist
roAutoriza
cionFactur
acion         Número de registro 
general obtenido al 
enviar por la sede 
electrónica de la ATC 
la autorización en 
materia de facturación 
o de libros de registro  Alfanumérico(1
2) 
 
 ImporteTot
al        Importe total de la 
factura  Decimal(12,2)  
 BaseImpon
ibleACoste         Para grupos de IGIC  Decimal(12,2)


## Página 6

Descripcio
nOperación         Descripción del objeto 
de la factura  Alfanumérico(5
00) 
 RefExterna         Referencia Externa. 
Dato adicional de 
contenido libre 
enviado por algunas 
aplicaciones clientes 
(asiento contable, etc).  Alfanumérico(6
0) 
 FacturaSim
plificadaAr
ticulos7.2_
7.3        Factura simplificada 
Articulo 7,2 Y 7,3 RD 
1619/2012.  
Si no se informa este 
campo se entenderá 
que tiene valor “N  Alfanumérico(1)  
L26 
 EntidadSuc
edida  NombreRa
zon 
       Nombre -razón social 
de la entidad sucedida 
como consecuencia de 
una operación de 
reestructuración  Alfanumérico(1
20) 
 
 NIF       NIF asociado a la 
entidad sucedida como 
consecuencia de una 
operación de 
reestructuración  FormatoNIF(9)


## Página 7

RegPrevio
GGEEoRE
DEME         Identificador que 
especifica aquellos 
registros de 
facturación con 
dificultades para 
enviarse en plazo por 
no tener constancia  del 
cambio de condición a 
GGEE o  de la 
inclusión en 
REDEME  
Si no se informa este 
campo se entenderá 
que tiene valor “N”.  Alfanumérico(1)  
L28 
 
Macrodato         Identificador que 
especifica aquellas 
facturas con importe 
de la factura superior a 
un umbral de 
100.000.000 euros.  
 
Si no se informa este 
campo se entenderá 
que tiene valor “N”.  Alfanumérico(1)  
L29 
 
DatosInmu
eble DetalleInm
ueble  SituaciónIn
mueble       Identificador que 
especifica la situación 
del inmueble  Numérico(1)  
L6 
 Referencia
Catastral       Referencia catastral 
del inmueble  Alfanumérico(2
5)


## Página 8

DatosArtic
ulo25  DetalleArti
culo25  PagoAntici
padoArt25       Identificador que 
especifica que se trata 
de un pago anticipado  Alfanumérico(1)  
L31 
 TipoBienA
rt25      Tipo de bien de 
inversión exento por 
artículo 25 L19/94  Alfanumérico(2)  
L32 
 IDDocume
ntoArt25  TipoD
ocum
Art25      Tipo de documento en 
que conste la 
operación exenta por 
artículo 25 L 19/94  Alfanumérico(2)  
L33 
 
Numer
oProto
colo     Número de protocolo 
de la escritura notarial 
en que conste la 
operación exenta por 
artículo 25 L19/94  Alfanumérico(6)  
 Apelli
dosNo
mbre  
Notari
o     Apellidos y nombre 
del notario que 
protocoliza la 
operación exenta por 
artículo 25 L19/94  Alfanumérico(1
20) 
 ImporteTra
nsmisionIn
mueblesSuj
etoAIGIC         Importe percibido por 
transmisiones de 
inmuebles sujetas a 
IGIC  Decimal(12,2)  
 EmitidaPor
TercerosO       Identificador que 
especifica si la factura 
ha sido emitida por un Alfanumérico(1)  
L10


## Página 9

Destinatari
o tercero o por el 
destinatario.  
Si no se informa este 
campo se entenderá 
que tiene valor “N”.  
 Facturacio
nDispAdici
onalTercer
aYsexta yD
el Mercado 
Organizado
DelGas         Identificador que 
especifica si la factura 
ha sido emitida por un 
tercero de acuerdo a 
una exigencia 
normativa (disposición 
adicional tercera y 
sexta Reglamento por 
el que se regulan las 
obligaciones de 
facturación y del 
Mercado Organizado 
del Gas).  
Si no se informa este 
campo se entenderá 
que tiene valor “N”.  Alfanumérico(1)  
L25 
 VariosDest
inatarios         Identificador que 
especifica si la factura 
tiene varios 
destinatarios.  Alfanumérico(1)  
L20


## Página 10

Si no se informa este 
campo se entenderá 
que tiene valor “N”.  
 Cupon         Identificador que 
especifica si la factura 
tipo R1, R5 o F4 tiene 
minoración de la base 
imponible por la 
concesión de cupones, 
bonificaciones o 
descuentos cuando 
solo se expide el 
original de la factura.  
Si no se informa este 
campo se entenderá 
que tiene valor “N”.  Alfanumérico(1)  
L22 
 FacturaSinI
dentifDesti
natarioArit
culo6.1.d         Factura sin 
identificación 
destinatario artículo 
6.1.d) RD 1619/2012  
Si no se informa este 
campo se entenderá 
que tiene valor “N”.  Alfanumérico(1)  
L27 
 Contrapart
e NombreRa
zon       Nombre -razón social 
de la contraparte de la 
operación (cliente) de 
facturas expedidas  Alfanumérico(1
20)


## Página 11

NIFRepres
entante        NIF del representante 
de la contraparte de la 
operación  FormatoNIF(9)  
 
NIF       Identificador del NIF 
contraparte de la 
operación (cliente) de 
facturas expedidas  FormatoNIF(9)  
 
 
IDOtro  CodigoPais       Código del país 
asociado contraparte 
de la operación 
(cliente) de facturas 
expedidas  Alfanumérico(2) 
(ISO 3166 -1 
alpha -2 codes)  
L17 
 
IDType       Clave para establecer 
el tipo de 
identificación en el 
país de residencia  Alfanumérico(2)  
L4 
 
ID      Número de 
identificación en el 
país de residencia  Alfanumérico(2
0) 
 
TipoDesgl
ose DesgloseFa
ctura  Sujeta  Exenta  DetalleEx
enta CausaEx
encion    Campo que especifica 
la causa de la exención  Alfanumérico(2)  
L9 
 BaseImp
onible    Importe en euros 
correspondiente a la 
causa de exención  Decimal(12,2)  
 NoExe
nta TipoNoE
xenta     Tipo de operación 
sujeta y no exenta para 
la diferenciación de Alfanumérico(2)  
L7


## Página 12

inversión de sujeto 
pasivo  
 
DesgloseI
GIC DetalleI
GIC TipoImpositi
vo  Porcentaje aplicado 
sobre la Base 
Imponible para 
calcular la cuota.  Decimal(3,2)  
 BaseImponi
ble  Magnitud dineraria 
sobre la cual se aplica 
un determinado tipo 
impositivo  Decimal(12,2)  
 
CuotaReperc
utida   Cuota resultante de 
aplicar a la base 
imponible un 
determinado tipo 
impositivo  Decimal(12,2)  
 
NoSujeta  Import
ePorA
rticulo
s9_Otr
os     Importe en euros si la 
sujeción es por el art. 9 
Ley 20/1991 y otros  Decimal(12,2)  
 Import
eTAIR
eglasL
ocaliza
cion     Importe en euros si la 
sujeción es por 
operaciones no sujetas 
en el TAI por reglas de 
localización  Decimal(12,2)  
 PrestacionS
ervicios  Sujeta  Exenta  DetalleE
xenta  CausaExenci
on  Campo que especifica 
la causa de la exención  Alfanumérico(2)  
L9


## Página 13

Desglose Ti
poOperacio
n BaseImponi
ble  Importe en euros 
correspondiente a la 
causa de exención  Decimal(12,2)  
 
NoExenta  TipoNo
Exenta    Tipo de operación 
sujeta y no exenta para 
la diferenciación de 
inversión de sujeto 
pasivo  Alfanumérico(2)  
L7 
 
Desglos
eIGIC  DetalleIGIC  TipoImpositi
vo Porcentaje aplicado 
sobre la Base 
Imponible para 
calcular la cuota.  Decimal(3,2)  
 BaseImponibl
e Magnitud dineraria 
sobre la cual se aplica 
un determinado tipo 
impositivo  Decimal(12,2)  
 
CuotaReperc
utida  Cuota resultante de 
aplicar a la base 
imponible un 
determinado tipo 
impositivo  Decimal(12,2)  
 
NoSuj
eta ImporteP
orArticulo
s9_Otros     Importe en euros si la 
sujeción es por el art. 9 
Ley 20/1991 y otros  Decimal(12,2)  
 ImporteT
AIReglas
Localizaci
on    Importe en euros si la 
sujeción es por 
operaciones no sujetas 
en el TAI por reglas de 
localización  Decimal(12,2)


## Página 14

Entrega  Sujeta  Exenta   
DetalleE
xenta  CausaExenci
on  Campo que especifica 
la causa de la exención  Alfanumérico(2)  
L9 
 BaseImponi
ble  Importe en euros 
correspondiente a la 
causa de exención  Decimal(12,2)  
 
NoExenta  TipoNo
Exenta    Tipo de operación 
sujeta y no exenta para 
la diferenciación de 
inversión de sujeto 
pasivo  Alfanumérico(2)  
L7 
 
 
Desglos
eIGIC  DetalleIGIC  TipoImpositi
vo Porcentaje aplicado 
sobre la Base 
Imponible para 
calcular la cuota.  Decimal(3,2)  
 
 BaseImponibl
e Magnitud dineraria 
sobre la cual se aplica 
un determinado tipo 
impositivo  Decimal(12,2)  
 
 CuotaReperc
utida  Cuota resultante de 
aplicar a la base 
imponible un 
determinado tipo 
impositivo  Decimal(12,2)  
 
 NoSuj
eta ImporteP
orArticulo
s9_Otros     Importe en euros si la 
sujeción es por el art. 9 
Ley 20/1991 y otros  Decimal(12,2)


## Página 15

ImporteT
AIReglas
Localizaci
on    Importe en euros si la 
sujeción es por 
operaciones no sujetas 
en el TAI por reglas de 
localización  Decimal(12,2)  
  Operación 
sujeta 
AIEM  Cuota 
AIEM        Cuota resultante de 
aplicar a la base 
imponible un 
determinado tipo 
impositivo  Decimal(12,2)  
   Clave del 
Impuesto 
especial  Clave del 
impuesto 
especial (1, 
2 y 3)       Campo que especifica 
el impuesto especial  Alfanumérico(1) 
L36 
 
 Operación 
sujeta 
II.EE 
gestionado 
por la CAC  Exenta  (S/N)       Identificador que 
especifica si la 
operación está exenta.  
Si no se informa este 
campo se entenderá 
que tiene valor “N”.  Alfanumérico(1)  
L.37 
  
Régimen 
suspensivo  (S/N)       Identificador que 
especifica si la 
operación está acogida 
a un régimen 
suspensivo.  
Si no se informa este 
campo se entenderá 
que tiene valor “N”.  Alfanumérico(1)  
L.38 
  Cuota II.EE 
CAC        Cuota resultante de 
aplicar a la base Decimal(12,2)


## Página 16

imponible un 
determinado tipo 
impositivo  
 
 
En el caso de que los sujetos pasivos acogidos al régimen especial del criterio de caja debieran incluir en el libro registro  de facturas 
expedidas información sobre los cobros, se deberá informar atendiendo a los siguientes campos de registro:  
 
BLOQUE  DATOS/  
AGRUPACIÓN  DATOS/  
AGRUPACIÓN  DATOS/  
AGRUP
ACIÓN  DATOS/  
AGRUPACI
ÓN DESCRIPCIÓN  FORMATO  
LONGITUD  
LISTA  
Cabecera  IDVersionSii     Identificación de la versión del esquema 
utilizado para el intercambio de 
información  Alfanumérico(3)  
L19 
Titular  NombreRazon  
   Nombre -razón social del Titular del libro de 
registro de facturas expedidas  Alfanumérico(120)  
NIFRepresentante    NIF del representante del titular del libro de 
registro  FormatoNIF(9)  
NIF   NIF asociado al titular del libro de registro  FormatoNIF(9)  
IDFactura  IDEmisorFactura  NIF  Identificador del NIF del emisor de la 
factura  FormatoNIF(9)


## Página 17

RegistroLRCo
bros NumSerieFacturaEmisor    Nº Serie+Nº  Factura que identifica a la 
factura emitida (en su caso primera factura 
del asiento resumen)  Alfanumérico(60)  
FechaExpedicionFacturaEmis
or   Fecha de expedición de la factura  Fecha(dd -mm-
yyyy)  
Cobros  Cobro  Fecha   Fecha de realización del cobro  Fecha(dd -mm-
yyyy)  
Importe   Importe cobrado  Decimal(12,2)  
Medio   Medio de cobro utilizado  Alfanumérico(2)  
 L11 
Cuenta_O
_Medio   Cuenta bancaria o medio de cobro utilizado  Alfanumérico(34)


## Página 18

En el caso de que los sujetos pasivos informen de más de quince números de referencias catastrales dentro de un mismo registr o de 
facturación (arrendamientos de locales de negocio), el suministro de estas referencias se realizará atendiendo a los siguient es campos de 
registro:  
 
BLOQUE  DATOS/  
AGRUPACIÓN  DATOS/  
AGRUPACIÓN  DATOS/  
AGRUP
ACIÓN  DATOS/  
AGRUPACI
ÓN DESCRIPCIÓN  FORMATO  
LONGITUD  
LISTA  
Cabecera  IDVersionSii     Identificación de la versión del esquema 
utilizado para el intercambio de 
información  Alfanumérico(3)  
L19 
Titular  NombreRazon  
   Nombre -razón social del Titular del libro de 
registro de facturas expedidas  Alfanumérico(120)  
NIFRepresentante    NIF del representante del titular del libro de 
registro  FormatoNIF(9)  
NIF   NIF asociado al titular del libro de registro  FormatoNIF(9)  
RegistroLRIn
mueblesAdicio
nales  IDFactura  IDEmisorFactura  NIF  Identificador del NIF del emisor de la 
factura  FormatoNIF(9)  
 
NumSerieFacturaEmisor    Nº Serie+Nº  Factura que identifica a la 
factura emitida (en su caso primera factura 
del asiento resumen)  Alfanumérico(60)  
FechaExpedicionFacturaEmis
or   Fecha de expedición de la factura  Fecha(dd -mm-
yyyy)  
DatosInmueble  DetalleInmueble  SituaciónI
nmueble   Identificador que especifica la situación del 
inmueble  Numérico(1)  
L6


## Página 19

Referenci
aCatastral   Referencia catastral del inmueble  Alfanumérico(25)  
 
 
2. Libro de registro de Facturas Recibidas  
 
BLOQU
E DATOS/  
AGRUPACIÓ
N DATOS/  
AGRUPACIÓN  DATOS/  
AGRUP
ACIÓN  DATOS/  
AGRUPAC
IÓN DATO
S/ 
AGRU
PACI
ÓN DATOS  DESCRIPCIÓN  FORMATO  
LONGITUD  
LISTA  
Cabecera  IDVersionSii      
 Identificación de la 
versión del esquema 
utilizado para el 
intercambio de 
información  Alfanumérico(3)  
L19 
Titular  NombreRazon  
    
 Nombre -razón social del 
Titular del libro de registro 
de facturas recibidas  Alfanumérico(120)  
NIFRepresentante      NIF del representante del 
titular del libro de registro  FormatoNIF(9)  
NIF     NIF asociado al titular del 
libro de registro  FormatoNIF(9)


## Página 20

TipoComunicaci
on     
 Tipo de operación (alta, 
modificación)  Alfanumérico(2)  
L0 
RegistroL
Rfacturas
Recibidas  PeriodoLiquidac
ion Ejercicio      Ejercicio  Numérico(4)  
Periodo     
 Periodo Liquidación  Alfanumérico(2)  
L1 
IDFactura  IDEmisorFactura  NIF    Identificador del NIF del 
emisor de la factura  FormatoNIF(9)  
 
IDOtro  CodigoPais    Código del país asociado 
al emisor de la factura  Alfanumérico( 2) (ISO 3166 -
1 alpha -2 codes)  
L17 
IDType    Clave para establecer el 
tipo de identificación en el 
país de residencia  Alfanumérico(2)  
L4 
ID   Número de identificación 
en el país de residencia  Alfanumérico(20)  
NumSerieFactura
Emisor     
 Nº Serie+Nº  Factura que 
identifica a la factura 
emitida (en su caso 
primera factura del asiento 
resumen)  Alfanumérico(60)  
NumSerieFactura
EmisorResumenF
in    
 Nº Serie+Nº Factura que 
identifica a la última  
factura cuando el Tipo de 
Factura es un asiento 
resumen de facturas  Alfanumérico(60)


## Página 21

FechaExpedicion
FacturaEmisor      Fecha de expedición de la 
factura  Fecha(dd -mm-yyyy)  
FacturaRecibida  TipoFactura      Especificación del tipo de 
factura: factura completa, 
factura simplificada, 
asiento resumen, 
importación y demás 
documentos justificativos 
del derecho a la 
deducción. La 
especificación de factura 
emitida en sustitución de 
facturas simplificadas o de 
factura rectificativa tienen 
carácter opci onal.  Alfanumérico(2)  
L2_RECI  
TipoRectificativa      Campo que identifica si el 
tipo de factura rectificativa 
es por sustitución o por 
diferencia  Alfanumérico(1)  
L5 
FacturasAgrupada
s IDFactura
Agrupada  NumSerieFa
cturaEmisor    Nº Serie+Nº Factura que 
identifica a la factura 
emitida   Alfanumérico(60)  
FechaExped
icionFactura
Emisor    Fecha de expedición de la 
factura  Fecha(dd -mm-yyyy)  
FacturasRectifica
das IDFactura
Rectificad
a NumSerieFa
cturaEmisor    Nº Serie+Nº Factura que 
identifica a la factura 
emitida  Alfanumérico(60)  
FechaExped
icionFactura
Emisor    Fecha de expedición de la 
factura  Fecha(dd -mm-yyyy)


## Página 22

ImporteRectificac
ion Base 
Rectificad
a    Base imponible de la 
factura/facturas 
sustituidas  Decimal(12,2)  
Cuota 
Rectificad
a    Cuota repercutida o 
soportada de la 
factura/facturas 
sustituidas  Decimal(12,2)  
CargaImp
ositivaIm
plicitaRec
tificada     Carga impositiva implícita 
rectificada  Decimal(12,2)  
FechaOperación      Fecha en la que se ha 
realizado la operación 
siempre que sea diferente 
a la fecha de expedición.  Fecha(dd -mm-yyyy)  
ClaveRegimenEs
pecialOTrascende
ncia     Clave que identificará el 
tipo de régimen del IGIC o 
una operación con 
trascendencia tributaria  Alfanumérico(2)  
L3.2 
ClaveRegimenEs
pecialOTrascende
nciaAdicional1      Clave adicional que 
identificará el tipo de 
régimen del IGIC o una 
operación con 
trascendencia tributaria  Alfanumérico(2)  
L3.2 
ClaveRegimenEs
pecialOTrascende
nciaAdicional2      Clave adicional que 
identificará el tipo de 
régimen del IGIC o una 
operación con 
trascendencia tributaria  Alfanumérico(2)  
L3.2


## Página 23

NumRegistroAuto
rizacionFacturaci
on     Número de registro 
general obtenido al enviar 
por la sede electrónica de 
la ATC la autorización en 
materia de facturación o 
de libros de registro  Alfanumérico(12)  
 
ImporteTotal      Importe total de la factura  Decimal(12,2)  
BaseImponibleA
Coste      Para grupos de IGIC  Decimal(12,2)  
DescripcionOpera
cion     Descripción del objeto de 
la factura  Alfanumérico(500)  
RefExterna      Referencia Externa. Dato 
adicional de contenido 
libre enviado por algunas 
aplicaciones clientes 
(asiento contable, etc .). Alfanumérico(60)  
FacturaSimplifica
daArticulos7.2_7.
3     Factura simplificada 
Articulo 7,2 Y 7,3 RD 
1619/2012.  
Si no se informa este 
campo se entenderá que 
tiene valor “N  Alfanumérico(1)  
L26 
EntidadSucedida  NombreR
azon 
    Nombre -razón social de la 
entidad sucedida como 
consecuencia de una 
operación de 
reestructuración  Alfanumérico(120)


## Página 24

NIF    NIF asociado a la entidad 
sucedida como 
consecuencia de una 
operación de 
reestructuración  FormatoNIF(9)  
RegPrevioGGEEo
REDEME      Identificador que 
especifica aquellos 
registros de facturación 
con dificultades para 
enviarse en plazo por no 
tener constancia del 
cambio de condición a 
GGEE o de la inclusión en 
REDEME  
Si no se informa este 
campo se entenderá que 
tiene valor “N”.  Alfanumérico(1)  
L28 
Macrodato      Identificador que 
especifica aquellas 
facturas con importe de la 
factura superior a un 
umbral de 100.000.000 
euros.  
 
Si no se informa este 
campo se entenderá que 
tiene valor “N”.  Alfanumérico(1)  
L29


## Página 25

DatosArticulo25  DetalleAr
ticulo25  PagoAnticip
adoArt25    Identificador que 
especifica que se trata de 
un pago anticipado  Alfanumérico(1)  
L31 
TipoBienArt
25   Tipo de bien de inversión 
exento por artículo 25 
L19/94  Alfanumérico(2)  
L32 
IDDocumen
toArt25  TipoDo
cumArt
25  Tipo de documento en que 
conste la operación exenta 
por artículo 25 L19/94  Alfanumérico(2)  
L33 
Numer
oProtoc
olo  Número de protocolo de la 
escritura notarial en que 
conste la operación exenta 
por artículo 25 L19/94  Alfanumérico(6)  
Apellid
osNom
breNot
ario  Apellidos y nombre del 
notario que protocoliza la 
operación exenta por 
artículo 25 L19/94  Alfanumérico(120)  
DesgloseFactura  Inversion
SujetoPas
ivo DetalleIGIC  TipoIm
positiv
o  Porcentaje aplicado sobre 
la Base Imponible para 
calcular la cuota  Decimal(3,2)  
BaseIm
ponible   Magnitud dineraria sobre 
la cual se aplica un 
determinado tipo 
impositivo  Decimal(12,2)  
CuotaS
oportad
a  Cuota resultante de aplicar 
a la base imponible un Decimal(12,2)


## Página 26

determinado tipo 
impositivo  
  BienIn
version   Identificador que 
especifica bien de 
inversión.  
Si no se informa este 
campo se entenderá que 
tiene valor “N”.  Alfanumérico(1)  
L34  
 
Desglose I
GIC DetalleIGIC  TipoIm
positiv
o  Porcentaje aplicado sobre 
la Base Imponible para 
calcular la cuota.  Decimal(3,2)  
BaseIm
ponible   Magnitud dineraria sobre 
la cual se aplica un 
determinado tipo 
impositivo  Decimal(12,2)  
CuotaS
oportad
a  Cuota resultante de aplicar 
a la base imponible un 
determinado tipo 
impositivo  Decimal(12,2)  
CargaI
mpositi
vaImpli
cita  Carga impositiva implícita  Decimal(12,2)  
CuotaR
ecargo
Minoris
ta  Cuota recargo minorista  Decimal(12,2)  
Porcent
Compe Porcentaje compensación 
Régimen Especial de la Decimal(3,2)


## Página 27

nsacion
REAG
YP Agricultura, Ganadería y 
Pesca.  
Importe
Compe
nsacion
REAG
YP  Compensación Régimen 
Especial de la Agricultura, 
Ganadería y Pesca.  Decimal(12,2)  
   BienIn
version   Identificador que 
especifica bien de 
inversión.  
Si no se informa este 
campo se entenderá que 
tiene valor “N”.  Alfanumérico(1)  
L34 
Contraparte  NombreR
azon    Nombre -razón social de la 
contraparte de la 
operación. Proveedor en 
facturas recibidas  Alfanumérico(120)  
NIFRepre
sentante     NIF del representante de la 
contraparte de la 
operación. Proveedor en 
facturas recibidas  FormatoNIF(9)  
 
NIF 
    Identificador del NIF de la 
contraparte de la 
operación. Proveedor en 
facturas recibidas  FormatoNIF(9)  
 
IDOtro  CodigoPais    Código del país asociado 
de la contraparte de la Alfanumérico(2) (ISO 3166 -
1 alpha -2 codes)  
L17


## Página 28

operación. Proveedor en 
facturas recibidas  
IDType    Clave para establecer el 
tipo de identificación en el 
país de residencia  Alfanumérico(2)  
L4 
ID   Número de identificación 
en el país de residencia  Alfanumérico(20)  
FechaRegContabl
e     Fecha del registro 
contable de la operación. 
Se utilizará para el plazo 
de remisión de las facturas 
recibidas  Fecha(dd -mm-yyyy)  
CuotaDeducible      Cuota deducible  Decimal(12,2)  
  
DeducirEnPeriod
oPosterior      Identificador que 
especifica si la factura se 
deduce en un periodo 
posterior  
Si no se informa este 
campo se entenderá que 
tiene valor “N”.  Alfanumérico(1)  
L35 
EjercicioDeduccci
on     Ejercicio de deducción  Numérico(4)  
PeriodoDeduccio
n     Periodo de deducción  Alfanumérico(2)  
L1 
Operación sujeta 
AIEM  Cuota  
AIEM     Cuota resultante de aplicar 
a la base imponible un Decimal(12,2)


## Página 29

determinado tipo 
impositivo  
Operación sujeta 
II.EE gestionado 
por la CAC  Clave del 
Impuesto 
especial  Clave del 
impuesto 
especial  (1, 
2 y 3)    Campo que especifica el 
impuesto especial  Alfanumérico(1)  
L36 
 
Exenta  (S/N)    Identificador que 
especifica si la operación 
está exenta.  
Si no se informa este 
campo se entenderá que 
tiene valor “N”.  Alfanumérico(1)  
L.37 
Régimen 
suspensiv
o (S/N)    Identificador que 
especifica si la operación 
está acogida a un régimen 
suspensivo.  
Si no se informa este 
campo se entenderá que 
tiene valor “N”.  Alfanumérico(1)  
L.38 
Cuota 
IIEE 
CAC     Cuota resultante de aplicar 
a la base imponible un 
determinado tipo 
impositivo  Decimal(12,2)  
 
En el caso de que los sujetos pasivos acogidos al régimen especial del criterio de caja o los sujetos pasivos no acogidos a e ste régimen que sean 
destinatarios de las operaciones afectadas por el mismo debieran incluir en el libro registro de facturas reci bidas información sobre los 
pagos, se deberá informar atendiendo a los siguientes campos de registro:


## Página 30

BLOQUE  DATOS/  
AGRUPACIÓN  DATOS/  
AGRUPACIÓN  DATOS/  
AGRUP
ACIÓN  DATOS/  
AGRUPACI
ÓN DESCRIPCIÓN  FORMATO  
LONGITUD  
LISTA  
Cabecera  IDVersionSii     Identificación de la versión del esquema 
utilizado para el intercambio de 
información  Alfanumérico(3)  
L19 
Titular  NombreRazon  
   Nombre -razón social del Titular del libro de 
registro de facturas recibidas  Alfanumérico(120)  
NIFRepresentante    NIF del representante del titular del libro de 
registro  FormatoNIF(9)  
NIF   NIF asociado al titular del libro de registro  FormatoNIF(9)  
RegistroLRPa
gos IDFactura  IDEmisorFactura  NombreR
azon  Nombre -razón social del emisor de la 
factura  Alfanumérico(120)  
NIF  Identificador del NIF del emisor de la 
factura  FormatoNIF(9)  
 
IDOtro  CodigoPais  Código del país asociado a la contraparte de 
la factura  Alfanumérico(2) 
(ISO 3166 -1 alpha -
2 codes)  
L17 
IDType  Clave para establecer el tipo de 
identificación en el país de residencia  Alfanumérico(2)  
L4 
ID Número de identificación en el país de 
residencia  Alfanumérico(20)


## Página 31

NumSerieFacturaEmisor    Nº Serie+Nº  Factura que identifica a la 
factura emitida (en su caso primera factura 
del asiento resumen)  Alfanumérico(60)  
FechaExpedicionFacturaEmis
or   Fecha de expedición de la factura  Fecha(dd -mm-
yyyy)  
Pagos  Pago  Fecha   Fecha de realización del pago  Fecha(dd -mm-
yyyy)  
Importe   Importe pagado  Decimal(12,2)  
Medio   Medio de pago utilizado  Alfanumérico(2)  
 L11 
Cuenta_O
_Medio   Cuenta bancaria o medio de pago utilizado  Alfanumérico(34)


## Página 32

3. Libro de registro de Bienes de Inversión  
 
BLOQUE  DATOS/  
AGRUPACIÓN  DATOS/  
AGRUPACIÓN  DATOS/  
AGRUP
ACIÓN  DATOS/  
AGRUPACI
ÓN DESCRIPCIÓN  FORMATO  
LONGITUD  
LISTA  
Cabecera  IDVersionSii     Identificación de la versión del esquema 
utilizado para el intercambio de 
información  Alfanumérico(3)  
L19 
Titular  NombreRazon  
   Nombre -razón social del Titular del libro de 
registro de bienes de inversión  Alfanumérico( 120) 
NIFRepresentante    NIF del representante del titular del libro de 
registro  FormatoNIF(9)  
NIF   NIF asociado al titular del libro de registro  FormatoNIF(9)  
TipoComunicacio
n    
Tipo de operación (alta, modificación)  Alfanumérico(2)  
L0 
RegistroLRBie
nesInversion  PeriodoLiquidaci
on Ejercicio    Ejercicio del Libro registro de  los bienes de 
inversión  Numérico(4)  
 Periodo    
0A Debe informarse  
con valor “0A”  
 IDFactura  IDEmisorFactura  NombreR
azon 
  Nombre -razón social del emisor de la 
factura asociada a los bienes de inversión  Alfanumérico(120)


## Página 33

NIF  Identificador del NIF del emisor de la 
factura  FormatoNIF(9)  
 
 
IDOtro  CodigoPais  Código del país asociado al emisor de la 
factura  Alfanumérico(2) 
(ISO 3166 -1 alpha -
2 codes)  
L17 
 IDType  Clave para establecer el tipo de 
identificación en el paí s de residencia  Alfanumérico(2)  
L4 
 ID Número de identificación en el país de 
residencia  Alfanumérico(20)  
 NumSerieFacturaEmisor    Nº Serie+Nº  Factura que identifica a la 
factura emitida  Alfanumérico(60)  
 FechaExpedicionFacturaEmis
or   Fecha de expedición de la factura  Fecha(dd -mm-
yyyy)  
 
BienesInversion  IdentificacionBien    Descripción de los bienes objeto de la 
operación  Alfanumérico(40)  
 FechaInicioUtilizacion    Fecha de inicio de utilización del mismo  Fecha(dd -mm-
yyyy)  
 ProrrataAnualDefinitiva    Prorrata anual definitiva  Decimal(3,2)  
 RegularizacionAnualDeduccio
n   Importe de la r egularización anual de las 
deducciones cuando proceda  Decimal(12,2)  
 IdentificacionEntrega    Referencia al asiento del libro registro de 
facturas expedidas que recoja la entrega del 
bien de inversión  Alfanumérico(40)  
 RegularizacionDeduccionEfec
tuada    Importe de la regularización de la 
deducción efectuada con motivo de la 
entrega del bien de inversión  Decimal(12,2)


## Página 34

RefExterna    Referencia Externa. Dato adicional de 
contenido libre enviado por algunas 
aplicaciones clientes (asiento contable, etc .) Alfanumérico(60)  
 NumRegistroAutorizacionFact
uracion    Número de registro general obtenido al 
enviar por la sede electrónica de la ATC la 
autorización en materia de facturación o de 
libros de registro  Alfanumérico(12 ) 
 
 EntidadSucedida  NombreR
azon 
  Nombre -razón social de la entidad 
sucedida como consecuencia de una 
operación de reestructuración  Alfanumérico(120)  
 
 NIF  NIF asociado a la entidad sucedida como 
consecuencia de una operación de 
reestructuración  FormatoNIF(9)


## Página 35

4. Suministro  de Operaciones de trascendencia tributaria  con carácter anual  
 
4.1. Operaciones en metálico (Importes superiores a 6.000 euros que se hubieran percibido en metálico durante el ejercicio de una misma persona 
o entidad)  
 
BLOQUE  DATOS/  
AGRUPACIÓN  DATOS/  
AGRUPACIÓN  DATO
S/ 
AGRU
PACI
ÓN DESCRIPCIÓN  FORMATO  
LONGITUD  
LISTA  
Cabecera  IDVersionSii    Identificación de la versión del esquema utilizado 
para el intercambio de información  Alfanumérico(3)  
L19 
Titular  NombreRazon  
  Nombre -razón socia l del t itular  Alfanumérico( 120) 
NIFRepresentante   NIF del representante del titular  FormatoNIF(9)  
NIF  NIF asociado al titular  FormatoNIF(9)  
TipoComunicacio
n   Tipo de operación (alta, modificación)  Alfanumérico(2)  
L0 
RegistroLRCo
brosMetalico  PeriodoLiquidaci
on Ejercicio   Ejercicio  Numérico(4)  
Periodo   0A Debe informarse 
con valor “0A”


## Página 36

Contraparte  NombreRazon   Nombre -razón social de la contraparte de la 
operación  Alfanumérico(120)  
NIFRepresentante   NIF del representante de la contraparte de la 
operación  FormatoNIF(9)  
NIF 
  NIF asociado a la contraparte de la operación  FormatoNIF(9)  
IDOtro  Codigo
Pais Código del país asociado a la contraparte  Alfanumérico(2) 
(ISO 3166 -1 alpha -
2 codes)  
L17 
IDTyp
e Clave para establecer el tipo de identificación en el 
país de residencia  Alfanumérico(2)  
L4 
ID Número de identificación en el país de residencia  Alfanumérico(20)  
ImporteTotal     
Importes superiores a 6.000 euros que se hubieran 
percibido en metálico de la misma persona o entidad 
por las operaciones realizadas durante el año natural.  
 Decimal(12,2)  
EntidadSucedida  NombreRazon  
  Nombre -razón social de la entidad sucedida como 
consecuencia de una operación de reestructuración  Alfanumérico(120)  
 
NIF 
 NIF asociado a la entidad su  
cedida como consecuencia de una operación de 
reestructuración  FormatoNIF(9)


## Página 37

4.2. Agencias de viajes. (Prestaciones de servicios en cuya realización intervienen actuando como mediadoras en nombre y por cuenta ajena a las 
que se refiere el apartado 7.b) de la disposición adicional cuarta del Real Decreto 1619/2012, de 30 de noviembre)  
 
BLOQUE  DATOS/  
AGRUPACIÓN  DATOS/  
AGRUPACIÓN  DATO
S/ 
AGRU
PACI
ÓN DESCRIPCIÓN  FORMATO  
LONGITUD  
LISTA  
Cabecera  IDVersionSii    Identificación de la versión del esquema utilizado para 
el intercambio de información  Alfanumérico(3)  
L19 
Titular  NombreRazon  
  Nombre -razón social del t itular  Alfanumérico(120)  
NIFRepresentante   NIF del representante del titular  FormatoNIF(9)  
NIF  NIF asociado al titular  FormatoNIF(9)  
TipoComunicacio
n   Tipo de operación (alta, modificación)  Alfanumérico(2)  
L0 
RegistroLRAg
enciasViajes  PeriodoLiquidaci
on Ejercicio   Ejercicio  Numérico(4)


## Página 38

Periodo   0A Debe informarse 
con valor “0A”   
  NombreRazon   Nombre -razón social de la contraparte de la operación  Alfanumérico(120)  
 Contraparte  NIFRepresentante   NIF del representante de la contraparte de la operación  FormatoNIF(9)  
  NIF 
  NIF asociado a la contraparte de la operación  FormatoNIF(9)  
  
IDOtro  Codigo
Pais Código del país asociado a la contraparte  Alfanumérico(2) 
(ISO 3166 -1 alpha -
2 codes)  
L17 
  IDTyp
e Clave para establecer el tipo de identificación en el 
país de residencia  Alfanumérico(2)  
L4 
  ID Número de identificación en el país de residencia  Alfanumérico(20)  
 ImporteTotal     
Importe anual  
 Decimal(12,2)  
 
EntidadSucedida  NombreRazon  
  Nombre -razón social de la entidad sucedida como 
consecuencia de una operación de reestructuración  Alfanumérico(120)  
 
 NIF 
 NIF asociado a la entidad su  
cedida como consecuencia de una operación de 
reestructuración  FormatoNIF(9)


## Página 39

II. CLAVES Y VALORES PERMITIDOS EN CAMPOS DE TIPO LISTA:  
 
L0 → Tipo de Comunicación  
VALORES  DESCRIPCIÓN  
A0 Alta de facturas/registro  
A1 Modificación de facturas/registros (errores registrales)  
A4 Modificación Factura Régimen de Viajeros  
A5 Alta de las devoluciones del IGIC de viajeros (DER)  
A6 Modificación de las devoluciones del IGIC de viajeros 
(DER)  
 
L1 → Periodo  de liquidación  
VALORES  DESCRIPCIÓN  
01 Enero    
02 Febrero  
03 Marzo  
04 Abril  
05 Mayo  
06 Junio  
07 Julio  
08 Agosto  
09 Septiembre  
10 Octubre


## Página 40

11 Noviembre  
12 Diciembre  
0A Anual  
1T 1º Trimestre  
2T 2º Trimestre  
3T 3º Trimestre  
4T 4º Trimestre  
 
Nota: Los libros de r egistro de facturas expedidas y  recibidas tendrán un periodo mensual /trimestral . El libro registro de bienes de inversión tendrá  periodicidad 
anual.  La información correspondiente a operaciones con trascendencia tributaria de suministro anual que formen parte de los libros registros de facturas 
expedidas y recibidas también tendrá por defecto como periodo el año.  
 
L2_EMI → Tipo de Factura Emitidas  
VALORES  DESCRIPCIÓN  
F1 Factura (art. 6, 7.2 y 7.3 del RD 1619/2012)  
F2 Factura Simplificada y y  Facturas sin identificación del 
destinatario art. 6.1.d) RD 1619/2012  
F3 Factura emitida en sustitución de facturas simplificadas 
facturadas y declaradas  con anterioridad  
F4 Asiento resumen de facturas  
R1 Factura Rectificativa ( Error fundado en derecho y Art. 
22 apartados 4, 5 y 11 L20/91 ) 
R2 Factura Rectificativa ( Art 22.6 L20/91 – concurso ) 
R3 Factura Rectificativa ( Art 22.7 L20/91 - deuda 
incobrable ) 
R4 Factura Rectificativa (Resto)  
R5 Factura Rectificativa en facturas simplificadas


## Página 41

AJ Ajuste margen bruto Régimen Especial de Agencias de 
viaje y Régimen Especial de Bienes Usados  
 
 
L2_RECI  → Tipo de Factura  Recibidas  
VALORES  DESCRIPCIÓN  
F1 Factura (art. 6, 7.2 y 7.3 del RD 1619/2012)  
F2 Factura Simplificada y y Facturas sin identificación del 
destinatario art. 6.1.d) RD 1619/2012  
F3 Factura emitida en sustitución de facturas simplificadas 
facturadas y declaradas  con anterioridad  
F4 Asiento resumen de facturas  
F5 Importaciones (DUA)  
F6 Justificantes contables  
R1 Factura Rectificativa (Error fundado en derecho y Art. 
22 apartados 4, 5 y 11 L20/91)  
R2 Factura Rectificativa (Art 22.6 L20/91 – concurso)  
R3 Factura Rectificativa (Art 22.7 L20/91 - deuda 
incobrable)  
R4 Factura Rectificativa (Resto)  
R5 Factura Rectificativa en facturas simplificadas  
LC Importaciones  - Liquidación complementaria  
24 Cuota s deducibles por exclusión  del R.E. comerciante 
minorista ( modelo  424) 
25 Documento de ingreso articulo 25 Ley 19/1994  
 
Las claves F3, R1, R2, R3, R4 y R5 tienen carácter opcional en el Libro registro de facturas recibidas.


## Página 42

L3.1 → Clave de régimen especial o trascendencia  en facturas expedidas  
VALORES  DESCRIPCIÓN  
01 Operación de régimen general.  
02 Exportación.  
03 Operaciones a las que se aplique los regímenes especiales de bienes usados y de 
objetos de arte, antigüedades y objetos de colección.  
04 Régimen especial del oro de inversión.  
05 Régimen especial de las agencias de viajes.  
06 Régimen especial grupo de entidade s en IGIC  (Nivel Avanzado)  
07 Régimen especial del criterio de caja.  
08 Operaciones sujetas al IVA (Impuesto sobre el Valor Añadido).  
09 Facturación de las prestaciones de servicios de agencias de viaje que actúan 
como mediadoras en nombre y por cuenta ajena (D.A.4ª RD1619/2012)  
10 Cobros por cuenta de terceros de honorarios profesionales o de derechos 
derivados de la propiedad industrial, de autor u otros por cuenta de sus socios, 
asociados o colegiados efectuados por sociedades, asociaciones, colegios 
profesionales u otras entidades que realicen estas funciones de cobro.  
11 Operaciones de arrendamiento de loca l de negocio  
14 Factura con IGIC  pendiente de devengo en certificaciones de obra cuyo 
destinatario sea una Administración Pública.  
15 Factu ra con IGIC  pendiente de devengo en operaciones de tracto sucesivo.


## Página 43

16 Facturas anteriores a la inclusión en el SII  
17 Régimen especial de comerciante minorista  
18 Régimen especial del pequeño empresario o profesional  
19 Operaciones interiores exentas por aplicación artículo 25 Ley 19/1994  
20 Operaciones sujetas al IPSI (Impuesto sobre la Producción, los Servicios y la 
Importación).  
 
L3.2 → Clave de régimen especial o trascendencia en facturas recibidas  
VALORES  DESCRIPCIÓN  
01 Operación de régimen general.  
02 Operaciones por las que los empresarios satisfacen compensaciones en las 
adquisiciones a personas acogidas al Régimen especial de la agricultura, 
ganadería  y pesca.  
03 Operaciones a las que se aplique los regímenes especiales de bienes usados y 
de objetos de arte, antigüedades y objetos de colección . 
04 Régimen especial del oro de inversión.  
05 Régimen especial de las agencias de viajes.  
06 Régimen especial grupo de entidades en IGIC  (Nivel Avanzado).  
07 Régimen especial del criterio de caja. 
08 Operaciones sujetas al IVA (Impuesto sobre el Valor Añadido).  
12 Operaciones de arrendamiento de local de negocio.  
13 Factura correspondiente a una importación (informada sin asociar a un DUA).  
14 Facturas anteriores a la inclusión en el SII 
15 Régimen especial de comerciante minorista  
16 Régimen especial del pequeño empresario o profesional  
17 Operaciones interiores exentas por aplicación artículo 25 Ley 19/1994


## Página 44

18 Operaciones sujetas al IPSI (Impuesto sobre la Producción, los Servicios y la 
Importación).  
 
 
 
 
 
 
 
 
L4 → Tipos de Identificación en el país de residencia  
VALORES  DESCRIPCIÓN  
03 PASAPORTE  
04 DOCUMENTO OFICIAL DE ID ENTIFICACIÓN EXPEDIDO POR EL PAÍ S O 
TERRITORIO DE RESIDENCIA  
05 CERTIFICADO DE RESIDENCIA  
06 OTRO DOCUMENTO PROBATORIO  
07 NO CENSADO  
 
La clave 07, “No censado”, puede utilizarse como tipo de identificación en el Libro registro de facturas expedidas y en las Operaciones de trascendencia tributaria 
con carácter anual  
 
L5 → Tipo de Factura Rectificativa  
VALORES  DESCRIPCIÓN  
S Por sustitución  
I Por diferencias


## Página 45

L6 → Situación del Inmueble  
VALORES  DESCRIPCIÓN  
1 Inmueble con referencia catastral situado en las Islas Canarias  
2 Inmueble sin referencia catastral situado en las Islas Canarias  
3 Inmueble con referencia catastral situado en el resto del territorio español  
4 Inmueble sin referencia catastral situado en el resto del territorio español  
5 Inmueble situado en el extranjero  
 
 
 
L7 → Calificación del tipo de operación  Sujeta/ No Exenta  
VALORES  DESCRIPCIÓN  
S1 No exenta - Sin inversión  sujeto pasivo  
S2 No exenta - Con inversión  sujeto p asivo  
S3 No exenta - Sin inversión  sujeto pasivo y con inversión  sujeto p asivo  
 
 
L9 → Causa de exención de operaciones sujetas y exentas  
VALORES  DESCRIPCIÓN  
E1 Exenta por el Art. 50 Ley 4/2012  
E2 Exenta por el Art. 11 Ley 20/1991  
E3 Exenta por el Art. 12 Ley 20/1991  
E4 Exenta por Art. 13 Ley 20/1991  
E5 Exenta por el Art. 25 Ley 19/1994  
E6 Exenta por el Art. 47 Ley 19/1994


## Página 46

E7 Exenta por el Art. 110 Ley 4/2012  
E8 Exenta Otros  
 
  
L10 → Emitidas por Terceros  
VALORES  DESCRIPCIÓN  
S Sí 
N No 
 
 
 
 
L11→ Medio de Pago/Cobro  
VALORES  DESCRIPCIÓN  
01 Transferencia  
02 Cheque  
03 No se cobra / paga (fecha límite de devengo / devengo forzoso en concurso de 
acreedores)  
04 Otros medios de cobro / pago  
05 Domiciliación bancaria  
 
 
L17→ Código de País .  
Se informará según la relación de códigos de países y territorios que se incluye en el Anexo II de la Orden EHA/3496/2011, de 15 de diciembre (BOE del 26 -
12-2011).


## Página 47

L19 -> IDVersionSii  
VALORES  DESCRIPCIÓN  
1.1 Versión Actual del esquema  utilizado para el intercambio de información  
 
L20 → Varios destinatarios  
VALORES  DESCRIPCIÓN  
S Si 
N No 
 
L22 → Factura R1, R5 o F4 con minoración de la base imponible por la concesión de cupones, bonificaciones o descuentos cuando solo se expide el original de 
la factura  
VALORES  DESCRIPCIÓN  
S Sí 
N No 
 
 
L25 → Emitida por terceros de acuerdo con una exigencia normativa  
 
VALORES  DESCRIPCIÓN  
S Sí 
N No 
 
L26 → Factura simplificada Articulo 7,2 Y 7,3 RD 1619/2012.


## Página 48

VALORES  DESCRIPCIÓN  
S Si 
N No 
 
L27 → Factura sin identificación destinatario artículo 6,1,d) RD 1619/2012  
VALORES  DESCRIPCIÓN  
S Sí 
N No 
 
 
 
L28 → Identificador que especifica aquellos registros de facturación con dificultades para enviarse en plazo por no tener constanci a del cambio de condición a 
GGEE o  de la inclusión en REDEME  
VALORES  DESCRIPCIÓN  
S Si 
N No 
 
L29 → Facturas con importe de la factura superior a un umbral  de 100.000.000 € 
VALORES  DESCRIPCIÓN  
S Sí 
N No 
 
L31 → Pago anticipado operación exenta artículo 25 Ley 19/1994  
VALORES  DESCRIPCIÓN


## Página 49

S Si 
N No 
 
 
L32 → Tipo bien operación exenta artículo 25 Ley 19/1994  
VALORES  DESCRIPCIÓN  
01 Adquisición, entrega o ejecución de obras que tengan por objeto de bienes 
inmuebles  
02 Adquisición, entrega o ejecución de obras qu e tengan por objeto de bienes 
muebles  
03 Adquisición o cesión de elementos del inmovilizado intangible consistente en el 
derecho de uso de propiedad industrial o intelectual  
04 Adquisición o cesión del inmovilizado intangible consistente en el derecho de uso 
de conocimientos no patentados  
05 Adquisición o cesión del inmovilizado intangible consistente en concesiones 
administrativas  
 
L33 → Tipo de documento artículo 25 Ley 19/1994  
VALORES  DESCRIPCIÓN  
01 Notarial  
02 Privado  
03 Otros  
 
L34 → Identificador q ue especifica bien de inversión  
VALORES  DESCRIPCIÓN


## Página 50

S Sí 
N No 
 
L35 → Identificador que especifica si la factura se deduce en un periodo posterior  
VALORES  DESCRIPCIÓN  
S Si 
N No 
 
L36 → Identificador que especifica el impuesto especial gestionado por la CAC  
VALORES  CLAVE DEL IMPUESTO ESPECIAL  GESTIONADO POR LA CAC  
01 Impuesto sobre las labores de tabaco  
02 Impuesto especial sobre combustibles derivados del petróleo  
03 Impuesto sobre el depósito de residuos en vertederos, la incineración y la 
coincineración de residuos  
 
L37 → Identificador que especifica si la operación se encuentra exenta del Impuesto especial gestionado por  la CAC   
VALORES  DESCRIPCIÓN  
S Sí 
N No 
 
L38 → Identificador que especifica si la operación se encuentra acogido a un régimen suspensivo del Impuesto especial gestionado por la CAC  
VALORES  DESCRIPCIÓN  
S Si 
N No


## Página 51




---

## NOTAS DE CONVERSIÓN
- Documento optimizado para lectura por LLMs (Claude, GPT, etc.)
- Encabezados jerárquicos
- Separación clara por bloques funcionales
- Texto **no modificado**
