import subprocess
import sys
import unittest

from django.conf import settings

#
# Must configure settings before opening database connection.
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
# to import the module django_monetdb.base.
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

	def testcreate(self):
		'''instantiate a cursor.'''
		import django_monetdb
		w = django_monetdb.base.DatabaseWrapper({})
		c = w.cursor()
		self.failUnless(c)

	def testbasicsql(self):
		'''Run some base SQL through cursor.  

		This time we get the cursor (and connection) the Django way.
		'''
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
		'''Get a database connection the Django way.'''
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

		The core issue is that if db_type() returns None, the field is 
		skipped.   And db_type() can return none if you have an error
		in your driver's data_type dictionary.
		'''

		from django.core.management import call_command
		call_command('syncdb')

	def testget_or_create(self):
		'''get_or_create requires driver to have an "ops" dictionary.

		ref: django/db/models/sql/where.py, make_atom()
		'''

		from django.core.management import call_command
		call_command('syncdb')

		from testapp.models import Simple
		obj, created = Simple.objects.get_or_create(name='one')

	def testcascadingdelete(self):
		'''in Django, deletes cascade.  test this works.'''

		from testapp.models import Simple, Parent, Aunt, GrandParent
		from django.core.management import call_command

		call_command('syncdb')

		s = Simple(name='one')
		s.save()
		s = Simple(name='two')
		s.save()

		#
		# Simple record should now be in database.
		#

		try:
			s = Simple.objects.get(name='one')
		except Simple.DoesNotExist:
			self.fail("didn't save Simple record")

		p = Parent(simple=s, name='p')
		p.save()
		try:
			tst = Parent.objects.get(name='p')
		except Parent.DoesNotExist:
			self.fail("didn't save Parent record")

		a = Aunt(simple=s, name='a')
		a.save()
		try:
			tst = Aunt.objects.get(name='a')
		except Aunt.DoesNotExist:
			self.fail("didn't save Aunt record")

		gp = GrandParent(parent=p, name='gp')
		gp.save()
		try:
			tst = GrandParent.objects.get(name='gp')
		except GrandParent.DoesNotExist:
			self.fail("didn't save GrandParent record")

		s.delete()

		#
		# Parent, Aunt and GrandParent records should now be gone from database.
		#

		ok = False
		try:
			tst = Parent.objects.get(name='p')
		except Parent.DoesNotExist:
			ok = True
		self.failIf(not ok, "delete did not cascade");

		ok = False
		try:
			tst = GrandParent.objects.get(name='gp')
		except GrandParent.DoesNotExist:
			ok = True
		self.failIf(not ok, "delete did not cascade");

		ok = False
		try:
			tst = Aunt.objects.get(name='a')
		except Aunt.DoesNotExist:
			ok = True
		self.failIf(not ok, "delete did not cascade");

	def testutf8(self):
		'''test that we can save and retrieve utf-8 characters.

		This was an attempt to duplicate a problem I hit with a real Django app;
		this test passed though, so I didn't capture the issue properly.
		'''

		from testapp.models import Simple, Parent, Aunt, GrandParent
		from django.core.management import call_command

		call_command('syncdb')

		cafe  = u"caf" + unichr(0x00E9)

		print "cafe=", cafe.encode('utf8')
		
		s = Simple(name=cafe)
		self.failUnless(s.name == cafe)

if __name__ == '__main__':
	unittest.main()
