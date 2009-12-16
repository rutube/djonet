#! /bin/sh -e
#
# Delete test monetdb database.
#

db=testdjangodb
user=django
pass=django
schema=django

[ "x$1" != "x" ] && db="$1"
[ "x$2" != "x" ] && user="$2"
[ "x$3" != "x" ] && pass="$3"
[ "x$4" != "x" ] && schema="$4"

echo "Deleting ${db}"
sudo monetdb stop ${db}
sudo monetdb destroy -f ${db}
