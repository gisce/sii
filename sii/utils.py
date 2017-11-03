# -*- coding: UTF-8 -*-

from unidecode import unidecode
from stdnum import es


def unidecode_str(s):
    if isinstance(s, bytes):
        res = unidecode(s.decode('utf-8'))
    else:
        res = unidecode(s)

    return res


class VAT:
    def __init__(self, vat):
        self.vat = vat

    @staticmethod
    def clean_vat(vat):
        """
        Returns the vat without the country code in the first two characters or
        without the "PS" that indicates it is a passport
        """
        country_code = len(vat) >= 2 and vat[:2].upper()
        if country_code in COUNTRY_CODES or country_code == 'PS':
            return vat[2:]
        return vat

    @staticmethod
    def is_dni_vat(vat):
        """ Returns True if vat is DNI (Spanish VAT)"""
        country_code = len(vat) >= 2 and vat[:2]
        if country_code in COUNTRY_CODES or country_code == 'PS':
            vat = vat[2:]
        if country_code == 'ES':
            return es.dni.is_valid(vat)
        return False

    @staticmethod
    def is_enterprise_vat(vat):
        """ Returns True if vat is enterprise"""
        country_code = len(vat) >= 2 and vat[:2]
        if country_code in COUNTRY_CODES or country_code == 'PS':
            vat = vat[2:]
        if country_code == 'ES':
            return es.cif.is_valid(vat)
        return False

    @staticmethod
    def is_nie_vat(vat):
        """ Returns True if vat is NIE (foreigner's document)"""
        country_code = len(vat) >= 2 and vat[:2]
        if country_code in COUNTRY_CODES or country_code == 'PS':
            vat = vat[2:]
        if country_code == 'ES':
            return es.nie.is_valid(vat)
        return False

    @staticmethod
    def is_official_identification_document(vat):
        """ Returns True if vat is a foreign official identification document"""
        country_code = len(vat) >= 2 and vat[:2]
        if country_code != 'ES':
            return country_code in COUNTRY_CODES
        return False

    @staticmethod
    def is_passport(vat):
        """ Returns True if vat is passport"""
        if len(vat) >= 2:
            return vat[:2] == 'PS'
        return False

    @staticmethod
    def sii_get_vat_type(vat):
        partner_vat = vat
        is_nif = VAT.is_dni_vat(partner_vat)
        is_nie = VAT.is_nie_vat(partner_vat)
        is_enterprise = VAT.is_enterprise_vat(partner_vat)
        if is_nif or is_nie or is_enterprise:
            return '02'
        elif VAT.is_passport(partner_vat):
            return '03'
        elif VAT.is_official_identification_document(partner_vat):
            return '04'
        else:
            return '02'


