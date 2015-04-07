#!/usr/bin/env python

from setuptools import setup, find_packages
import os

setup(name='CipCipPy',
    description='Twitter IR system for the TREC Microblog track',
    author='Giacomo Berardi <giacomo.berardi@isti.cnr.it>, Andrea Esuli <andrea.esuli@isti.cnr.it>, Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>',
    version='0.2',
    license='GNU GENERAL PUBLIC LICENSE Version 3',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=['CipCipPy.config'],
    #packages=['CipCipPy.'+name for name in os.listdir('src') if os.path.isdir(os.path.join('src', name))],
    requires=['numpy', 'whoosh', 'sklearn', 'nltk']
)