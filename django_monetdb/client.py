# Copyright (c) 2009 - 2010, Mark Bucciarelli <mkbucc@gmail.com>
# Copyright (c) 2009 Vikram Bhandoh <vikram@bhandoh.com>
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
 
from django.db.backends import BaseDatabaseClient
from django.conf import settings
import os

class DatabaseClient(BaseDatabaseClient):
    def runshell(self):
        args = ['']
        db = settings.DATABASE_OPTIONS.get('db', settings.DATABASE_NAME)
        user = settings.DATABASE_OPTIONS.get('user', settings.DATABASE_USER)
        passwd = settings.DATABASE_OPTIONS.get('passwd', settings.DATABASE_PASSWORD)
        host = settings.DATABASE_OPTIONS.get('host', settings.DATABASE_HOST)
        port = settings.DATABASE_OPTIONS.get('port', settings.DATABASE_PORT)
        defaults_file = settings.DATABASE_OPTIONS.get('read_default_file')
        # Seems to be no good way to set sql_mode with CLI
    
        if defaults_file:
            args += ["--defaults-file=%s" % defaults_file]
        if user:
            args += ["--user=%s" % user]
        if passwd:
            args += ["--password=%s" % passwd]
        if host:
            args += ["--host=%s" % host]
        if port:
            args += ["--port=%s" % port]
        if db:
            args += [db]

        os.execvp('monet', args)
