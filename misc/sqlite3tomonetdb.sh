#! /bin/sh -e
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
 
#
# Dump a sqlite3 table to stdout, changing SQL to fit MonetDB Assumes
# table is already created in MonetDB (it will be if Django's syncdb
# command).
#
# Sample usage:
#
#		$ ./sqlite3tomonetdb.sh ./my.db fromtbl totbl > t.sql
#		$ mclient -l sql -d mydb -u myuser < t.sql
#		<enter password>
#
# Or, you can combine both commands together and skip creating the
# interim file
#
#		$ ./sqlite3tomonetdb.sh ./my.db fromtbl totbl \
#		> | mclient -l sql -d mydb -u myuser
#		<enter password>
#		$
#
# If table has a sequence, and you inserted the autoid's from the
# sqlite3 table, you have to tell Monet DB to start at a higher number
# than the last-used id.
#
#		$ mclient -l sql -d mydb -u myuser -s "\d newtable"
#		sql> \d newtable
#		<read sequence name from output>
#		sql> \q
#		$ mclient -l sql -d mydb -u myuser -s \
#		> -s "alter sequence myseq restart with (select max(id)+1 from newtable);"
#		$
#

usage="$0 <sqlite3_db> <sqlite3_table> <monetdb_table>"

[ "x$1" = "x" ] && echo ${usage} >> /dev/stderr && exit 1
[ "x$2" = "x" ] && echo ${usage} >> /dev/stderr && exit 1
[ "x$3" = "x" ] && echo ${usage} >> /dev/stderr && exit 1

db=${1}
from=${2}
to=${3}

#
# Modifications to SQLite3 output:
#
#	1. Change table name <from> to <to>
#	2. Remove the CREATE INDEX and CREATE TABLE commands
#	3. Change BEGIN to START TRANSACTION
#

sqlite3 ${db} ".dump ${from}" \
| sed "s/${from}/${to}/" \
| grep -v "^CREATE INDEX" \
| sed "s/BEGIN \{1,\}TRAN/START TRAN/" \
| awk '\
	BEGIN		{ flag = 0} \
	/CREATE TABLE/	{ flag = 1; next} \
	flag == 1 	{ if ($0 == ");") flag = 0; next;} \
	flag == 0	{ print $0; } \
	' 

cat << EOF

-- 
-- Now manually run something similar to:
--	alter sequence <seq name> restart with (select max(id)+1 from ${from});
--

EOF

echo "*******************" >> /dev/stderr
echo "" >> /dev/stderr
echo "" >> /dev/stderr
echo "Now manually run something similar to:" >> /dev/stderr
echo "" >> /dev/stderr
echo "	alter sequence <seq name> restart with (select max(id)+1 from ${from});" >> /dev/stderr
echo "" >> /dev/stderr
echo "" >> /dev/stderr
echo "*******************" >> /dev/stderr
