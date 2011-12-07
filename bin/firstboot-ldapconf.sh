#!/bin/bash

uri=$1
basedn=$2
binddn=$3
bindpw=$4

ldapconf=/etc/ldap.conf
bakconf=/etc/ldap.conf.gecos-firststart.bak
tmpconf=/tmp/ldap.conf.tmp
debconffile=/usr/share/firstboot/debconf.ldap
pamdconfig=/usr/share/firstboot/pamd-ldap
bakdir=/usr/share/firstboot/pamd-ldap.bak
pamd=/etc/pam.d/
nsswitch=/etc/nsswitch.conf



# Need root user
need_root() {
    if [ 0 != `id -u` ]; then
        echo "You must be root to run this script."
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {

    if [ ! -f $ldapconf ]; then
        echo "File not found: "$ldapconf
        exit 1
    fi

    if [ "" == "$uri" ]; then
        echo "URI couldn't be empty."
        exit 1
    fi

    if [ "" == "$basedn" ]; then
        echo "Base DN couldn't be empty."
        exit 1
    fi

    if [ "" == "$binddn" ]; then
        echo "Bind DN couldn't be empty."
        exit 1
    fi

}

# Check if LDAP is currently configured
check_configured() {
    if [ -f $bakconf ]; then
        echo 1
    else
        echo 0
    fi
    exit 0
}

# Restore the configuration
restore() {

    if [ ! -f $bakconf ]; then
        echo "File not found: "$bakconf
        exit 1
    fi

    mv $ldapconf $ldapconf".bak"
    mv $bakconf $ldapconf
    mv $bakdir/nsswitch.conf $nsswitch
    mv $bakdir/* $pamd/
    rm -rf $bakdir
    pam-auth-update --force --package
    exit 0
}

# Make a backup
backup() {
    if [ ! -f $bakconf ]; then
        cp $ldapconf $bakconf
    fi
    if [ ! -d $bakdir ]; then
        mkdir $bakdir
        cp -r $pamd/* $bakdir
        cp $nsswitch $bakdir
    else
        cp -r $pamd/* $bakdir
        cp $nsswitch $bakdir
    fi

}


# Update the configuration
update_conf() {

    check_prerequisites
    backup

    cp -r $pamdconfig/ldap.conf $ldapconf
    sed -e s@"^uri .*"@"uri $uri"@ \
        -e s/"^base .*"/"base $basedn"/g \
        -e s/"^binddn .*"/"binddn $binddn"/g \
        -e s/"^bindpw .*"/"bindpw $bindpw"/g \
        $ldapconf > $tmpconf

    # It's posible that some options are commented,
    # be sure to decomment them.
    sed -e s/"^#base .*"/"base $basedn"/g \
        -e s/"^#binddn .*"/"binddn $binddn"/g \
        -e s/"^#bindpw .*"/"bindpw $bindpw"/g \
        $tmpconf > $tmpconf".2"

    mv $tmpconf".2" $tmpconf

    check_configuration

    mv $tmpconf $ldapconf
    cp -r $pamdconfig/pam.d/* $pamd
    cp -r $pamdconfig/nsswitch.conf $nsswitch
    debconf-set-selections $debconffile 2>&1 |grep -qi "can't open"
    retval=$(echo $?)
    if [ $retval -eq 0 ]; then
        echo "Fail connecting to LDAP"
        restore
        exit 1
    fi
    pam-auth-update --package --force
    retval=$(echo $?)
    if [ $retval -ne 0 ]; then
        echo "Fail connecting to LDAP"
        restore
        exit 1
    fi
    echo "The configuration was updated successfully."

    exit 0
}

# Check the changes are valid
check_configuration() {
    r_uri=`egrep "^uri $uri" $tmpconf`
    r_base=`egrep "^base $basedn" $tmpconf`
    r_bind=`egrep "^binddn $binddn" $tmpconf`
    r_pass=`egrep "^bindpw $bindpw" $tmpconf`

    if [ "" == "$r_uri" -o "" == "$r_base" -o "" == "$r_bind" -o "" == "$r_pass" ]; then
        echo "The configuration couldn't be updated correctly."
        exit 1
    fi
}

# Restore or update the LDAP configuration
case $uri in
    --restore | -r)
        need_root
        restore
        ;;
    --query | -q)
        check_configured
        ;;
    *)
        need_root
        update_conf
        ;;
esac
