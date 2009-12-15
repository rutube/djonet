#! /bin/sh -e
#
# Create test monetdb.  Destroys any data in that db.
#

db=testdjangodb
schema=django
user=django
pass=django

echo "(re)creating ${db} at ${host}"
monetdb stop ${db}
monetdb destroy -f ${db}
monetdb create ${db} || exit 1
monetdb start ${db} || exit 1

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

EOF
mclient -d ${db} < t1.sql

#
# Release, so the django user can log in to the test database.
#

monetdb release ${db}
