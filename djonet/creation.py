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


import sys

from django.db.backends.creation import BaseDatabaseCreation
from django.conf import settings
from django.utils.functional import cached_property
import pymonetdb.control
import pymonetdb

auth_query = """
ALTER USER "monetdb" RENAME TO "%(username)s";
ALTER USER SET PASSWORD '%(password)s' USING OLD PASSWORD 'monetdb';
CREATE SCHEMA "%(database)s" AUTHORIZATION "%(username)s";
ALTER USER "%(username)s" SET SCHEMA "%(database)s";
"""


class DatabaseCreation(BaseDatabaseCreation):
    data_types = {
        'AutoField': 'int AUTO_INCREMENT',
        'BooleanField': 'boolean',
        'CharField': 'varchar(%(max_length)s)',
        'CommaSeparatedIntegerField': 'varchar(%(max_length)s)',
        'DateField': 'date',
        'DateTimeField': 'timestamp',
        'DecimalField': 'numeric(%(max_digits)s, %(decimal_places)s)',
        'FileField': 'varchar(%(max_length)s)',
        'FilePathField': 'varchar(%(max_length)s)',
        'FloatField': 'float',
        'IntegerField': 'int',
        'BigIntegerField': 'bigint',
        'IPAddressField': 'char(15)',
        'GenericIPAddressField': 'char(39)',
        'NullBooleanField': 'boolean',
        'OneToOneField': 'int',
        'PositiveIntegerField': 'int',
        'PositiveSmallIntegerField': 'smallint',
        'SlugField': 'varchar(%(max_length)s)',
        'SmallIntegerField': 'smallint',
        'TextField': 'clob',
        'TimeField': 'time',
    }

    def __init__(self, *args, **kwargs):
        super(DatabaseCreation, self).__init__(*args, **kwargs)
        self.monetdb_hostname = getattr(settings, 'MONETDB_HOSTNAME',
                                        'localhost')
        self.monetdb_port = getattr(settings, 'MONETDB_PORT', 50000)
        self.monetdb_passphrase = getattr(settings, 'MONETDB_PASSPHRASE',
                                          'testdb')
        self.test_database_name = self._get_test_db_name()
        self.test_database_user = self.connection.settings_dict['USER']
        self.test_database_password = self.connection.settings_dict['PASSWORD']
        self.test_database_host = self.connection.settings_dict['HOST']
        self.test_database_port = self.connection.settings_dict['PORT']

    @cached_property
    def monetdb_control(self):
        return pymonetdb.control.Control(self.monetdb_hostname,
                                       self.monetdb_port,
                                       self.monetdb_passphrase)

    def _create_test_db(self, verbosity, autoclobber):

        def create_monet_db():
            self.monetdb_control.create(self.test_database_name)
            self.monetdb_control.release(self.test_database_name)
            self.monetdb_control.start(self.test_database_name)

            con = pymonetdb.connect(hostname=self.test_database_host,
                                   port=self.test_database_port,
                                   database=self.test_database_name,
                                   username="monetdb",
                                   password="monetdb")

            if self.test_database_user != "monetdb":
                cur = con.cursor()
                params = {
                    'username': self.test_database_user,
                    'password': self.test_database_password,
                    'database': self.test_database_name,
                }
                cur.execute(auth_query % params)

        try:
            create_monet_db()
        except pymonetdb.OperationalError, e:
            sys.stderr.write(
                "Got an error creating the test database: %s\n" % e)
            if not autoclobber:
                confirm = raw_input(
                    "Type 'yes' if you would like to try deleting the test "
                    "database '%s', or 'no' to cancel: " % self.test_database_name)
            if autoclobber or confirm == 'yes':
                if verbosity >= 1:
                    print ("Destroying old test database '%s'..."
                           % self.connection.alias)
                try:
                    self._destroy_test_db(self.test_database_name, verbosity)
                    create_monet_db()
                except Exception, e:
                    sys.stderr.write(
                        "Got an error recreating the test database: %s\n" % e)
                    sys.exit(2)
            else:
                print "Tests cancelled."
                sys.exit(1)
        return self.test_database_name

    def _destroy_test_db(self, test_database_name, verbosity):
        print "stopping %s" % test_database_name
        try:
            self.monetdb_control.stop(self.test_database_name)
        except pymonetdb.OperationalError, e:
            print "warning: can't stop database"
            pass
        print "destroying %s" % test_database_name
        self.monetdb_control.destroy(self.test_database_name)
