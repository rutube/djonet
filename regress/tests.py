import subprocess
import sys
import unittest

from django.conf import settings

#
# Must configure settings before importing base.
#

db = 'testdjangodb1'
schema = 'django1'
user = 'django1'
passwd = 'django1'

settings.configure(
    DEBUG=True,
    DATABASE_ENGINE='django_monetdb',
    DATABASE_NAME=db,
    DATABASE_USER=user,
    DATABASE_PASSWORD=passwd,
    INSTALLED_APPS = ('testapp',),
)

#
# In order for Django to find our driver for the unit tests, the parent
# directory of the source must be on the system path, as Django tries
# to import monetdb.base.
#

sys.path.append('..')

def run(cmd):
	'''Wrapper for subprocess.call that handles errors.'''
	try:
		rc = subprocess.call(cmd, shell=True)
		if rc == 0:
			pass	# normal
		elif rc < 0:
			self.fail("Child was terminated by signal %s" % (-rc,))
		else:
			self.fail("Child returned error code %s" % (rc,))
	except OSError, e:
		self.fail("Execution failed:", e)
	

class TestMonetDjango(unittest.TestCase):
	'''Basic tests of MonetDB driver.'''

	def setUp(self):
		cmd = './createdb.sh "%s" "%s" "%s" "%s"' % \
		    (db, user, passwd, schema)
		run(cmd)

	def tearDown(self):

		from django.db import connection
		connection.close()

		cmd = './zapdb.sh "%s" "%s" "%s" "%s"' % \
		    (db, user, passwd, schema)
		#run(cmd)

	def testinit(self):
		'''instantiate our custom database wrapper.'''
		from django_monetdb.base import DatabaseWrapper
		db = DatabaseWrapper({})
		#import django_monetdb
		#db = django_monetdb.base.DatabaseWrapper({})

	def testcreate(self):
		'''instantiate a cursor.'''
		import django_monetdb
		w = django_monetdb.base.DatabaseWrapper({})
		c = w.cursor()
		self.failUnless(c)

	def testbasicsql(self):
		'''Run some base SQL through cursor.'''
		from django.db import connection
		c = connection.cursor()
		s = "CREATE TABLE test (id int, name varchar(10))"
		c.execute(s)
		s = "INSERT INTO test values (1, 'one')"
		c.execute(s)
		s = "INSERT INTO test values (2, 'two')"
		c.execute(s)
		s = "INSERT INTO test values (3, 'three')"
		c.execute(s)
		s = "SELECT name FROM test WHERE id = 2"
		self.failUnless(c.execute(s) == 1)
		row = c.fetchone()
		self.failUnless(row[0] == 'two')

	def testconnection(self):
		from django.db import connection
		c = connection.cursor()
		self.assert_(c)

	def testsyncdb(self):
		'''Does syncdb run (using models.py in the testapp subdir)?

		Note that this does not actually test that fields are created,
		just that syncdb command exits without error.  For example, 
		while developing this driver I noticed that the FloatField was
		not actually created, although syncdb completed.

		As a workaround for this particular issue, I used a float field 
		in the unique_together section of the Meta subclass.  But that's
		a one-off test hack; to really test, I should get a model instance
		and verify it's attributes match what was inserted into the db.
		'''

		from django.core.management import call_command
		call_command('syncdb')

if __name__ == '__main__':
	unittest.main()
