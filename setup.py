#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='vint',
      version='0.0',
      description='Lint tool for Vim script Language',
      author='Kuniwak (Orga Chem)',
      author_email='orga.chem.job+vint@gmail.com',
      url='https://github.com/Kuniwak/vint',
      install_requires=[
          'PyYAML',
      ],
      packages=find_packages())
