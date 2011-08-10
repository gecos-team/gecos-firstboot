#!/bin/bash

uri=$1
port=$2
base=$3

ldapconf=/etc/ldap.conf
tmpconf=/etc/ldap.conf.tmp
bakconf=/etc/ldap.conf.bak

# Check prerequisites
if [ 0 != `id -u` ]; then
    echo "You must be root"
    exit 1
fi

if [ ! -f $ldapconf ]; then
    echo "File not found: "$ldapconf
    exit 1
fi

if [ "" == "$uri" ]; then
    echo "URI is empty"
    exit 1
fi

if [ "" == "$port" ]; then
    echo "PORT is empty"
    exit 1
fi

if [ "" == "$base" ]; then
    echo "BASE is empty"
    exit 1
fi


# Make a backup
cp $ldapconf $bakconf


# Replace the configuration parameters
sed -e s@"^uri .*"@"uri $uri"@g \
    -e s/"^port .*"/"port $port"/g \
    -e s/"^base .*"/"base $base"/g \
    $ldapconf > $tmpconf

ret=`egrep "^port [0-9]+" $tmpconf`

if [ "" == "$ret" ]; then
    sed -e s/"#port .*"/"port $port"/g $tmpconf > $tmpconf"_2"
    mv $tmpconf"_2" $tmpconf
fi


# Check the changes are valid
r_uri=`egrep "^uri $uri" $tmpconf`
r_port=`egrep "^port $port" $tmpconf`
r_base=`egrep "^base $base" $tmpconf`

if [ "" == $r_uri -o "" == $r_port -o "" == $r_base ]; then
    echo "The configuration could not be changed"
    exit 1
fi

mv $tmpconf $ldapconf
echo "The configuration was updated successfully"
#cat $ldapconf

exit 0

