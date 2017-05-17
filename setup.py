# coding=utf-8

from setuptools import setup, find_packages
from sii import __LIBRARY_VERSION__

INSTALL_REQUIRES = [line for line in open('requirements.txt')]

TESTS_REQUIRE = [line for line in open('requirements-dev.txt')]

PACKAGES_DATA = {'sii': ['data/*.xsd']}

setup(
    name='sii',
    description='Librería de Suministro Inmediato de Información',
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    url='http://www.gisce.net',
    version=__LIBRARY_VERSION__,
    license='General Public Licence 2',
    long_description=open('README.md').read(),
    provides=['sii'],
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    packages=find_packages(exclude=['spec']),
    package_data=PACKAGES_DATA
)
