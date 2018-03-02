#!/usr/bin/env python

from distutils.core import setup

setup(name='djonet',
    version='0.3-django-1.6-rt05',
    description='MonetDB backend for Django',
    author='Gijs Molenaar',
    author_email='gijsmolenaar@gmail.com',
    url='https://github.com/gijzelaerr/djonet',
    packages=['djonet'],
    requires=['pymonetdb', 'django']
)
