#!/usr/bin/env python

import os.path
from setuptools import setup, find_packages


def load_requires_from_file(filepath):
    return [pkg_name.rstrip('\r\n') for pkg_name in open(filepath).readlines()]


def install_requires():
    return load_requires_from_file('requirements.txt')


def test_requires():
    return load_requires_from_file('test-requirements.txt')


def get_version():
    vint_root = os.path.dirname(__file__)
    version_file = open(os.path.join(vint_root, 'VERSION.txt'))
    return version_file.read().strip()


VERSION = get_version()


setup(
    name='vim-vint',
    version=VERSION,
    description='Lint tool for Vim script Language',
    author='Kuniwak',
    author_email='orga.chem.job+vint@gmail.com',
    url='https://github.com/Kuniwak/vint',
    download_url='https://github.com/Kuniwak/vint/archive/v{version}.tar.gz'.format(version=VERSION),
    install_requires=install_requires(),
    tests_require=test_requires(),
    packages=find_packages(),
    package_data={
        'vint': [
            'asset/default_config.yaml',
            'asset/void_config.yaml',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Quality Assurance',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Text Editors',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    entry_points={
        'console_scripts': [
            'vint = vint:main',
        ],
    },
)
