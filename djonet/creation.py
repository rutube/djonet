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
