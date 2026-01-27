# coding=utf-8
"""
Constants específiques per al SII de l'Agència Tributària Canària (ATC)

Diferències principals amb AEAT:
- IGIC (Impuesto General Indirecto Canario) en lloc d'IVA
- Tipus impositius diferents
- Codis específics de Canàries
"""

# Tipus impositius IGIC (diferents dels d'IVA)
# Font: Anexo validaciones de Facturas Expedidas - SII IGIC v1.1
# NOTA: Els tipus permesos depenen de la data d'operació (FechaOperacion)

# Tipus actuals (després de 2019)
TIPO_IMPOSITIVO_IGIC_VALUES = [
    0.0,    # IGIC 0% (exempció, exportacions)
    3.0,    # IGIC 3% (tipus reduït - productes bàsics)
    5.0,    # IGIC 5% (tipus reduït especial)
    7.0,    # IGIC 7% (tipus reduït)
    9.5,    # IGIC 9.5% (tipus general reduït)
    15.0,   # IGIC 15% (tipus incrementat)
    20.0,   # IGIC 20% (tipus especial - tabac, etc.)
]

# Tipus històrics (FechaOperacion <= 2012)
TIPO_IMPOSITIVO_IGIC_HISTORICOS_2012 = [
    2.0,    # IGIC 2% (històric)
    2.75,   # IGIC 2.75% (històric)
    4.5,    # IGIC 4.5% (històric)
    9.0,    # IGIC 9% (històric)
    13.0,   # IGIC 13% (històric)
    35.0,   # IGIC 35% (històric)
]

# Tipus vàlids entre 2012 i 2019
TIPO_IMPOSITIVO_IGIC_2012_2019 = [
    13.5,   # IGIC 13.5% (vàlid 2012-2019)
]

# Tipus vàlid només per 2019
TIPO_IMPOSITIVO_IGIC_2019 = [
    6.5,    # IGIC 6.5% (vàlid només 2019)
]

# Mapa de tipus IGIC per validació
IGIC_TAX_MAP = {
    0.0: 'IGIC 0%',
    0.03: 'IGIC 3%',
    0.07: 'IGIC 7%',
    0.095: 'IGIC 9.5%',
    0.135: 'IGIC 13.5%',
    0.15: 'IGIC 15%',
    0.20: 'IGIC 20%',
}

# Tipus de comunicació (igual que AEAT)
TIPO_COMUNICACION_VALUES = ['A0', 'A1', 'A4']

# Tipus de factura (igual que AEAT)
TIPO_FACTURA_VALUES = [
    'F1',  # Factura
    'F2',  # Factura simplificada (ticket)
    'F3',  # Factura emesa en substitució de factures simplificades
    'F4',  # Assentament resumen de factures
    'F5',  # Importacions (DUA)
    'F6',  # Justificants comptables
    'R1',  # Factura rectificativa (error fonament art. 80.1, 80.2 i 80.6 LIVA)
    'R2',  # Factura rectificativa (art. 80.3)
    'R3',  # Factura rectificativa (art. 80.4)
    'R4',  # Factura rectificativa (resto)
    'R5',  # Factura rectificativa en factures simplificades
]

# Períodes (igual que AEAT)
PERIODO_VALUES = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '0A'
]

# Tipus de no exempció (igual que AEAT)
TIPO_NO_EXENTA_VALUES = ['S1', 'S2', 'S3']

# Tipus de rectificativa (igual que AEAT)
TIPO_RECTIFICATIVA_VALUES = ['S', 'I']

