#!/usr/bin/env python
from setuptools import setup, find_packages


install_requires = [
    'PyYAML>=3.11',
    'ansicolor>=0.2.4',
    'chardet>=2.3.0',
    'setuptools>=36.2.2',  # for enhanced marker support (used below).
    'enum34>=1.0.4;python_version<"3.4"',
    'pathlib>=1.0.1;python_version<"3.4"',
    'typing>=3.6.2;python_version<"3.6"',
]

test_requires = [
    'pytest',
    'pytest-cov',
    'mock;python_version<"3.3"',
]


def read_readme():
    with open('README.rst', 'r') as f:
        return f.read()


setup(
    name='vim-vint',
    description='Lint tool for Vim script Language',
    long_description=read_readme(),
    author='Kuniwak',
    author_email='orga.chem.job+vint@gmail.com',
    url='https://github.com/Kuniwak/vint',
    download_url='https://github.com/Kuniwak/vint/releases',
    use_scm_version={
        'write_to': 'vint/__version__.py',
    },
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=install_requires,
    tests_require=test_requires,
    extras_require={
        'testing': test_requires,
    },
    packages=find_packages(exclude=['dev_tool', 'test*']),
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
    ],
    entry_points={
        'console_scripts': [
            'vint = vint:main',
        ],
    },
)
