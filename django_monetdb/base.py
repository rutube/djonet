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
 
from django.db.backends import *
from django.conf import settings

import monetdb.sql as Database

from django_monetdb.cursorwrapper import CursorWrapper
from django_monetdb.introspection import DatabaseIntrospection
from django_monetdb.creation import DatabaseCreation
from django_monetdb.operations import DatabaseOperations

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError

class DatabaseWrapper(BaseDatabaseWrapper):
    '''A database connection.'''

    operators = DatabaseOperations.operators

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.features = DatabaseFeatures()
        self.ops = DatabaseOperations()
        self.validation = BaseDatabaseValidation(self)
        self.introspection = DatabaseIntrospection(self)
        self.creation = DatabaseCreation(self)

    def _cursor(self):
	kwargs = {}
        if not self.connection:
            if settings.DATABASE_USER:
                kwargs['username'] = settings.DATABASE_USER
            if settings.DATABASE_NAME:
                kwargs['database'] = settings.DATABASE_NAME
            if settings.DATABASE_PASSWORD:
                kwargs['password'] = settings.DATABASE_PASSWORD
            # Force strings to always come back as unicode.
            kwargs['use_unicode'] = True

            self.connection = Database.connect(**kwargs)

        c =  self.connection.cursor()

	#
	# fetch more rows at once, makes things faster (useable, actually)
	#

	c.arraysize = 1000

        #return c
	return CursorWrapper(c)

#    def _enter_transaction_management(self, managed):
#        pass
#
#    def _leave_transaction_management(self, managed):
#        pass

class DatabaseFeatures(BaseDatabaseFeatures):

    #
    # I'm not sure about this one.  If MonetDB can select from a table
    # it's updating, then we can leave this as the default of True.
    # Setting it to False is slower but will always work.  See
    # Django's source file db/models/sql/subqueries.py for the only place
    # this is used.
    #

    update_can_self_select = False

    #
    # Again, I'm not sure about this, so I'll use the more conservative
    # settings.
    #
    # Here's a relevant comment from the only file that uses this setting:
    # db/models/fields/related.py:
    #
    #     The database column type of a ForeignKey is the column type
    #     of the field to which it points. An exception is if the
    #     ForeignKey points to an AutoField / PositiveIntegerField /
    #     PositiveSmallIntegerField, in which case the column type
    #     is simply that of an IntegerField.  If the database needs
    #     similar types for key fields however, the only thing we can
    #     do is making AutoField an IntegerField.
    #

    related_fields_match_type = False