# Codis de país (igual que AEAT)
CODIGO_PAIS_VALUES = [
    'AF', 'AL', 'DE', 'AD', 'AO', 'AI', 'AQ', 'AG', 'SA', 'DZ', 'AR', 'AM',
    'AW', 'AU', 'AT', 'AZ', 'BS', 'BH', 'BD', 'BB', 'BE', 'BZ', 'BJ', 'BM',
    'BY', 'BO', 'BA', 'BW', 'BV', 'BR', 'BN', 'BG', 'BF', 'BI', 'BT', 'CV',
    'KY', 'KH', 'CM', 'CA', 'CF', 'CC', 'CO', 'KM', 'CG', 'CD', 'CK', 'KP',
    'KR', 'CI', 'CR', 'HR', 'CU', 'TD', 'CZ', 'CL', 'CN', 'CY', 'CW', 'DK',
    'DM', 'DO', 'EC', 'EG', 'AE', 'ER', 'SK', 'SI', 'ES', 'US', 'EE', 'ET',
    'FO', 'PH', 'FI', 'FJ', 'FR', 'GA', 'GM', 'GE', 'GS', 'GH', 'GI', 'GD',
    'GR', 'GL', 'GU', 'GT', 'GG', 'GN', 'GQ', 'GW', 'GY', 'HT', 'HM', 'HN',
    'HK', 'HU', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM', 'IS', 'IL', 'IT', 'JM',
    'JP', 'JE', 'JO', 'KZ', 'KE', 'KG', 'KI', 'KW', 'LA', 'LS', 'LV', 'LB',
    'LR', 'LY', 'LI', 'LT', 'LU', 'XG', 'MO', 'MK', 'MG', 'MY', 'MW', 'MV',
    'ML', 'MT', 'FK', 'MP', 'MA', 'MH', 'MU', 'MR', 'YT', 'UM', 'MX', 'FM',
    'MD', 'MC', 'MN', 'ME', 'MS', 'MZ', 'MM', 'NA', 'NR', 'CX', 'NP', 'NI',
    'NE', 'NG', 'NU', 'NF', 'NO', 'NC', 'NZ', 'IO', 'OM', 'NL', 'BQ', 'PK',
    'PW', 'PA', 'PG', 'PY', 'PE', 'PN', 'PF', 'PL', 'PT', 'PR', 'QA', 'GB',
    'RW', 'RO', 'RU', 'SB', 'SV', 'WS', 'AS', 'KN', 'SM', 'SX', 'PM', 'VC',
    'SH', 'LC', 'ST', 'SN', 'RS', 'SC', 'SL', 'SG', 'SY', 'SO', 'LK', 'SZ',
    'ZA', 'SD', 'SS', 'SE', 'CH', 'SR', 'TH', 'TW', 'TZ', 'TJ', 'PS', 'TF',
    'TL', 'TG', 'TK', 'TO', 'TT', 'TN', 'TC', 'TM', 'TR', 'TV', 'UA', 'UG',
    'UY', 'UZ', 'VU', 'VA', 'VE', 'VN', 'VG', 'VI', 'WF', 'YE', 'DJ', 'ZM',
    'ZW'
]

# Tipus d'identificació (igual que AEAT)
ID_TYPE_VALUES = {
    '02': 'NIF-IVA',
    '03': 'Pasaporte',
    '04': 'Document oficial del país de residència',
    '05': 'Certificat de residència',
    '06': 'Altre document probatori',
    '07': 'No censat',
}

# Claus de règim especial o transcendència (igual que AEAT)
CLAVE_REGIMEN_ESPECIAL_VALUES = [
    '01',  # Operació de règim general
    '02',  # Exportació
    '03',  # Operacions a les quals es pugui aplicar el règim especial
    '04',  # Règim especial criteri de caixa
    '05',  # Règim especial de les agències de viatges
    '06',  # Règim especial grup d'entitats en IVA (Nivell Avançat)
    '07',  # Règim especial del criteri de caixa
    '08',  # Operacions subjectes a IPSI / IGIC
    '09',  # Facturació dels serveis d'agències de viatges
    '10',  # Cobraments per compte de tercers
    '11',  # Operacions de lloguer de local de negoci
    '12',  # Operacions de lloguer de local de negoci subjecte a retenció
    '13',  # Operacions de lloguer de local de negoci amb inversió del subjecte passiu
    '14',  # Factura amb IGIC pendent de cobrament
    '15',  # Factura amb IGIC cobrat
]

