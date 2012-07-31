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

import re

from django.db.backends import util
from django.db.backends import BaseDatabaseOperations

class DatabaseOperations(BaseDatabaseOperations):
    '''
    Tells Django how to build a SQL where clauses from a Django model query.

    Also encapsulates all backend-specific differences, such
    as the way a backend performs ordering or calculates the ID of
    a recently-inserted row.
    '''

    #
    #    'endswith'        : 'LIKE %s',
    #    'iendswith'    : 'ILIKE %s',
    #    'iexact'        : 'ILIKE %s',
    #

    compiler_module = "djonet.compiler"

    operators = {
        'gt'        : '>  %s',
        'gte'        : '>= %s',
        'lt'        : '<  %s',
        'lte'        : '<= %s',
        'exact'        : '=  %s',
        'startswith'    : 'LIKE %s',
        'istartswith'    : 'ILIKE %s',
        'iexact'        : 'ILIKE %s',
        'icontains'        : 'ILIKE %s',
    }

    def quote_name(self, name):
        '''Return quoted name of table, index or column name.'''

        name = re.sub('-', '', name)

        if name.startswith('"') and name.endswith('"'):
            return name
        return '"%s"' % (name,)

    def sql_flush(self, style, tables, sequences):
        """
        Returns a list of SQL statements required to remove all data from
        the given database tables (without actually removing the tables
        themselves).

        The `style` argument is a Style object as returned by either
        color_style() or no_style() in django.core.management.color.
        """
        sql = []
        if tables:
            for table in tables:
                sql.append('%s %s;' % (style.SQL_KEYWORD('DELETE FROM'), style.SQL_FIELD(self.quote_name(table))))
        return sql


    def date_extract_sql(self, lookup_type, field_name):
        '''Given a lookup_type of 'year', 'month' or 'day',
        returns the SQL that extracts a value from the given
        date field field_name.
            '''

        return "EXTRACT(%s FROM %s)" % (lookup_type, field_name)

    def start_transaction_sql(self):
        '''MonetDB uses START TRANSACTION not BEGIN.'''

        return 'START TRANSACTION;'

    def model_to_sequencesql(self, m):
        '''Make the SQL statement that updates the tables primary
        key sequence.  Return empty string if no SQL needed.
        '''

        from django.db import connection

        # tbl has app_label prefix; e.g., testapp_simple
        tbl = m._meta.db_table

        # Get name of sequence for this table.  Here's
        # a trace from doing it manually.
        #
        #     sql>  select "default" from sys.columns 
        #     more> where table_id = 4186 and name = 'id';
        #     +-------------------------------------+
        #     | default                             |
        #     +=====================================+
        #     | next value for "django1"."seq_4176" |
        #     +-------------------------------------+
        #     1 tuple
        #     sql>
        #

        c = connection.cursor()
        fmt = '''
SELECT 
  "default" 
FROM 
  sys.columns 
WHERE 
  table_id = (SELECT id FROM sys.tables where name = %s) AND
  name = 'id'
;
'''
        c.execute(fmt, [tbl,])
        row = c.fetchone()
        # default = 'next value for "django1"."seq_4176"'
        default = row[0]
        p = default.rfind('"."seq_')
        if p == -1:
            return ''

        # seq = '"seq_4176"'
        seq = default[p + 2:]

        fmt = 'ALTER SEQUENCE %s RESTART WITH (SELECT MAX(id) + 1 FROM %s);'

        return fmt % (seq, tbl)

    def sequence_reset_sql(self, style, model_list):
        '''Return list of sequence update SQL for given models.

        Style is how to color the output for a terminal??!!'''

        from django.db import models

        fmt = "ALTER SEQUENCE %s RESTART WITH (SELECT MAX(id) + 1 FROM %s);"

        rval = []
        for model in model_list:
            sql = self.model_to_sequencesql(model)
            if sql:
                rval.append(sql)
        return rval

    def value_to_db_decimal(self, value, max_digits, decimal_places):
        """
        Transform a decimal.Decimal value to an object compatible with what is
        expected by the backend driver for decimal (numeric) columns.
        """
        if value is None:
            return None

        # monetdb only supports only 18 digitis for decimal
        max_digits = min(max_digits, 18)
        decimal_places = min(decimal_places, 17)
        return util.format_number(value, max_digits, decimal_places)

#
#    def date_trunc_sql(self, lookup_type, field_name):
#        fields = ['year', 'month', 'day', 'hour', 'minute', 'second']
#        format = ('%%Y-', '%%m', '-%%d', ' %%H:', '%%i', ':%%s') 
#        format_def = ('0000-', '01', '-01', ' 00:', '00', ':00')
#        try:
#            i = fields.index(lookup_type) + 1
#        except ValueError:
#            sql = field_name
#        else:
#            format_str = ''.join([f for f in format[:i]] + [f for f in format_def[i:]])
#            sql = "CAST(DATE_FORMAT(%s, '%s') AS DATETIME)" % (field_name, format_str)
#        return sql
#
#    def drop_foreignkey_sql(self):
#        return "DROP FOREIGN KEY"
#
#    def fulltext_search_sql(self, field_name):
#        return 'MATCH (%s) AGAINST (%%s IN BOOLEAN MODE)' % field_name
#
#    def no_limit_value(self):
#        # 2**64 - 1, as recommended by the MySQL documentation
#        return 18446744073709551615L
#

#
#    def random_function_sql(self):
#        return 'RAND()'
#
#    def sql_flush(self, style, tables, sequences):
#        # NB: The generated SQL below is specific to MySQL
#        # 'TRUNCATE x;', 'TRUNCATE y;', 'TRUNCATE z;'... style SQL statements
#        # to clear all tables of all data
#        if tables:
#            sql = ['SET FOREIGN_KEY_CHECKS = 0;']
#            for table in tables:
#                sql.append('%s %s;' % (style.SQL_KEYWORD('TRUNCATE'), style.SQL_FIELD(self.quote_name(table))))
#            sql.append('SET FOREIGN_KEY_CHECKS = 1;')
#
#            # 'ALTER TABLE table AUTO_INCREMENT = 1;'... style SQL statements
#            # to reset sequence indices
#            sql.extend(["%s %s %s %s %s;" % \
#                (style.SQL_KEYWORD('ALTER'),
#                 style.SQL_KEYWORD('TABLE'),
#                 style.SQL_TABLE(self.quote_name(sequence['table'])),
#                 style.SQL_KEYWORD('AUTO_INCREMENT'),
#                 style.SQL_FIELD('= 1'),
#                ) for sequence in sequences])
#            return sql
#        else:
#            return []
#
#    def value_to_db_datetime(self, value):
#        if value is None:
#            return None
#        
#        # MySQL doesn't support tz-aware datetimes
#        if value.tzinfo is not None:
#            raise ValueError("MySQL backend does not support timezone-aware datetimes.")
#
#        # MySQL doesn't support microseconds
#        return unicode(value.replace(microsecond=0))
#
#    def value_to_db_time(self, value):
#        if value is None:
#            return None
#            
#        # MySQL doesn't support tz-aware datetimes
#        if value.tzinfo is not None:
#            raise ValueError("MySQL backend does not support timezone-aware datetimes.")
#        
#        # MySQL doesn't support microseconds
#        return unicode(value.replace(microsecond=0))
#
#    def year_lookup_bounds(self, value):
#        # Again, no microseconds
#        first = '%s-01-01 00:00:00'
#        second = '%s-12-31 23:59:59.99'
#        return [first % value, second % value]
