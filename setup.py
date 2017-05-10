# coding=utf-8

from setuptools import setup, find_packages
from sii import __LIBRARY_VERSION__

INSTALL_REQUIRES = ['marshmallow']

TESTS_REQUIRE = ['mamba', 'expects']

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
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    packages=find_packages(exclude=['tests']),
    package_data=PACKAGES_DATA,
    test_suite='tests',
)