# Valors per la Clave de Régimen Especial per factures emeses (ATC - IGIC)
CRE_FACTURAS_EMITIDAS_ATC = [
    ('01', u'Operación de régimen general'),
    ('02', u'Exportación'),
    ('03', u'Operaciones régimen especial bienes usados, arte, antigüedades, colección'),
    ('04', u'Régimen especial oro de inversión'),
    ('05', u'Régimen especial agencias de viajes'),
    ('06', u'Régimen especial grupo entidades IGIC (Nivel Avanzado)'),
    ('07', u'Régimen especial criterio de caja'),
    ('08', u'Operaciones sujetas a IPSI/IGIC'),
    ('09', u'Facturación agencias viajes como mediadoras'),
    ('10', u'Cobros por cuenta de terceros'),
    ('11', u'Operaciones arrendamiento local negocio con retención'),
    ('12', u'Operaciones arrendamiento local negocio sin retención'),
    ('13', u'Operaciones arrendamiento local negocio (con y sin retención)'),
    ('14', u'Factura con IGIC pendiente en certificaciones obra'),
    ('15', u'Factura con IGIC pendiente en operaciones tracto sucesivo'),
    ('16', u'Primer semestre 2017 y otras facturas previas al SII'),
    ('17', u'Operaciones acogidas régimen especial agricultura, ganadería y pesca'),
    ('18', u'Arrendamiento local negocio inversión sujeto pasivo'),
    ('19', u'Arrendamiento local negocio (con y sin inversión)'),
    ('20', u'Operaciones en régimen simplificado'),
]

# Valors per la Clave de Régimen Especial per factures rebudes (ATC - IGIC)
CRE_FACTURAS_RECIBIDAS_ATC = [
    ('01', u'Operación de régimen general'),
    ('02', u'Operaciones con compensación régimen especial agricultura, ganadería y pesca'),
    ('03', u'Operaciones régimen especial bienes usados, arte, antigüedades, colección'),
    ('04', u'Régimen especial oro de inversión'),
    ('05', u'Régimen especial agencias de viajes'),
    ('06', u'Régimen especial grupo entidades IGIC (Nivel Avanzado)'),
    ('07', u'Régimen especial criterio de caja'),
    ('08', u'Operaciones sujetas a IPSI/IGIC'),
    ('09', u'Adquisiciones intracomunitarias bienes y prestaciones servicios'),
    ('10', u'Cobros por cuenta de terceros'),
    ('11', u'Operaciones con inversión sujeto pasivo'),
    ('12', u'Empresa acogida régimen especial criterio caja'),
    ('13', u'Operaciones en régimen simplificado'),
    ('14', u'Primer semestre 2017 y otras facturas previas al SII'),
    ('15', u'Factura con IGIC pendiente en certificaciones obra'),
]


def get_valid_igic_rates(fecha_operacion):
    """
    Retorna els tipus impositius IGIC vàlids segons la data d'operació.
    
    Args:
        fecha_operacion: Data de l'operació (datetime.date o string 'YYYY-MM-DD')
    
    Returns:
        list: Llista de tipus impositius vàlids
        
    Validacions segons normativa SII IGIC v1.1:
    - Si FechaOperacion <= 2012: tipus històrics (2%, 2.75%, 4.5%, 9%, 13%, 35%)
    - Si 2012 < FechaOperacion < 2019: afegir 13.5%
    - Si FechaOperacion = 2019: afegir 6.5%
    - Si FechaOperacion > 2019: tipus actuals
    """
    from datetime import datetime
    
    # Convertir string a datetime si cal
    if isinstance(fecha_operacion, str):
        fecha_operacion = datetime.strptime(fecha_operacion, '%Y-%m-%d').date()
    elif isinstance(fecha_operacion, datetime):
        fecha_operacion = fecha_operacion.date()
    
    year = fecha_operacion.year
    
    # Tipus actuals sempre permesos
    valid_rates = list(TIPO_IMPOSITIVO_IGIC_VALUES)
    
    # Afegir tipus històrics segons any
    if year <= 2012:
        valid_rates.extend(TIPO_IMPOSITIVO_IGIC_HISTORICOS_2012)
    
    if 2012 < year <= 2019:
        valid_rates.extend(TIPO_IMPOSITIVO_IGIC_2012_2019)
    
    if year == 2019:
        valid_rates.extend(TIPO_IMPOSITIVO_IGIC_2019)
    
    return sorted(set(valid_rates))


def validate_igic_rate(rate, fecha_operacion):
    """
    Valida si un tipus impositiu IGIC és vàlid per una data determinada.
    
    Args:
        rate: Tipus impositiu (float)
        fecha_operacion: Data de l'operació
        
    Returns:
        bool: True si és vàlid, False altrament
    """
    valid_rates = get_valid_igic_rates(fecha_operacion)
    return float(rate) in valid_rates
