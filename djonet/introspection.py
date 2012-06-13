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
 
from django.db.backends import BaseDatabaseIntrospection

class DatabaseIntrospection(BaseDatabaseIntrospection):

    data_types_reverse = {
        'boolean'    : 'BooleanField',
        'varchar'    : 'CharField',
        'date'       : 'DateField',
        'timestamp'  : 'DateTimeField',
        'numeric'    : 'FloatField',
        'double'    : 'FloatField',
        'int'        : 'IntegerField',
        'smallint'   : 'IntegerField',
        'clob'       : 'TextField',
        'time'       : 'TimeField',
	'tinyint'	: 'SmallIntegerField',
	'char'	: 'CharField',
    }

    def get_table_description(self, cursor, table_name):
        "Returns a description of the table, with the DB-API cursor.description interface."
        cursor.execute("SELECT * FROM %s LIMIT 1" % self.connection.ops.quote_name(table_name))
        return cursor.description

    def get_table_list(self, cursor):
        '''Return a list of table names in the current database.'''
        cursor.execute("SELECT name FROM sys.tables WHERE NOT system;")
        return [row[0] for row in cursor.fetchall()]

    def _name_to_index(self, cursor, table_name):
        """
        Returns a dictionary of {field_name: field_index} for the given table.
        Indexes are 0-based.
        """
        return dict([(d[0], i) for i, d in enumerate(self.get_table_description(cursor, table_name))])

    def get_relations(self, cursor, table_name):
        """
        Returns a dictionary of {field_index: (field_index_other_table, other_table)}
        representing all relationships to the given table. Indexes are 0-based.
        """
        my_field_dict = self._name_to_index(cursor, table_name)
        constraints = self.get_key_columns(cursor, table_name)
        relations = {}
        for my_fieldname, other_table, other_field in constraints:
            other_field_index = self._name_to_index(cursor, other_table)[other_field]
            my_field_index = my_field_dict[my_fieldname]
            relations[my_field_index] = (other_field_index, other_table)
        return relations

    def get_indexes(self, cursor, table_name):
        """
        Returns a dictionary of fieldname -> infodict for the given table,
        where each infodict is in the format:
            {'primary_key': boolean representing whether it's the primary key,
             'unique': boolean representing whether it's a unique index}

             note: monetdb doesn't support indexes
        """

        return {}
