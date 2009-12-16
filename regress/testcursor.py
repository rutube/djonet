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

class TestCursor(unittest.TestCase):

	def setUp(self):
		cmd = './createdb.sh "%s" "%s" "%s" "%s"' % (db, user, passwd, schema)
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


	def tearDown(self):
		# XXX: delete database created in setup.
		pass

	def testcreate(self):
		w = base.DatabaseWrapper({})
		c = w.cursor()
		self.failUnless(c)

if __name__ == '__main__':
	unittest.main()
