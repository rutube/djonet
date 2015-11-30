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

from django.db.backends import BaseDatabaseOperations
from djonet.introspection import DatabaseIntrospection


def toposort(data):
    """Dependencies are expressed as a dictionary whose keys are items
and whose values are a set of dependent items. Output is a list of
sets in topological order. The first set consists of items with no
dependences, each subsequent set consists of items that depend upon
items in the preceeding sets.

found on:
http://code.activestate.com/recipes/578272-topological-sort/

>>> print '\\n'.join(repr(sorted(x)) for x in toposort2({
...     2: set([11]),
...     9: set([11,8]),
...     10: set([11,3]),
...     11: set([7,5]),
...     8: set([7,3]),
...     }) )
[3, 5, 7]
[8, 11]
[2, 9, 10]
"""

    from functools import reduce

    # Ignore self dependencies.
    for k, v in data.items():
        v.discard(k)
    # Find all items that don't depend on anything.
    extra_items_in_deps = reduce(set.union, data.itervalues()) - set(data.iterkeys())
    # Add empty dependences where needed
    data.update({item:set() for item in extra_items_in_deps})
    while True:
        ordered = set(item for item, dep in data.iteritems() if not dep)
        if not ordered:
            break
        yield ordered
        data = {item: (dep - ordered)
                for item, dep in data.iteritems()
                    if item not in ordered}

    assert not data, "Cyclic dependencies exist among these items:\n%s" %\
                     '\n'.join(repr(x) for x in data.iteritems())


class DatabaseOperations(BaseDatabaseOperations):
    compiler_module = "djonet.compiler"

    operators = {
        'gt': '>  %s',
        'gte': '>= %s',
        'lt': '<  %s',
        'lte': '<= %s',
        'exact': '=  %s',
        'startswith': 'LIKE %s',
        'istartswith': 'ILIKE %s',
        'iexact': 'ILIKE %s',
        'icontains': 'ILIKE %s',
    }

    def quote_name(self, name):
        """Return quoted name of table, index or column name."""
        name = re.sub('-', '', name)
        if name.startswith('"') and name.endswith('"'):
            return name
        return '"%s"' % (name,)

    def sql_flush(self, style, tables, sequences, allow_cascade=False):
        """
        Returns a list of SQL statements required to remove all data from
        the given database tables (without actually removing the tables
        themselves).

        The `style` argument is a Style object as returned by either
        color_style() or no_style() in django.core.management.color.

        Since we can't disable foreign key checks, we need to do some sort
        of ordering. Topological sorting is applied to make sure no referred
        foreign keys are deleted. This only works in a-cycling references.
        """
        if not tables:
            return []

        introspection = DatabaseIntrospection(self.connection)
        cursor = self.connection.connection.cursor()

        all_relations = {}
        for table in tables:
            relations = introspection.get_relations(cursor, table)
            for field, other_table in relations.values():
                if other_table not in all_relations:
                    all_relations[other_table] = [table]
                else:
                    all_relations[other_table].append(table)

        all_relations = dict([(k, set(v)) for k, v in all_relations.items()])
        sorted_topo = toposort(all_relations)
        sorted_tables = [j for i in sorted_topo for j in i]

        sql = []
        for table in sorted_tables:
            sql.append('%s %s;' % (style.SQL_KEYWORD('DELETE FROM'),
                                   style.SQL_FIELD(self.quote_name(table)))
                       )
        return sql

    def date_extract_sql(self, lookup_type, field_name):
        """
        Given a lookup_type of 'year', 'month' or 'day', returns the SQL that
        extracts a value from the given date field field_name.
        """
        return "EXTRACT(%s FROM %s)" % (lookup_type, field_name)

    def date_interval_sql(self, sql, connector, timedelta):
        """
        Implements the date interval functionality for expressions
        """
        raise NotImplementedError()

    def date_trunc_sql(self, lookup_type, field_name):
        """
        Given a lookup_type of 'year', 'month' or 'day', returns the SQL that
        truncates the given date field field_name to a date object with only
        the given specificity.
        """
        fields = ['year', 'month', 'day', 'hour', 'minute', 'second']
        format = ('%%Y-', '%%m', '-%%d', ' %%H:', '%%i', ':%%s')
        format_def = ('0000-', '01', '-01', ' 00:', '00', ':00')
        try:
            i = fields.index(lookup_type) + 1
        except ValueError:
            sql = field_name
        else:
            format_str = ''.join([f for f in format[:i]] + [f for f in format_def[i:]])
            sql = "CAST(date_to_str(%s, '%s') AS DATE)" % (field_name, format_str)
        return sql

    def datetime_cast_sql(self):
        """
        Returns the SQL necessary to cast a datetime value so that it will be
        retrieved as a Python datetime object instead of a string.

        This SQL should include a '%s' in place of the field's name.
        """
        return "%s"

    def datetime_extract_sql(self, lookup_type, field_name, tzname):
        """
        Given a lookup_type of 'year', 'month', 'day', 'hour', 'minute' or
        'second', returns the SQL that extracts a value from the given
        datetime field field_name, and a tuple of parameters.
        """
        # FIXME TZ support
        return "EXTRACT(%s FROM %s)" % (lookup_type, field_name), []

    def datetime_trunc_sql(self, lookup_type, field_name, tzname):
        """
        Given a lookup_type of 'year', 'month', 'day', 'hour', 'minute' or
        'second', returns the SQL that truncates the given datetime field
        field_name to a datetime object with only the given specificity, and
        a tuple of parameters.
        """
        #FIXME TZ support
        # if settings.USE_TZ:
        #     field_name = "CONVERT_TZ(%s, 'UTC', %%s)" % field_name
        #     params = [tzname]
        # else:
        #     params = []
        fields = ['year', 'month', 'day', 'hour', 'minute', 'second']
        # Use double percents to escape.
        format = ('%%Y-', '%%m', '-%%d', ' %%H:', '%%i', ':%%s')
        format_def = ('0000-', '01', '-01', ' 00:', '00', ':00')
        try:
            i = fields.index(lookup_type) + 1
        except ValueError:
            sql = field_name
        else:
            format_str = ''.join([f for f in format[:i]] + [f for f in format_def[i:]])
            sql = "CAST(timestamp_to_str(%s, '%s') AS TIMESTAMP)" % (field_name, format_str)

        return sql, []

    def start_transaction_sql(self):
        """MonetDB uses START TRANSACTION not BEGIN."""
        return 'START TRANSACTION;'

    def model_to_sequencesql(self, m):
        """Make the SQL statement that updates the tables primary
        key sequence.  Return empty string if no SQL needed.
        """
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

        c = self.connection.cursor()
        fmt = """
SELECT
  "default"
FROM
  sys.columns
WHERE
  table_id = (SELECT id FROM sys.tables where name = %s) AND
  name = 'id'
;
"""
        c.execute(fmt, [tbl, ])
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
        """Return list of sequence update SQL for given models."""
        results = []
        for model in model_list:
            sql = self.model_to_sequencesql(model)
            if sql:
                results.append(sql)
        return results

    def random_function_sql(self):
        return "RAND()"
