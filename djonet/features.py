
from django.db.backends import BaseDatabaseFeatures

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
