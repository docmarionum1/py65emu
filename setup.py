#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='py65emu',
    version='2.0.0',
    description='A 6502 Emulator',
    long_description=readme + '\n\n' + history,
    author='Jeremy Neiman',
    author_email='docmarionum1@gmail.com',
    url='https://github.com/docmarionum1/py65emu',
    packages=[
        'py65emu',
    ],
    package_dir={'py65emu': 'py65emu'},
    include_package_data=True,
    install_requires=[
    ],
    python_requires='>=3.2',
    license="WTFPL",
    zip_safe=False,
    keywords='py65emu',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: WTFPL',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    test_suite='tests',
)
