#!/usr/bin/env python

# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

__version__ = "0.0.1"

setup(
    name="mekanixecore",
    version=__version__,
    description="Cloudmechanik core modules",
    author="Connessione Technologies",
    author_email="connessionetechnologies@gmail.com",
    license="Apache 2.0",
    packages=find_packages(),
    classifiers=[       
        "Programming Language :: Python :: 3", 
        'Intended Audience :: Developers',
        "Operating System :: OS Independent",
        "Framework :: Tornado :: 6.0.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License"

    ], 
    python_requires='>=3.7'
    
)


