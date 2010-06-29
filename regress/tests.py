# Copyright (c) 2009 - 2010, Mark Bucciarelli <mkbucc@gmail.com>
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

class SubprocessError(Exception): pass

def run(cmd):
	'''Wrapper for subprocess.call that handles errors.'''

	emsg = ''
	try:
		rc = subprocess.call(cmd, shell=True)
		if rc == 0:
			pass	# normal
		elif rc < 0:
			emsg = "%s, child terminated by signal %s" \
			    % (cmd, -rc)
		else:
			emsg = "%s, child returned error %s" % (cmd, rc)
	except OSError, e:
		emsg = "%s, execution failed: %s" % (cdm, e)
	if emsg:
		raise SubprocessError(emsg)
	

class TestMonetDjango(unittest.TestCase):
	'''Basic tests of MonetDB driver.'''

	def setUp(self):
		cmd = './createdb.sh "%s" "%s" "%s" "%s"' % \
		    (db, user, passwd, schema)
		run(cmd)

	def tearDown(self):

		from django.db import connection
		connection.close()

		# createdb.sh deletes b/f it creates.
		#cmd = './zapdb.sh "%s" "%s" "%s" "%s"' % \
		#    (db, user, passwd, schema)
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

		Note that this does not actually test that fields are
		created, just that syncdb command exits without error.
		For example, while developing this driver I noticed
		that the FloatField was not actually created, although
		syncdb completed.

		As a workaround for this particular issue, I used a float
		field in the unique_together section of the Meta subclass.
		But that's a one-off test hack; to really test, I should
		get a model instance and verify it's attributes match
		what was inserted into the db.

		The core issue is that if db_type() returns None, the
		field is skipped.   And db_type() can return none if
		you have an error in your driver's data_type dictionary.
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
		# Parent, Aunt and GrandParent records should now be
		# gone from database.
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
		'''utf-8 in, unicode out.'''

		from testapp.models import Simple, Parent, Aunt, GrandParent
		from django.core.management import call_command

		call_command('syncdb')

		unicode_cafe  = u"caf" + unichr(0x00E9)
		utf8_cafe = unicode_cafe.encode('utf8')

		print "cafe =", unicode_cafe.encode('utf8')
		
		s = Simple(name=unicode_cafe)
		s.save()

		#
		# When we retrieve object, name should now be unicode.
		# 

		o = Simple.objects.get(pk=1)
		django_cafe = o.name

		self.assertEqual(type(django_cafe), type(unicode_cafe))
		self.assertEqual(django_cafe, unicode_cafe)

	def test_startswith(self):
		from testapp.models import Simple
		from django.core.management import call_command
		from django.db.models import Count

		call_command('syncdb')

		names = (
		    'start 1',
		    'start 2',
		    'start 12',
		    'Start 12',
		    )
		for n in names:
			s = Simple(name=n)
			s.save()

		qs = Simple.objects.filter(name__startswith='start')
		q = qs.aggregate(n = Count('id'))
		self.assertEqual(q['n'], 3)

		qs = Simple.objects.filter(name__startswith='start 1')
		q = qs.aggregate(n = Count('id'))
		self.assertEqual(q['n'], 2)

		qs = Simple.objects.filter(name__startswith='start 12')
		q = qs.aggregate(n = Count('id'))
		self.assertEqual(q['n'], 1)

		qs = Simple.objects.filter(name__startswith='start 3')
		q = qs.aggregate(n = Count('id'))
		self.assertEqual(q['n'], 0)

		qs = Simple.objects.filter(name__startswith='tart 1')
		q = qs.aggregate(n = Count('id'))
		self.assertEqual(q['n'], 0)

	def test_istartswith(self):
		from testapp.models import Simple
		from django.core.management import call_command
		from django.db.models import Count

		call_command('syncdb')

		names = (
		    'Start 1',
		    'Start 2',
		    'Start 12',
		    )
		for n in names:
			s = Simple(name=n)
			s.save()

		qs = Simple.objects.filter(name__istartswith='start')
		q = qs.aggregate(n = Count('id'))
		self.assertEqual(q['n'], len(names))

		qs = Simple.objects.filter(name__istartswith='start 1')
		q = qs.aggregate(n = Count('id'))
		self.assertEqual(q['n'], 2)

		qs = Simple.objects.filter(name__istartswith='start 12')
		q = qs.aggregate(n = Count('id'))
		self.assertEqual(q['n'], 1)

		qs = Simple.objects.filter(name__istartswith='start 3')
		q = qs.aggregate(n = Count('id'))
		self.assertEqual(q['n'], 0)

		qs = Simple.objects.filter(name__istartswith='tart 1')
		q = qs.aggregate(n = Count('id'))
		self.assertEqual(q['n'], 0)

	def test_safeunicode(self):
		'''Slug fields have type SafeUnicode, we need to support
		this field type.'''

		from testapp.models import Simple
		from django.core.management import call_command
		from django.utils.safestring import SafeUnicode

		call_command('syncdb')

		n = SafeUnicode('a name')
		s = Simple(name=n)
		s.save()

	def test_autocommit_on_by_default(self):
		'''Django's default behavior is auto commit.'''

		from testapp.models import Simple
		from django.core.management import call_command
		from django.utils.safestring import SafeUnicode

		from monetdb.monetdb_exceptions import OperationalError

		call_command('syncdb')

		s = Simple(name='mark')
		s.save()
		s = Simple(name='mark')
		try:
			s.save()
		except OperationalError:
			pass

		# first one should be saved.
		s = Simple.objects.get(name='mark')
		self.assertTrue(a is not None)

if __name__ == '__main__':
	unittest.main()
