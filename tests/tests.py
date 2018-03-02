#!/usr/bin/env python
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
import pymonetdb.control
import pymonetdb

from django.conf import settings

#
# Must configure settings before opening database connection.
#

MONETDB_HOST = 'localhost'
MONETDB_PORT = 50000
MONETDB_PASSPHRASE = 'monetdb'

db = 'test_djonet'
user = 'test_djonet'
passwd = 'test_djonet'

settings.configure(
    DEBUG=True,
    DATABASES = {
        'default': {
            'ENGINE': 'djonet',
            'NAME': db,
            'USER': user,
            'PASSWORD': passwd,
        }
    },
    INSTALLED_APPS = ('testapp',),
)


auth_query = """
ALTER USER "monetdb" RENAME TO "%(username)s";
ALTER USER SET PASSWORD '%(password)s' USING OLD PASSWORD 'monetdb';
CREATE SCHEMA "%(database)s" AUTHORIZATION "%(username)s";
ALTER USER "%(username)s" SET SCHEMA "%(database)s";
"""


#
# In order for Django to find our driver for the unit tests, the parent
# directory of the source must be on the system path, as Django tries
# to import the module djonet.base.
#

sys.path.append('..')

class SubprocessError(Exception): pass

def create_database(name, user, password):
    control = pymonetdb.control.Control(MONETDB_HOST, MONETDB_PORT, MONETDB_PASSPHRASE)
    control.create(name)
    control.release(name)

    con = pymonetdb.connect(username='monetdb', password='monetdb',
                              hostname=MONETDB_HOST, port=MONETDB_PORT,
                              database=name)
    cur = con.cursor()

    params = {
        'username': user,
        'password': password,
        'database': name,
    }
    cur.execute(auth_query % params)


def destroy_database(name):
    control = pymonetdb.control.Control(MONETDB_HOST, MONETDB_PORT, MONETDB_PASSPHRASE)
    try:
        control.stop(name)
    except pymonetdb.OperationalError:
        pass
    control.destroy(name)



class TestMonetDjango(unittest.TestCase):
    '''Basic tests of MonetDB driver.'''

    def setUp(self):
        try:
            destroy_database(db)
        except pymonetdb.OperationalError:
            pass
        create_database(db, user, passwd)

    def tearDown(self):
        destroy_database(db)

    def testinit(self):
        '''instantiate our custom database wrapper.'''
        from djonet.base import DatabaseWrapper
        db = DatabaseWrapper({})

    def testcreate(self):
        '''instantiate a cursor.'''
        import djonet
        w = djonet.base.DatabaseWrapper({})
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

    def test_icontains(self):
        from testapp.models import Simple
        from django.core.management import call_command
        from django.db.models import Count

        call_command('syncdb')

        names = (
            'Start 1',
            '2 Start',
            'Art 2',
            '123 ART',
            )
        for n in names:
            s = Simple(name=n)
            s.save()

        qs = Simple.objects.filter(name__icontains='art')
        q = qs.aggregate(n = Count('id'))
        self.assertEqual(q['n'], len(names))

        qs = Simple.objects.filter(name__icontains='start')
        q = qs.aggregate(n = Count('id'))
        self.assertEqual(q['n'], 2)

        qs = Simple.objects.filter(name__icontains='art ')
        q = qs.aggregate(n = Count('id'))
        self.assertEqual(q['n'], 2)


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

    def test_autocommit_like_behavior(self):
        '''Django's default behavior is "like" auto commit.

        From Django docs, "Managing database transactions":

            Django's default behavior is to run with an open
            transaction which it commits automatically when any
            built-in, data-altering model function is called. For
            example, if you call model.save() or model.delete(),
            the change will be committed immediately.

            This is much like the auto-commit setting for most
            databases.

        Note the "much like" phrase.  Initially, I thought they
        meant you should turn on autocommit on the database
        connection, but that didn't work.  They mean that
        internally Django has code to mimic autocommit.
        '''

        from testapp.models import Simple
        from django.core.management import call_command
        from django.core.validators import ValidationError
        import django

        # full_clean() (used by this test) is new to Django 1.2
        maj = django.VERSION[0]
        min = django.VERSION[1]
        self.assertTrue(maj > 1 or (maj == 1 and min >= 2))
        
        call_command('syncdb')

        s = Simple(name='mark')
        s.save()
        s = Simple(name='mark')
        try:
            s.full_clean()    
            s.save()
        except ValidationError:
            pass

        # first one should be saved.
        s = Simple.objects.get(name='mark')
        self.assertTrue(s is not None)

    def test_loadfixture(self):
        '''Update sequence nextval's when a fixture is loaded.

        Note: Here's a great set of fixture unit tests:

        http://django-pyodbc.googlecode.com/svn/trunk/tests/fixtures/models.py
        '''

        from testapp.models import Simple
        from django.core import management
        from django.db.models import Count

        management.call_command('syncdb')
        management.call_command('loaddata', 'fixture1', verbosity=0)

        # Fixture should have loaded Two records.
        qs = Simple.objects.all()
        d = qs.aggregate(n = Count('id'))
        self.assertEqual(d['n'], 2)

        # We should be able to save a new record.
        s = Simple(name = 'abc xyz')
        s.save()

    def test_iexact(self):
        from testapp.models import Simple
        from django.core.management import call_command
        from django.db.models import Count

        call_command('syncdb')

        names = (
            'iExactly this',
            'iExactly This',
            'iExactly This not',
            'not iExactly This',
            )
        for n in names:
            s = Simple(name=n)
            s.save()

        iexact_matches_n = len(names) - 2

        qs = Simple.objects.filter(name__iexact='iExactly this')
        q = qs.aggregate(n = Count('id'))
        self.assertEqual(q['n'], iexact_matches_n)


if __name__ == '__main__':
    unittest.main()
