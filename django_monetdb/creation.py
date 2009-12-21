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
	    'NullBooleanField'		: 'boolean',
	    'OneToOneField'		: 'int',
	    'PositiveIntegerField'	: 'int',
	    'PositiveSmallIntegerField'	: 'smallint',
	    'SlugField'			: 'varchar(%(max_length)s)',
	    'SmallIntegerField'		: 'smallint',
	    'TextField'			: 'clob',
	    'TimeField'			: 'time',
	}
