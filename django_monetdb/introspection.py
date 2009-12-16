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
		cursor.execute("select name from sys.tables;")
		return [row[0] for row in cursor.fetchall()]
