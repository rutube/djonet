#! /bin/sh -e
#
# Delete test monetdb database.
#

db=test
user=test
pass=test
schema=test

[ "x$1" != "x" ] && db="$1"
[ "x$2" != "x" ] && user="$2"
[ "x$3" != "x" ] && pass="$3"
[ "x$4" != "x" ] && schema="$4"

echo "Stopping ${db} ..."
sudo monetdb stop ${db}
echo "Destroying ${db} ..."
sudo monetdb destroy -f ${db}
