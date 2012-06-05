Djonet is a MonetDB backend for Django.

Installation
============

run::

 $ python setup.py install

or make sure the Djonet source directory is in your *PYTHONPATH*.


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

