# Copyright (c) 2012, Gijs Molenaar <gijsmolenaar@gmail.com>
# Copyright (c) 2009 - 2010, Mark Bucciarelli <mkbucc@gmail.com>
# Copyright (c) 2009 Vikram Bhandoh <vikram@bhandoh.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

from django.db.backends.base.base import *
import monetdb.sql as Database
from djonet.introspection import DatabaseIntrospection
from djonet.creation import DatabaseCreation
from djonet.operations import DatabaseOperations
from djonet.features import DatabaseFeatures
from djonet.validation import DatabaseValidation

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError


class CursorWrapper(object):
    """
    A thin wrapper around MonetDB normal cursor class so that we can tune SQL
    before execute.
    """
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, args=None):
        if not args:
            # remove escaping %%
            query = query % ()
            args = None
        return self.cursor.execute(query, args)

    def executemany(self, query, args):
        if not args:
            # remove escaping %%
            query = query % ()
            args = None
        return self.cursor.executemany(query, args)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)


class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'monetdb'
    data_types = {
        'AutoField'         : 'int AUTO_INCREMENT',
        'BooleanField'      : 'boolean',
        'CharField'         : 'varchar(%(max_length)s)',
        'CommaSeparatedIntegerField': 'varchar(%(max_length)s)',
        'DateField'         : 'date',
        'DateTimeField'     : 'timestamp',
        'DecimalField'      : 'numeric(%(max_digits)s, %(decimal_places)s)',
        'FileField'         : 'varchar(%(max_length)s)',
        'FilePathField'     : 'varchar(%(max_length)s)',
        'FloatField'        : 'float',
        'IntegerField'      : 'int',
        'IPAddressField'        : 'char(15)',
        'GenericIPAddressField': 'char(39)',
        'NullBooleanField'      : 'boolean',
        'OneToOneField'     : 'int',
        'PositiveIntegerField'  : 'int',
        'PositiveSmallIntegerField' : 'smallint',
        'SlugField'         : 'varchar(%(max_length)s)',
        'SmallIntegerField'     : 'smallint',
        'TextField'         : 'clob',
        'TimeField'         : 'time',
    }

    operators = DatabaseOperations.operators

    Database = Database

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.features = DatabaseFeatures(self)
        self.ops = DatabaseOperations(self)
        self.creation = DatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        self.validation = DatabaseValidation(self)

    def create_cursor(self):
        if not self.is_usable():
            conn_params = self.get_connection_params()
            self.connection = self.get_new_connection(conn_params)
        cursor = self.connection.cursor()
        cursor.arraysize = 1000
        return CursorWrapper(cursor)

    def get_connection_params(self):
        kwargs = {}
        if self.settings_dict['USER']:
            kwargs['username'] = self.settings_dict['USER']
        if self.settings_dict['NAME']:
            kwargs['database'] = self.settings_dict['NAME']
        if self.settings_dict['PASSWORD']:
            kwargs['password'] = self.settings_dict['PASSWORD']
        if self.settings_dict['HOST']:
            kwargs['hostname'] = self.settings_dict['HOST']
        if self.settings_dict['PORT']:
            kwargs['port'] = int(self.settings_dict['PORT'])
        return kwargs

    def get_new_connection(self, conn_params):
        conn = Database.connect(**conn_params)
        return conn

    def init_connection_state(self):
        pass

    def _set_autocommit(self, autocommit):
        self.connection.set_autocommit(autocommit)

    def ensure_connection(self):
        """
        Guarantees that a connection to the database is established.
        """
        if self.connection is None:
            super(DatabaseWrapper, self).ensure_connection()
        elif not self.is_usable():
            self.close()
            self.connect()

    def is_usable(self):
        if not self.connection:
            return False
        try:
            self.connection.execute('SELECT 1;')
        except Exception:
            return False
        else:
            return True

