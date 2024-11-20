#!/usr/bin/env python

# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

__version__ = "0.0.1"

setup(
    name="cdscore",
    version=__version__,
    description="Cloudisense core modules",
    author="Connessione Technologies",
    author_email="connessionetechnologies@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    packages=find_packages(),
    classifiers=[       
        "Programming Language :: Python :: 3.8", 
        'Intended Audience :: Developers',
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 2 - Pre-Alpha"
    ], 
    python_requires='>=3.7'
    
)
