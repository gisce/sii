# -*- coding: utf-8 -*-
"""
Plugins per SII ATC

Aquest mòdul conté plugins de Zeep per funcionalitat addicional:
- DryRunPlugin: Mode dry-run per no enviar peticions reals
- PersistXmlPlugin: Persistir XMLs de petició i resposta
"""
from __future__ import absolute_import, unicode_literals

from .dry_run_plugin import DryRunPlugin
from .persist_xml_plugin import PersistXmlPlugin

__all__ = ['DryRunPlugin', 'PersistXmlPlugin']
