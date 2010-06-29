"""
Cursor hack so we can handle special Django types.
"""

from django.utils.safestring import SafeString, SafeUnicode

#import sys

#from django.db import utils
#from django.db.backends import *
from django.db.backends.signals import connection_created
#from django.db.backends.postgresql.client import DatabaseClient
#from django.db.backends.postgresql.creation import DatabaseCreation
#from django.db.backends.postgresql.introspection import DatabaseIntrospection
#from django.db.backends.postgresql.operations import DatabaseOperations
#from django.db.backends.postgresql.version import get_version

class CursorWrapper(object):
    """
    A thin wrapper around MonetDB cursors that allows them to accept
    SafeUnicode and SafeString strings as params.

    This is necessary because currently there is no way to add a custom
    type to the Monetizer.mapping dictionary used by the MonetDB cursor
    to convert datatypes..
    """

    def __init__(self, cursor):
        self.cursor = cursor

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor.fetchall())

    def __handle_custom_types(self, params):
        if isinstance(params, dict):
            newparams = {}
            for k, v in params.items():
               if isinstance(v, SafeUnicode):
                   newparams[k] = unicode(v)
               elif isinstance(v, SafeString):
                   newparams[k] = str(v)
               else:
                   newparams[k] = v
            return newparams
        elif isinstance(params, tuple):
            newparams = []
            for v in params:
               if isinstance(v, SafeUnicode):
                   newparams.append(unicode(v))
               elif isinstance(v, SafeString):
                   newparams.append(str(v))
               else:
                   newparams.append(v)
            return newparams
        elif isinstance(params, SafeUnicode):
		return unicode(params)
        elif isinstance(params, SafeString):
		return str(params)
        else:
            return params

    def execute(self, sql, params=()):
	newparams = self.__handle_custom_types(params)
        return self.cursor.execute(sql, newparams)

    def executemany(self, sql, params):
	newparams = self.__handle_custom_types(params)
        return self.cursor.execute(sql, newparams)
