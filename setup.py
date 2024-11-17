#!/usr/bin/env python

# -*- coding: utf-8 -*-
import os.path

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages




setup(
    name="mekanixe-core",
    version="0.0.1",
    description="Cloudmechanik core modules",
    author="Connessione Technologies",
    author_email="connessionetechnologies@gmail.com",
    license="Apache 2.0",
    packages=["mekanixe.core"],
    classifiers=[       
        "Programming Language :: Python :: 3", 
        'Intended Audience :: Developers',
        "License :: OSI Approved :: Apache 2.0 License", 
        "Operating System :: OS Independent",
    ], 
    python_requires='>=3.7'
    
)


