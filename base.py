from django.db.backends import *
from django.conf import settings

import monetdb.sql as Database

class DatabaseWrapper(BaseDatabaseWrapper):
    """
    Represents a database connection.
    """

    ops = None

    def __init__(self, settings_dict):
        super(DatabaseWrapper, self).__init__(settings_dict)

        # `settings_dict` should be a dictionary containing keys such as
        # DATABASE_NAME, DATABASE_USER, etc. It's called `settings_dict`
        # instead of `settings` to disambiguate it from Django settings
        # modules.
        #self.connection = None
        #self.queries = []
        #self.settings_dict = settings_dict

        self.features = DatabaseFeatures()
        self.ops = DatabaseOperations()

    def _cursor(self):
	kwargs = {}
        if not self.connection:
            if settings.DATABASE_USER:
                kwargs['username'] = settings.DATABASE_USER
            if settings.DATABASE_NAME:
                kwargs['database'] = settings.DATABASE_NAME
            if settings.DATABASE_PASSWORD:
                kwargs['password'] = settings.DATABASE_PASSWORD
            self.connection = Database.connect(**kwargs)
        return self.connection.cursor()

class DatabaseFeatures(BaseDatabaseFeatures):

    #
    # I'm not sure about this one.  If MonetDB can select from a table
    # it's updating, then we can leave this as the default of True.
    # Setting it to False is slower but will always work.  See
    # Django's source file db/models/sql/subqueries.py for the only place
    # this is used.
    #

    update_can_self_select = False

    #
    # Again, I'm not sure about this, so I'll use the more conservative
    # settings.
    #
    # Here's a relevant comment from the only file that uses this setting:
    # db/models/fields/related.py:
    #
    #     The database column type of a ForeignKey is the column type
    #     of the field to which it points. An exception is if the
    #     ForeignKey points to an AutoField / PositiveIntegerField /
    #     PositiveSmallIntegerField, in which case the column type
    #     is simply that of an IntegerField.  If the database needs
    #     similar types for key fields however, the only thing we can
    #     do is making AutoField an IntegerField.
    #

    related_fields_match_type = False

class DatabaseOperations(BaseDatabaseOperations):
    """
    This class encapsulates all backend-specific differences, such as the way
    a backend performs ordering or calculates the ID of a recently-inserted
    row.
    """

    pass

#    def date_extract_sql(self, lookup_type, field_name):
#        """
#        Given a lookup_type of 'year', 'month' or 'day', returns the SQL that
#        extracts a value from the given date field field_name.
#        """
#        raise NotImplementedError()
#
#    def date_trunc_sql(self, lookup_type, field_name):
#        """
#        Given a lookup_type of 'year', 'month' or 'day', returns the SQL that
#        truncates the given date field field_name to a DATE object with only
#        the given specificity.
#        """
#        raise NotImplementedError()
#
#    def fulltext_search_sql(self, field_name):
#        """
#        Returns the SQL WHERE clause to use in order to perform a full-text
#        search of the given field_name. Note that the resulting string should
#        contain a '%s' placeholder for the value being searched against.
#        """
#        raise NotImplementedError('Full-text search is not implemented for this database backend')
#
#    def no_limit_value(self):
#        """
#        Returns the value to use for the LIMIT when we are wanting "LIMIT
#        infinity". Returns None if the limit clause can be omitted in this case.
#        """
#        raise NotImplementedError
#
#    def quote_name(self, name):
#        """
#        Returns a quoted version of the given table, index or column name. Does
#        not quote the given name if it's already been quoted.
#        """
#        raise NotImplementedError()
#
#    def regex_lookup(self, lookup_type):
#        """
#        Returns the string to use in a query when performing regular expression
#        lookups (using "regex" or "iregex"). The resulting string should
#        contain a '%s' placeholder for the column being searched against.
#
#        If the feature is not supported (or part of it is not supported), a
#        NotImplementedError exception can be raised.
#        """
#        raise NotImplementedError
#
#    def savepoint_create_sql(self, sid):
#        """
#        Returns the SQL for starting a new savepoint. Only required if the
#        "uses_savepoints" feature is True. The "sid" parameter is a string
#        for the savepoint id.
#        """
#        raise NotImplementedError
#
#    def savepoint_commit_sql(self, sid):
#        """
#        Returns the SQL for committing the given savepoint.
#        """
#        raise NotImplementedError
#
#    def savepoint_rollback_sql(self, sid):
#        """
#        Returns the SQL for rolling back the given savepoint.
#        """
#        raise NotImplementedError
#
#    def sql_flush(self, style, tables, sequences):
#        """
#        Returns a list of SQL statements required to remove all data from
#        the given database tables (without actually removing the tables
#        themselves).
#
#        The `style` argument is a Style object as returned by either
#        color_style() or no_style() in django.core.management.color.
#        """
#        raise NotImplementedError()
#
