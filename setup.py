"""pyramid_fullauth's installation file."""

import os
import re
from setuptools import setup, find_packages

here = os.path.dirname(__file__)
with open(os.path.join(here, 'pyramid_fullauth', '__init__.py')) as v_file:
    package_version = re.compile(
        r".*__version__ = '(.*?)'", re.S
    ).match(v_file.read()).group(1)


def read(fname):
    """
    Read file's content.

    :param str fname: name of file to read

    :returns: file content
    :rtype: str
    """
    return open(os.path.join(here, fname)).read()

requirements = [
    'pyramid_localize',
    'pyramid >=1.4',
    'pyramid_mako',
    'tzf.pyramid_yml >=1.0',
    'pyramid_basemodel>=0.3',
    'velruse >=1.1.1'
]

test_requires = [
    'mock',
    'pytest_pyramid',
    'pytest-cov',
    'pytest-dbfixtures[mysql,postgresql]',
]

extras_require = {
    'docs': ['sphinx'],
    'tests': test_requires
}

setup(
    name='pyramid_fullauth',
    version=package_version,
    description='''This package intends to provide full authentication / authorisation
    implementation for pyramid applications''',
    long_description=(
        read('README.rst') + '\n\n' + read('CHANGES.rst')
    ),
    keywords='python authentication authorisation pyramid',
    author='Grzegorz Sliwinski',
    author_email='fizyk@fizyk.net.pl',
    url='https://github.com/fizyk/pyramid_fullauth',
    license="MIT License",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
    install_requires=requirements,
    tests_require=test_requires,
    test_suite='tests',
    include_package_data=True,
    zip_safe=False,
    message_extractors={'pyramid_fullauth': [
        ('**.py', 'python', None),
        ('resources/templates/**.mako', 'mako', None),
        ('resources/static/**', 'ignore', None)]},
    extras_require=extras_require,
)
