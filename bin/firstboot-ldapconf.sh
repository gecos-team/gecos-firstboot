#!/bin/bash

uri=$1
basedn=$2
binddn=$3
bindpw=$4

ldapconf=/etc/ldap.conf
bakconf=/etc/ldap.conf.gecos-firststart.bak
tmpconf=/tmp/ldap.conf.tmp


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

    exit 0
}

# Make a backup
backup() {
    if [ ! -f $bakconf ]; then
        cp $ldapconf $bakconf
    fi
}


# Update the configuration
update_conf() {

    check_prerequisites
    backup

    sed -e s@"^uri .*"@"uri $uri"@g \
        -e s/"^base .*"/"base $basedn"/g \
        -e s/"^binddn .*"/"binddn $binddn"/g \
        -e s/"^bindpw .*"/"bindpw $bindpw"/g \
        $ldapconf > $tmpconf

    # It's posible that some options are commented,
    # be sure to decomment them.
    sed -e s@"^#uri .*"@"uri $uri"@g \
        -e s/"^#base .*"/"base $basedn"/g \
        -e s/"^#binddn .*"/"binddn $binddn"/g \
        -e s/"^#bindpw .*"/"bindpw $bindpw"/g \
        $tmpconf > $tmpconf".2"

    mv $tmpconf".2" $tmpconf

    check_configuration

    mv $tmpconf $ldapconf
    echo "The configuration was updated successfully."

    exit 0
}

# Check the changes are valid
check_configuration() {
    r_uri=`egrep "^uri $uri" $tmpconf`
    r_base=`egrep "^base $basedn" $tmpconf`
    r_bind=`egrep "^binddn $binddn" $tmpconf`
    r_pass=`egrep "^bindpw $bindpw" $tmpconf`

    if [ "" == $r_uri -o "" == $r_base -o "" == $r_bind -o "" == $r_pass ]; then
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