COUNTRY_CODES = {
    'AF': 'AFGANISTÁN',
    'AL': 'ALBANIA',
    'DE': 'ALEMANIA (Incluida la Isla de Helgoland)',
    'AD': 'ANDORRA',
    'AO': 'ANGOLA (incluido Cabinda)',
    'AI': 'ANGUILA',
    'AQ': 'ANTÁRTIDA',
    'AG': 'ANTIGUA Y BARBUDA',
    'SA': 'ARABIA SAUDÍ',
    'DZ': 'ARGELIA',
    'AR': 'ARGENTINA',
    'AM': 'ARMENIA',
    'AW': 'ARUBA',
    'AU': 'AUSTRALIA',
    'AT': 'AUSTRIA',
    'AZ': 'AZERBAIYÁN',
    'BS': 'BAHAMAS',
    'BH': 'BAHRÉIN',
    'BD': 'BANGLADESH',
    'BB': 'BARBADOS',
    'BE': 'BÉLGICA',
    'BZ': 'BELICE',
    'BJ': 'BENÍN',
    'BM': 'BERMUDAS',
    'BY': 'BIELORRUSIA (BELARÚS)',
    'BO': 'BOLIVIA',
    'BA': 'BOSNIA-HERZEGOVINA',
    'BW': 'BOTSUANA',
    'BV': 'BOUVET, ISLA',
    'BR': 'BRASIL',
    'BN': 'BRUNÉI (BRUNÉI DARUSSALAM)',
    'BG': 'BULGARIA',
    'BF': 'BURKINA FASO (Alto Volta)',
    'BI': 'BURUNDI',
    'BT': 'BUTÁN',
    'CV': 'CABO VERDE, REPÚBLICA DE',
    'KY': 'CAIMÁN, ISLAS',
    'KH': 'CAMBOYA',
    'CM': 'CAMERÚN',
    'CA': 'CANADÁ',
    'CF': 'CENTROAFRICANA, REPÚBLICA',
    'CC': 'COCOS, ISLA DE (KEELING)',
    'CO': 'COLOMBIA',
    'KM': 'COMORAS (Gran Comora, Anjouan y Mohéli)',
    'CG': 'CONGO',
    'CD': 'CONGO, REPÚBLICA DEMOCRÁTICA DEL (Zaire)',
    'CK': 'COOK, ISLAS',
    'KP': 'COREA DEL NORTE (República Popular Democrática de Corea)',
    'KR': 'COREA DEL SUR (República de Corea)',
    'CI': 'COSTA DE MARFIL',
    'CR': 'COSTA RICA',
    'HR': 'CROACIA',
    'CU': 'CUBA',
    'TD': 'CHAD',
    'CZ': 'CHECA, REPÚBLICA',
    'CL': 'CHILE',
    'CN': 'CHINA',
    'CY': 'CHIPRE',
    'CW': 'CURAÇAO (antes en Antillas Neerlandesas)',
    'DK': 'DINAMARCA',
    'DM': 'DOMINICA',
    'DO': 'DOMINICANA, REPÚBLICA',
    'EC': 'ECUADOR (incluidas las Islas Galápagos)',
    'EG': 'EGIPTO',
    'AE': 'EMIRATOS ÁRABES UNIDOS (Abu Dabi, Dubai, Sharya, Ayman, Umm al-Qaiwain, Ras al-Jaima y Fuyaira)',
    'ER': 'ERITREA',
    'SK': 'ESLOVAQUIA',
    'SI': 'ESLOVENIA',
    'ES': 'ESPAÑA',
    'US': 'ESTADOS UNIDOS DE AMÉRICA',
    'EE': 'ESTONIA',
    'ET': 'ETIOPÍA',
    'FO': 'FEROE, ISLAS',
    'PH': 'FILIPINAS',
    'FI': 'FINLANDIA (Incluidas las Islas Aland)',
    'FJ': 'FIYI',
    'FR': 'FRANCIA (Incluidos los departamentos franceses de ultramar: Reunión, Guadalupe, Martinica y Guayana Francesa)',
    'GA': 'GABÓN',
    'GM': 'GAMBIA',
    'GE': 'GEORGIA',
    'GS': 'GEORGIA DEL SUR Y LAS ISLAS SANDWICH DEL SUR',
    'GH': 'GHANA',
    'GI': 'GIBRALTAR',
    'GD': 'GRANADA (incluidas las Islas Granadinas del Sur)',
    'GR': 'GRECIA',
    'GL': 'GROENLANDIA',
    'GU': 'GUAM',
    'GT': 'GUATEMALA',
    'GG': 'GUERNESEY (isla anglonormanda del Canal).',
    'GN': 'GUINEA',
    'GQ': 'GUINEA ECUATORIAL',
    'GW': 'GUINEA-BISSAU',
    'GY': 'GUYANA',
    'HT': 'HAITÍ',
    'HM': 'HEARD Y MCDONALD, ISLAS',
    'HN': 'HONDURAS (incluidas Islas del Cisne)',
    'HK': 'HONG-KONG',
    'HU': 'HUNGRÍA',
    'IN': 'INDIA',
    'ID': 'INDONESIA',
    'IR': 'IRÁN',
    'IQ': 'IRAQ',
    'IE': 'IRLANDA',
    'IM': 'ISLA DE MAN',
    'IS': 'ISLANDIA',
    'IL': 'ISRAEL',
    'IT': 'ITALIA (Incluido Livigno)',
    'JM': 'JAMAICA',
    'JP': 'JAPÓN',
    'JE': 'JERSEY (isla anglonormanda del Canal).',
    'JO': 'JORDANIA',
    'KZ': 'KAZAJSTÁN',
    'KE': 'KENIA',
    'KG': 'KIRGUISTÁN',
    'KI': 'KIRIBATI',
    'KW': 'KUWAIT',
    'LA': 'LAOS (LAO)',
    'LS': 'LESOTHO',
    'LV': 'LETONIA',
    'LB': 'LÍBANO',
    'LR': 'LIBERIA',
    'LY': 'LIBIA',
    'LI': 'LIECHTENSTEIN',
    'LT': 'LITUANIA',
    'LU': 'LUXEMBURGO',
    'XG': 'LUXEMBURGO (por lo que respecta a las rentas percibidas por las Sociedades a que se refiere el párrafo 1 del protocolo anexo al Convenio de doble imposición (3 junio 1986)',
    'MO': 'MACAO',
    'MK': 'MACEDONIA (Antigua República Yugoslava)',
    'MG': 'MADAGASCAR',
    'MY': 'MALASIA ((Malasia Peninsular y Malasia Oriental: Sarawak, Sabah y Labuán)',
    'MW': 'MALAWI',
    'MV': 'MALDIVAS',
    'ML': 'MALI',
    'MT': 'MALTA (Incluidos Gozo y Comino)',
    'FK': 'MALVINAS, ISLAS (FALKLANDS)',
    'MP': 'MARIANAS DEL NORTE, ISLAS',
    'MA': 'MARRUECOS',
    'MH': 'MARSHALL, ISLAS',
    'MU': 'MAURICIO (Isla Mauricio, Isla Rodrígues, Islas Agalega y Cargados, Carajos Shoals (Islas San Brandón))',
    'MR': 'MAURITANIA',
    'YT': 'MAYOTTE (Gran Tierra y Pamandzi)',
    'UM': 'MENORES ALEJADAS DE LOS EE.UU, ISLAS (Baker, Howland, Jarvis, Johston, Kingman Reef, Midway, Navassa, Palmira y Wake)',
    'MX': 'MÉXICO',
    'FM': 'MICRONESIA, FEDERACIÓN DE ESTADOS DE (Yap, Kosrae, Truk, Pohnpei)',
    'MD': 'MOLDAVIA',
    'MC': 'MÓNACO',
    'MN': 'MONGOLIA',
    'ME': 'MONTENEGRO',
    'MS': 'MONTSERRAT',
    'MZ': 'MOZAMBIQUE',
    'MM': 'MYANMAR (Antigua Birmania)',
    'NA': 'NAMIBIA',
    'NR': 'NAURU',
    'CX': 'NAVIDAD, ISLA',
    'NP': 'NEPAL',
    'NI': 'NICARAGUA (incluidas las Islas del Maíz)',
    'NE': 'NÍGER',
    'NG': 'NIGERIA',
    'NU': 'NIUE, ISLA',
    'NF': 'NORFOLK, ISLA',
    'NO': 'NORUEGA (Incluidos la Isla Jan Mayen y el archipiélago Svalbard)',
    'NC': 'NUEVA CALEDONIA (Incluidas las islas Lealtad: Maré, Lifou y Ouvéa)',
    'NZ': 'NUEVA ZELANDA',
    'IO': 'OCÉANO ÍNDICO, TERRITORIO BRITÁNICO DEL (Archipiélago de Chagos)',
    'OM': 'OMÁN',
    'NL': 'PAÍSES BAJOS (parte europea)',
    'BQ': 'PAÍSES BAJOS (parte caribeña: Bonaire, San Eustaquio y Saba; antes en Antillas Neerlandesas)',
    'PK': 'PAKISTÁN',
    'PW': 'PALAU',
    'PA': 'PANAMÁ (incluida la antigua Zona del Canal)',
    'PG': 'PAPÚA NUEVA GUINEA (Parte oriental de Nueva Guinea; Archipiélago Bismarck (incluidas: Nueva Bretaña, Nueva Irlanda, Lavongai y las Islas del Almirantazgo); Islas Salomón del Norte (Bougainville y Buka); Islas Trobriand, Islas Woodlark, Islas Entrecasteaux y Archipiélago de la Lousiade)',
    'PY': 'PARAGUAY',
    'PE': 'PERÚ',
    'PN': 'PITCAIRN (incluidas las Islas Henderson, Ducie y Oeno)',
    'PF': 'POLINESIA FRANCESA (Islas Marquesas, Isla de la Sociedad (incluido Tahiti, Islas Gambier, Islas Tuamotú e islas Australes incluida la Isla de Clipperton)',
    'PL': 'POLONIA',
    'PT': 'PORTUGAL (Incluidos los Archipiélagos de las Azores y de Madeira)',
    'PR': 'PUERTO RICO',
    'QA': 'QATAR',
    'GB': 'REINO UNIDO (Gran Bretaña e Irlanda del Norte)',
    'RW': 'RUANDA',
    'RO': 'RUMANÍA',
    'RU': 'RUSIA (FEDERACIÓN DE)',
    'SB': 'SALOMÓN, ISLAS',
    'SV': 'SALVADOR, EL',
    'WS': 'SAMOA (Samoa Occidental)',
    'AS': 'SAMOA AMERICANA',
    'KN': 'SAN CRISTÓBAL Y NIEVES (Saint Kitts y Nevis)',
    'SM': 'SAN MARINO',
    'SX': 'SAN MARTÍN (parte meridional; antes en Antillas Neerlandesas)',
    'PM': 'SAN PEDRO Y MIQUELÓN',
    'VC': 'SAN VICENTE Y LAS GRANADINAS',
    'SH': 'SANTA ELENA (Incluidos la Isla de la Ascensión y el Archipiélago Tristán da Cuhna)',
    'LC': 'SANTA LUCÍA',
    'ST': 'SANTO TOMÉ Y PRÍNCIPE',
    'SN': 'SENEGAL',
    'RS': 'SERBIA',
    'SC': 'SEYCHELLES (Islas Mahé, Isla Praslin, La Digue, Fragata y Silhouette, Islas Almirantes (entre ellas Desroches, Alphonse, Plate y Coëtivy); Islas Farquhar (entre ellas Providencia); Islas Aldabra e Islas Cosmoledo.)',
    'SL': 'SIERRA LEONA',
    'SG': 'SINGAPUR',
    'SY': 'SIRIA (REPÚBLICA ÁRABE)',
    'SO': 'SOMALIA',
    'LK': 'SRI LANKA',
    'SZ': 'SUAZILANDIA',
    'ZA': 'SUDÁFRICA',
    'SD': 'SUDÁN',
    'SS': 'SUDÁN DEL SUR',
    'SE': 'SUECIA',
    'CH': 'SUIZA (Incluidos el territorio alemán de Büsingen y el municipio italiano de Campione de Italia)',
    'SR': 'SURINAM',
    'TH': 'TAILANDIA',
    'TW': 'TAIWÁN',
    'TZ': 'TANZANIA (REPÚBLICA UNIDA DE) (Tanganica e islas de Zanzibar y Pemba)',
    'TJ': 'TAYIKISTÁN',
    'PS': 'TERRITORIO PALESTINO OCUPADO (Cisjordania y Franja de Gaza)',
    'TF': 'TIERRAS AUSTRALES FRANCESAS (Isla de Nueva Amsterdam, Isla San Pablo, las Islas Crozet y Kerguelén)',
    'TL': 'TIMOR LESTE',
    'TG': 'TOGO',
    'TK': 'TOKELAU, ISLAS',
    'TO': 'TONGA',
    'TT': 'TRINIDAD Y TOBAGO',
    'TN': 'TÚNEZ',
    'TC': 'TURCAS Y CAICOS, ISLAS',
    'TM': 'TURKMENISTÁN',
    'TR': 'TURQUÍA',
    'TV': 'TUVALU',
    'UA': 'UCRANIA',
    'UG': 'UGANDA',
    'UY': 'URUGUAY',
    'UZ': 'UZBEKISTÁN',
    'VU': 'VANUATU',
    'VA': 'VATICANO, CIUDAD DEL (Santa Sede)',
    'VE': 'VENEZUELA',
    'VN': 'VIETNAM',
    'VG': 'VÍRGENES BRITÁNICAS, ISLAS',
    'VI': 'VÍRGENES DE LOS EE.UU, ISLAS',
    'WF': 'WALLIS Y FUTUNA, ISLAS (incluida la Isla Alofi)',
    'YE': 'YEMEN (Yemen del Norte y Yemen del Sur)',
    'DJ': 'YIBUTI',
    'ZM': 'ZAMBIA',
    'ZW': 'ZIMBABWE'
}
