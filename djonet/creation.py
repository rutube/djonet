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


import subprocess
import sys

#from django.conf import settings
from django.db.backends.creation import BaseDatabaseCreation

class DatabaseCreation(BaseDatabaseCreation):

    #
    # XXX: I didn't see where to define the max int values that fit
    # XXX: in the int fields.  The Positive* variants will hold less
    # XXX: than expected, as they use same type as the non-Positive*
    # XXX: ones.
    #

    #
    # Careful with things like %(max_digits)s.  If Django does not
    # require the property, then db_type() will return None (as
    # there will be a key error with the data dictionary, and the
    # field will not be added to the database table!
    #

    data_types = {
        'AutoField'			: 'int AUTO_INCREMENT',
        'BooleanField'		: 'boolean',
        'CharField'			: 'varchar(%(max_length)s)',
        'CommaSeparatedIntegerField': 'varchar(%(max_length)s)',
        'DateField'			: 'date',
        'DateTimeField'		: 'timestamp',
        'DecimalField'		: 'numeric(%(max_digits)s, %(decimal_places)s)',
        'FileField'			: 'varchar(%(max_length)s)',
        'FilePathField'		: 'varchar(%(max_length)s)',
        'FloatField'		: 'float',
        'IntegerField'		: 'int',
        'IPAddressField'		: 'char(15)',
        'GenericIPAddressField': 'char(39)',
        'NullBooleanField'		: 'boolean',
        'OneToOneField'		: 'int',
        'PositiveIntegerField'	: 'int',
        'PositiveSmallIntegerField'	: 'smallint',
        'SlugField'			: 'varchar(%(max_length)s)',
        'SmallIntegerField'		: 'smallint',
        'TextField'			: 'clob',
        'TimeField'			: 'time',
    }

    def _create_test_db(self, verbosity, autoclobber):
        """
        Internal implementation - creates the test db tables.
        """
        test_database_name = self._get_test_db_name()

        def create_monet_db():
            errorcode = subprocess.check_call(["monetdb", "create", test_database_name])
            if not errorcode:
                errorcode = subprocess.check_call(["monetdb", "release", test_database_name])
            if not errorcode:
                errorcode = subprocess.check_call(["monetdb", "start", test_database_name])
            return errorcode

        try:
            create_monet_db()
        except OSError, e:
            sys.stderr.write(
                "Can't find monetdb, make sure it is installed and in your PATH: %s\n" % e)
            import os
            sys.stderr.write(os.environ['PATH'])
            sys.exit(2)
        except subprocess.CalledProcessError, e:
            sys.stderr.write(
                "Got an error creating the test database: %s\n" % e)
            if not autoclobber:
                confirm = raw_input(
                    "Type 'yes' if you would like to try deleting the test "
                    "database '%s', or 'no' to cancel: " % test_database_name)
            if autoclobber or confirm == 'yes':
                if verbosity >= 1:
                    print ("Destroying old test database '%s'..."
                           % self.connection.alias)
                try:
                    subprocess.check_call(["monetdb", "stop", test_database_name])
                except Exception:
                    pass
                try:
                    subprocess.check_call(["monetdb", "destroy", "-f", test_database_name])
                    create_monet_db()
                except Exception, e:
                    sys.stderr.write(
                        "Got an error recreating the test database: %s\n" % e)
                    sys.exit(2)
            else:
                print "Tests cancelled."
                sys.exit(1)
        return test_database_name

    def _destroy_test_db(self, test_database_name, verbosity):
        self._prepare_for_test_db_ddl()

        try:
            subprocess.check_call(["monetdb", "stop", test_database_name])
        except Exception:
            pass
        try:
            subprocess.check_call(["monetdb", "destroy", "-f", test_database_name])
        except Exception, e:
            sys.stderr.write("Got an error destroying the test database: %s\n" % e)
