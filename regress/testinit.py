# We should be able to create an instance of the database wrapper class.

import sys

from django.conf import settings

settings.configure(DEBUG=True)

sys.path.append('../')
import base

db = base.DatabaseWrapper({})
