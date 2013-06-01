# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

here = os.path.dirname(__file__)
with open(os.path.join(here, 'pyramid_fullauth', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)


def read(fname):
    return open(os.path.join(here, fname)).read()

requirements = ['pyramid >=1.4',
                'tzf.pyramid_yml >= 0.2',
                'pyramid_basemodel <=0.1.5, !=0.1.4',
                # since all other versions contains requirements for inflect, which isn't python3 compatible
                'velruse'
                ]

test_requires = [
    'WebTest',
    'nose',
    'coverage',
    'mock',
    'lxml'
]

extras_require = {
    'docs': ['sphinx', 'sphinx_bootstrap_theme'],
    'tests': test_requires
}

setup(
    name='pyramid_fullauth',
    version=package_version,
    description='''This package intends to provide full authentication / authorisation
    implementation for pyramid applications''',
    long_description=(
        read('README.rst')
        + '\n\n' +
        read('CHANGES.rst')
    ),
    keywords='python authentication authorisation pyramid',
    author='Grzegorz Sliwinski',
    author_email='username: fizyk, domain: fizyk.net.pl',
    url='https://github.com/fizyk/pyramid_fullauth',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
    install_requires=requirements,
    tests_require=test_requires,
    test_suite='tests',
    include_package_data=True,
    zip_safe=False,
    extras_require=extras_require,
)
