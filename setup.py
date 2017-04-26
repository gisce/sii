# coding=utf-8

from setuptools import setup, find_packages
from sii import __LIBRARY_VERSION__

PACKAGES_DATA = {'sii': ['data/*.xsd']}

setup(
    name='sii',
    description='Librería de Suministro Inmediato de Información',
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    url='http://www.gisce.net',
    version=__LIBRARY_VERSION__,
    license='General Public Licence 2',
    long_description='''Long description''',
    provides=['sii'],
    install_requires=['libcomxml', 'marshmallow'],
    tests_require=['expects'],
    packages=find_packages(exclude=['tests']),
    package_data=PACKAGES_DATA,
    test_suite='tests',
)
