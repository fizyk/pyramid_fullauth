"""pyramid_fullauth's installation file."""

import os
from setuptools import setup, find_packages

here = os.path.dirname(__file__)


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
    'pyramid>=1.4',
    'pyramid_mako',
    'tzf.pyramid_yml>=1.0',
    'pyramid_basemodel>=0.3',
    'SQLAlchemy!=1.1.0,!=1.1.1',
    'velruse >=1.1.1'
]

test_requires = [
    'mock==2.0.0',
    'pytest==3.0.6',
    'pytest-pyramid==0.3.0',
    'pytest-cov==2.4.0',
    'pytest-mysql==1.1.0',
    'pytest-postgresql==1.2.0',
]

extras_require = {
    'docs': ['sphinx'],
    'tests': test_requires
}

setup(
    name='pyramid_fullauth',
    version='0.6.0',
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
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
