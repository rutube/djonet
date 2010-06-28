#! /bin/sh -e
#
# Create MonetDB database.  Destroys any data in that db.
#
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

usage="usage: $0 <db> <user> <pass> <schema>"

[ "x$1" = "x" ] && echo $usage && exit 1
[ "x$2" = "x" ] && echo $usage && exit 1
[ "x$3" = "x" ] && echo $usage && exit 1
[ "x$4" = "x" ] && echo $usage && exit 1

db=$1		# 'testdjangodb1'
user=$2		# 'django1'
pass=$3		# 'django1'
schema=$4	# 'django1'

# XXX: make a script argument like other params.
# The user that runs merovingian
merouser=mero

echo "(re)creating ${db} at ${host}"
sudo su - $merouser -c "monetdb stop ${db}"
sudo su - $merouser -c "monetdb destroy -f ${db}"
sudo su - $merouser -c "monetdb create ${db}" || exit 1
sudo su - $merouser -c "monetdb start ${db}" || exit 1

#
# I couldn't set password on command-line, despite what mclient man
# page says.
#

export DOTMONETDBFILE="./.testmonetdb"
cat > ${DOTMONETDBFILE} << EOF
user=monetdb
password=monetdb
language=sql
EOF

#
# Setup Django test user.
#

echo "Creating ${user} user with schema ${schema}:"
echo "user: ${user}"
echo "pass: ${pass}"
cat > t1.sql << EOF

CREATE USER "${user}" 
	WITH PASSWORD '${pass}' 
	NAME 'Django Test User' 
	SCHEMA "sys";

--
-- The AUTHORIZATION clause defines the schema owner.
-- 

CREATE SCHEMA "${schema}" AUTHORIZATION "${user}";

ALTER USER "${user}" SET SCHEMA "${schema}";

--
-- 	Note:
--
--	By default, MonetDB gives users select permission on the 
--	tables view in the sys schema.	So we don't need to issue
--	a grant statment like this:
--
--		GRANT select on tables to ${user};
-- 

EOF
mclient -d ${db} < t1.sql

#
# Release, so the test user can log in to the test database.
#

sudo su - $merouser -c "monetdb release ${db}"

rm ${DOTMONETDBFILE}
rm t1.sql
