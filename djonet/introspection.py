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
	    'boolean'	: 'BooleanField',
	    'varchar'	: 'CharField',
	    'date'	: 'DateField',
	    'timestamp'	: 'DateTimeField',
	    'numeric'	: 'FloatField',
	    'int'	: 'IntegerField',
	    'smallint'	: 'IntegerField',
	    'clob'	: 'TextField',
	    'time'	: 'TimeField',
	}

	def get_table_list(self, cursor):
		'''Return a list of table names in the current database.'''
		cursor.execute("SELECT name FROM sys.tables WHERE NOT system;")
		return [row[0] for row in cursor.fetchall()]
