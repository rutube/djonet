from django.db.backends import BaseDatabaseIntrospection
import re

foreign_key_re = re.compile(r"\sCONSTRAINT `[^`]*` FOREIGN KEY \(`([^`]*)`\) REFERENCES `([^`]*)` \(`([^`]*)`\)")

class DatabaseIntrospection(BaseDatabaseIntrospection):
    data_types_reverse = {
        'boolean'	: 'BooleanField',
        'varchar'	: 'CharField',
        'date'		: 'DateField',
        'timestamp'	: 'DateTimeField',
        'numeric'	: 'FloatField',
        'int'		: 'IntegerField',
        'smallint'	: 'IntegerField',
        'clob'		: 'TextField',
        'time'		: 'TimeField',
    }

    def get_table_list(self, cursor):
        "Returns a list of table names in the current database."
        cursor.execute("select name from sys.tables;")
        return [row[0] for row in cursor.fetchall()]
