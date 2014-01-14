About
=====

Djonet is a MonetDB backend for Django. It is not complete, but works for us.

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
            'NAME': 'test',
            'USER': 'test',
            'PASSWORD': 'test',
            'HOST': 'localhost',
            'PORT': 5000,
        }
    }


If you want to issue management commands, like creating (test) databases you
need to add something like this to your *settings.py* also::

    MONETDB_HOST = 'localhost'
    MONETDB_PORT = 50000
    MONETDB_PASSPHRASE = 'test'


About
=====

* http://www.monetdb.org/
* http://www.django.org/

