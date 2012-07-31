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
 
from django.db.backends import *
from django.conf import settings

import monetdb.sql as Database

from djonet.introspection import DatabaseIntrospection
from djonet.creation import DatabaseCreation
from djonet.operations import DatabaseOperations
from djonet.features import DatabaseFeatures
from djonet.validation import DatabaseValidation

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError

class DatabaseWrapper(BaseDatabaseWrapper):
    operators = DatabaseOperations.operators

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.features = DatabaseFeatures(self)
        self.ops = DatabaseOperations(self)
        self.validation = DatabaseValidation(self)
        self.introspection = DatabaseIntrospection(self)
        self.creation = DatabaseCreation(self)

    def _cursor(self):
        settings_dict = self.settings_dict
        kwargs = {}
        if not self.connection:
            if settings_dict['USER']:
                kwargs['username'] = settings_dict['USER']
            if settings_dict['NAME']:
                kwargs['database'] = settings_dict['NAME']
            if settings_dict['PASSWORD']:
                kwargs['password'] = settings_dict['PASSWORD']
            if settings_dict['HOST']:
                kwargs['hostname'] = settings_dict['HOST']
            if settings_dict['PORT']:
                kwargs['port'] = int(settings_dict['PORT'])

            self.connection = Database.connect(**kwargs)

        cursor = self.connection.cursor()
        cursor.arraysize = 1000
    	return cursor
