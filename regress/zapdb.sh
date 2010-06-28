#! /bin/sh -e
#
# Delete MonetDB database.
#

usage="usage: $0 <db> <user> <pass> <schema>"

[ "x$1" = "x" ] && echo $usage && exit 1
[ "x$2" = "x" ] && echo $usage && exit 1
[ "x$3" = "x" ] && echo $usage && exit 1
[ "x$4" = "x" ] && echo $usage && exit 1
db=$1
user=$2
pass=$3
schema=$4

# XXX: make a script argument like other params.
# The user that runs merovingian
merouser=mero

echo "Stopping ${db} ..."
sudo su - $merouser -c "monetdb stop ${db}"
echo "Destroying ${db} ..."
sudo su - $merouser -c "monetdb destroy -f ${db}"
