#!/bin/bash

uri=$1
port=$2
base=$3
tplfile=./ldap.conf.in
tmpfile=./ldap.conf.tmp
file=./ldap.conf


if [ ! -f $tplfile ]; then
    echo "File not found: "$tplfile
    exit 1
fi

if [ "" == "$uri" ]; then
    echo "URI non valid"
    exit 1
fi

if [ "" == "$port" ]; then
    echo "PORT non valid"
    exit 1
fi

if [ "" == "$base" ]; then
    echo "BASE non valid"
    exit 1
fi

sed -e s@"^uri .*"@"uri $uri"@g \
    -e s/"^port .*"/"port $port"/g \
    -e s/"^base .*"/"base $base"/g \
    $tplfile > $tmpfile

ret=`egrep "^port [0-9]+" $tmpfile`

if [ "" == "$ret" ]; then
    sed -e s/"#port .*"/"port $port"/g $tmpfile > $tmpfile"_2"
    mv $tmpfile"_2" $tmpfile
fi

mv $tmpfile $file
cat $file

exit 0
