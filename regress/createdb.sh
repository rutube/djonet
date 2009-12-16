#! /bin/sh -e
#
# Create test monetdb.  Destroys any data in that db.
#

db=test
user=test
pass=test
schema=test

[ "x$1" != "x" ] && db="$1"
[ "x$2" != "x" ] && user="$2"
[ "x$3" != "x" ] && pass="$3"
[ "x$4" != "x" ] && schema="$4"

echo "(re)creating ${db} at ${host}"
sudo monetdb stop ${db}
sudo monetdb destroy -f ${db}
sudo monetdb create ${db} || exit 1
sudo monetdb start ${db} || exit 1

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

sudo monetdb release ${db}

rm ${DOTMONETDBFILE}
rm t1.sql
