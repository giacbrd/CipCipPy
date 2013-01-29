#!/usr/bin/env python

from distutils.core import setup
import os

setup(name='CipCipPy',
    version='0.1',
    package_dir={'CipCipPy': 'src'},
    py_modules=['CipCipPy.config'],
    packages=['CipCipPy.'+name for name in os.listdir('src') if os.path.isdir(os.path.join('src', name))]
)