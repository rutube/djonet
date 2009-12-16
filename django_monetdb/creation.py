#from django.conf import settings
from django.db.backends.creation import BaseDatabaseCreation

class DatabaseCreation(BaseDatabaseCreation):
	data_types = {
	    'AutoField':         'int AUTO_INCREMENT',
	    'BooleanField':      'boolean',
	    'CharField':         'varchar(%(max_length)s)',
	    'CommaSeparatedIntegerField': 'varchar(%(max_length)s)',
	    'DateField':         'date',
	    'DateTimeField':     'timestamp',
	    'DecimalField':      'numeric(%(max_digits)s, %(decimal_places)s)',
	    'FileField':         'varchar(%(max_length)s)',
	    'FilePathField':     'varchar(%(max_length)s)',
	    'FloatField':        'numeric(%(max_digits)s, %(decimal_places)s)',
	    'IntegerField':      'int',
	    'IPAddressField':    'char(15)',
	    'NullBooleanField':  'boolean',
	    'OneToOneField':     'int',
	    'PositiveIntegerField': 'int UNSIGNED',
	    'PositiveSmallIntegerField': 'smallint UNSIGNED',
	    'SlugField':         'varchar(%(max_length)s)',
	    'SmallIntegerField': 'smallint',
	    'TextField':         'clob',
	    'TimeField':         'time',
	    'USStateField':      'varchar(2)',
	}
	pass
