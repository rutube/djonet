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
    DATABASE_NAME=db,
    DATABASE_USER=user,
    DATABASE_PASSWORD=passwd
)
sys.path.append('../')
import base

def run(cmd):
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

	def setUp(self):
		cmd = './createdb.sh "%s" "%s" "%s" "%s"' % \
		    (db, user, passwd, schema)
		run(cmd)


	def tearDown(self):
		cmd = './zapdb.sh "%s" "%s" "%s" "%s"' % \
		    (db, user, passwd, schema)
		run(cmd)

	def testinit(self):
		'''instantiate our custom database wrapper.'''
		db = base.DatabaseWrapper({})

	def testcreate(self):
		'''instantiate a cursor.'''
		w = base.DatabaseWrapper({})
		c = w.cursor()
		self.failUnless(c)

	def testbasicsql(self):
		'''Run some base SQL through cursor.'''
		w = base.DatabaseWrapper({})
		c = w.cursor()
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

if __name__ == '__main__':
	unittest.main()
