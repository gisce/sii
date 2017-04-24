# coding=utf-8

from setuptools import setup, find_packages

PACKAGES_DATA = {'sii': ['data/*.xsd']}

setup(
    name='sii',
    description='Librería de Suministro Inmediato de Información',
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    url='http://www.gisce.net',
    version='0.1.0alpha',
    license='General Public Licence 2',
    long_description='''Long description''',
    provides=['sii'],
    install_requires=['libcomxml', 'marshmallow'],
    tests_require=['expects'],
    packages=find_packages(exclude=['tests']),
    package_data=PACKAGES_DATA,
    test_suite='tests',
)
