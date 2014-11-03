#!/usr/bin/env python

from setuptools import setup, find_packages
from vint import VERSION


def load_requires_from_file(filepath):
    return [pkg_name.rstrip('\r\n') for pkg_name in open(filepath).readlines()]


def install_requires():
    return load_requires_from_file('requirements.txt')


def test_requires():
    return load_requires_from_file('test-requirements.txt')


def get_version():
    return VERSION


setup(
    name='vint',
    version=get_version(),
    description='Lint tool for Vim script Language',
    author='Kuniwak',
    author_email='orga.chem.job+vint@gmail.com',
    url='https://github.com/Kuniwak/vint',
    download_url='https://github.com/Kuniwak/vint/releases',
    install_requires=install_requires(),
    tests_require=test_requires(),
    packages=find_packages(),
    classfiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Quality Assurance',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Text Editors',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': [
            'vint = vint:main',
        ],
    },
)
