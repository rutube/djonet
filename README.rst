Djonet is a MonetDB backend for Django.

Installation
============

run from the source folder::

 $ python setup.py install

or make sure the Djonet source directory is in your *PYTHONPATH*.

Djonet is also installable with pip::

 $ pip install djonet


Usage
=====

put something like this in your Django *settings.py*::

 DATABASES = {
     'default': {
         'ENGINE': 'djonet',
         'NAME': 'database_name',
         'USER': 'database_user',
         'PASSWORD': 'database_password',
         'HOST': 'database_host',
         'PORT': '5000',
     }
 }

About
=====
 * http://www.monetdb.org/

