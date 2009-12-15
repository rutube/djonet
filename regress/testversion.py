import sys

sys.path.append('../')
import base.py

db = base.DatabaseWrapper()

#
# If this raises 
#
#	django.core.exceptions.ImproperlyConfigured: 
#	Error loading MonetSQLdb module: No module named MonetSQLdb
#
# then you need to run 
#
#	python setup.py install 
#
# in 
#
#	monetdb/clients/src/python
#

version = db.get_server_version()
